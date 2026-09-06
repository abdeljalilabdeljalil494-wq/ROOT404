"""AI Mentor — guide socratique (moteur heuristique v1).

Contrat (README) : l'assistant ne donne **jamais** la solution finale — il
pose des questions, explique des concepts et suggère des ressources.

Cette première version est un moteur de règles déterministe qui exploite le
contexte réel de l'étudiant (dernière soumission, tests échoués, projet).
L'entrée `ask()` est le point d'attache prévu pour un vrai LLM plus tard :
l'API et les payloads ne changeraient pas.

Niveaux d'assistance (comme l'UI) :
    1 → hint court (texte seul)
    2 → questions socratiques (+ liste)
    3 → explication du concept (+ footer)
    4 → + suggestions de ressources (chips)
    5 → tout, avec un maximum d'explicite
"""

import re
from datetime import timedelta

from sqlalchemy import select

from .. import models

OPENING = (
    "Salut {name} 👋 J'ai analysé ta dernière soumission{ctx}. "
    "Je ne vais pas te donner la solution — mais je peux t'aider à la trouver. "
    "Par quoi veux-tu commencer ?"
)
OPENING_CHIPS = ["Comprendre mon erreur", "Expliquer un concept", "Me donner un indice"]

# Each rule: (regex, {text, list?, footer?, chips?, concept?})
# La règle de refus passe AVANT les règles de sujet : « écris-moi le code »
# ne doit pas être traité comme une question technique.
RULES: list[tuple[str, dict]] = [
    (
        r"(donne|donnes)\s*[- ]\s*moi\s*(le|la|l'|un|une)\s*(code|solution|implémentation|réponse)|écri[stz]\s*[- ]\s*moi\s*(le|ce|la|un)\s*(code|programme|fonction|projet)|code pour moi|fais[- ]?le pour moi|fais[- ]?moi\s*(ce|le)\s*code|solution finale|copie le code",
        {
            "text": "Je ne vais pas écrire ce code à ta place — c'est ton projet, et c'est ce que tu en retiens qui compte. Mais on peut y arriver ensemble :",
            "list": [
                "Où en es-tu exactement — quelle ligne, quelle fonction ?",
                "Qu'as-tu déjà essayé, et qu'a donné chaque essai ?",
                "Quel concept penses-tu être bloquant ?",
            ],
            "footer": "Reformule le problème avec tes propres mots — souvent la réponse arrive pendant la reformulation.",
        },
    ),
    (
        r"segfault|segmentation|crash|faute de seg|il plante|ça plante|segmentation fault",
        {
            "text": "Un segfault, c'est toujours un accès à une mémoire que tu n'as pas le droit de toucher. Avant de chercher L'endroit, cherche l'objet : qui alloue, qui libère, et qui utilise après ?",
            "list": [
                "Réduis le cas au minimum reproductible : 3 lignes qui plantent, sans le reste.",
                "Quel pointeur est en cause au moment du crash — d'où vient-il ?",
                "Que verrais-tu si tu affichais sa valeur juste avant l'accès ?",
            ],
            "footer": "Un segfault en shell vient souvent d'un descripteur fermé deux fois ou d'un tableau de pipes mal indexé. `gdb ./app` + `bt` te donne la ligne — mais essaie de la trouver d'abord avec tes raisons.",
            "chips": ["man 2 pipe", "gdb : bt et frame", "Micro-exercice : cat | cat | ls"],
        },
    ),
    (
        r"pipe|fork|exec|descripteur|dup2|close|process|shell",
        {
            "text": "Le shell, c'est de la gestion de processus et de descripteurs. Avant le code, dessine-moi la topologie du cas qui te bloque :",
            "list": [
                "Pour `cmd1 | cmd2 | cmd3`, combien de pipes crées-tu ?",
                "Dans le parent, qu'advient-il des extrémités de pipe après chaque fork ?",
                "Chaque enfant ferme-t-il bien les extrémités qu'il n'utilise pas ? Si non, qui bloque ?",
            ],
            "footer": "Un segfault ou un blocage ici vient souvent d'un `close()` manquant dans le parent, ou d'un index de pipe qui déborde (n-1 pipes pour n commandes).",
            "chips": ["man 2 fork", "man 2 dup2", "Schéma : 3 cmd = 2 pipes"],
        },
    ),
    (
        r"fuite|leak|valgrind|malloc|free|mémoire|memory|dédoublement|double free|alloue",
        {
            "text": "Le concept sous-jacent s'appelle l'ownership de la mémoire : une allocation, UN seul responsable pour la libérer. Réponds-moi précisément :",
            "list": [
                "Qui alloue ce buffer — et qui a le droit de le libérer ?",
                "À quel endroit exact du code l'ownership change-t-elle ?",
                "Si tu libérais une ligne plus tôt, que casserait-ce ? Une ligne plus tard ?",
            ],
            "footer": "Une fuite classique : le reste d'une ligne non consommée qui est alloué puis jeté sans `free`. `valgrind --leak-check=full` te donne la LIGNE d'allocation, pas le lieu du bug — relie les deux.",
            "chips": ["man 3 malloc", "valgrind --leak-check=full", "Règle : 1 malloc = 1 free"],
        },
    ),
    (
        r"norme|norminette|style|25 lignes|tabulation",
        {
            "text": "La norme n'est pas du décor : elle force une découpe qui rend le code vérifiable. Dis-moi ce que la norminette te signale, et réponds :",
            "list": [
                "Quelle fonction dépasse 25 lignes — que fait-elle EN TROP ?",
                "Peux-tu la décrire en une phrase ? Si non, elle fait plusieurs choses.",
                "Quel serait le nom de chaque sous-tâche si tu en faisais des fonctions ?",
            ],
            "footer": "Concept suggéré : Separation of Concerns — une fonction = une responsabilité. Si le nom contient « et », c'est déjà deux fonctions.",
            "chips": ["Norminette 42", "Refactor : extract function", "Naming : des noms qui se lisent"],
        },
    ),
    (
        r"compil|undefined reference|implicit declaration|linker|erreur de (compilation|liaison)|gcc",
        {
            "text": "Un message de compilation est une phrase entière — lis-le du bas vers le haut : la cause est dans la première ligne, pas dans le bruit. Qu'est-ce qu'il dit exactement ?",
            "list": [
                "« implicit declaration » : quelle fonction est appelée sans prototype visible — où est son header ?",
                "« undefined reference » : la fonction est déclarée mais jamais compilée — quel .c manque ? (ou est exclu de la compilation ?)",
                "Avec `-Werror`, est-ce un warning qui bloque ? Lequel, et pourquoi est-il là ?",
            ],
            "footer": "Cherche toujours le PREMIER message d'erreur : les suivants sont souvent des conséquences.",
            "chips": ["gcc -Wall -Wextra -Werror", "make -n (voir la commande)", "Les headers avant l'implémentation"],
        },
    ),
    (
        r"pointeur|pointer|référen|\*|déréféren",
        {
            "text": "Un pointeur est une adresse — c'est tout. La question n'est pas « comment ça marche » mais « QUE contient cette adresse, et qui l'a mise là ? »",
            "list": [
                "Si tu affiches l'ADRESSE, quelle valeur obtiens-tu ? Et si tu affiches ce qu'elle CONTIENT ?",
                "Entre l'écriture de la valeur et sa lecture, qui aurait pu changer l'adresse (ou la libérer) ?",
                "Peut-elle être NULL à cet endroit ? Que se passe-t-il si oui ?",
            ],
            "footer": "Dessin utile : une case mémoire contenant une autre case. Tout bug de pointeur se raconte avec deux cases.",
            "chips": ["& et * en C", "pointeur NULL", "tableau = pointeur"],
        },
    ),
    (
        r"thread|pthread|philosoph|mutex|synchron|race|concurrent",
        {
            "text": "Avec des threads, le bug est une course : deux threads sur la même donnée sans ordre garanti. Identifie-moi la ressource partagée :",
            "list": [
                "Quelle variable est lue/écrite par plusieurs threads ?",
                "Quelle section doit être critique — et quelle mutex la protège (ou devrait le) ?",
                "Peux-tu construire l'ordre exact des événements qui produit le plantage ?",
            ],
            "footer": "Un deadlock arrive quand deux threads s'attendent mutuellement — dessine qui attend qui. Et `usleep` dans une boucle, c'est un anti-pattern de synchronisation.",
            "chips": ["man 3 pthread_mutex", "sections critiques", "deadlock : cycle d'attente"],
        },
    ),
    (
        r"printf|%d|%s|%c|%p|format|conversion|bougie",
        {
            "text": "Un printf est un contrat : le format dicte comment lire les arguments. Relis-moi le contrat, un à un :",
            "list": [
                "Pour chaque `%X`, quel argument exact est passé — et de quel type ?",
                "`%s` attend un `char *` : es-tu sûr que c'est ce que tu passes ?",
                "Qu'affiche `%%` ? Et si le format contient des `%` non échappés ?",
            ],
            "footer": "Règle d'or : le nombre et le type des arguments doivent correspondre au format, sinon c'est undefined behavior — parfois spectaculaire.",
            "chips": ["man 3 printf", "format specifiers", "undefined behavior"],
        },
    ),
    (
        r"eof|fin de fichier|fichier|getline|readline|buffer|saisie|input|entrée|fin de ligne|\\n",
        {
            "text": "Gérer un flux, c'est traiter 3 états : données, fin de flux, erreur. Lequel des trois est mal géré chez toi ?",
            "list": [
                "Que doit renvoyer ta fonction APRÈS la dernière ligne — et comment le détectes-tu ?",
                "Le `\\n` est-il consommé ou laissé dans le buffer ? Qui en hérite ?",
                "Et si le fichier ne se termine pas par `\\n` ? Que renvoie ta boucle ?",
            ],
            "footer": "EOF n'est pas « le fichier est vide » : c'est « plus rien à lire » — et il peut arriver au milieu d'une ligne.",
            "chips": ["man 2 read", "fin de ligne vs EOF", "buffer à taille fixe"],
        },
    ),
    (
        r"complexité|complexity|optimis|performance|lent|lente|algo|tri|sort|O\(|dichotom",
        {
            "text": "La complexité ne se devine pas, elle se compte : combien d'opérations pour une entrée de taille n ? Décomposons :",
            "list": [
                "Quelle est ta boucle la plus interne — et combien de fois s'exécute-t-elle par élément ?",
                "Peux-tu préparer (trier, indexer, pré-calculer) pour éviter de refaire le travail ?",
                "Quelle est la meilleure complexité théorique pour ce problème — et pourquoi ?",
            ],
            "footer": "Réflexe : si tu vois deux boucles imbriquées sur la même donnée, demande-toi si un tri + deux pointeurs (O(n log n)) ne remplacerait pas le O(n²).",
            "chips": ["notation O(·)", "tri fusion / quicksort", "pré-calcul vs recalcul"],
        },
    ),
    (
        r"get_next_line|gnl",
        {
            "text": "get_next_line est un problème de buffer entre deux appels. La question clé : que devient le RESTE de la ligne non lu ?",
            "list": [
                "Si read() renvoie « bonj\\nmonde\\n », que retourne ta première appel ? Et le buffer contient quoi après ?",
                "Où stockes-tu le reste — et qui le libère ?",
                "Combien d'appels read() pour une ligne de 10 000 caractères ? Ton code le gère-t-il ?",
            ],
            "footer": "Le piège classique : allouer le buffer global une fois et le laisser pointer vers de la mémoire déjà libérée (use-after-free) — ou ne jamais le libérer (fuite).",
            "chips": ["man 2 read", "buffer persistant", "1 malloc / 1 free"],
        },
    ),
]
_FALLBACK = {
    "text": "Bonne question. Reformule-moi d'abord le problème avec tes propres mots : qu'attends-tu exactement en sortie, et qu'obtiens-tu à la place ?",
    "list": [
        "Quel est le comportement ATTENDU ?",
        "Quel est le comportement RÉEL ?",
        "À partir de quelle étape ça diverge ?",
    ],
}

_RULE_COMPILED = [(re.compile(p, re.IGNORECASE), r) for p, r in RULES]


def latest_context(db, user: models.User) -> dict:
    """Projet + tests échoués de la dernière soumission (contexte du mentor)."""
    sub = db.execute(
        select(models.Submission)
        .where(models.Submission.user_id == user.id)
        .order_by(models.Submission.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if sub is None:
        return {"project": None, "failed": [], "score": None}
    project = db.get(models.Project, sub.project_id)
    failed = [t.get("name", "") for t in (sub.tests or []) if t.get("status") == "fail"]
    return {
        "project": project.slug if project else None,
        "failed": failed,
        "score": sub.score,
    }


def build_reply(rule: dict, ctx: dict, level: int) -> dict:
    """Level 1: text · 2: +list · 3: +footer · 4/5: +chips (5 = tout)."""
    out: dict = {"role": "ai", "text": rule["text"]}
    if level >= 2 and rule.get("list"):
        out["list"] = rule["list"]
    if level >= 3:
        parts = []
        if rule.get("footer"):
            parts.append(rule["footer"])
        if ctx.get("failed"):
            proj = f" ({ctx['project']})" if ctx.get("project") else ""
            parts.append(
                f"Dernier échec Moulinette{proj} : {ctx['failed'][0]} — "
                "c'est souvent le meilleur point de départ."
            )
        if parts:
            out["footer"] = " · ".join(parts)
    if level >= 4 and rule.get("chips"):
        out["chips"] = rule["chips"]
    return out


def socratic_reply(message: str, ctx: dict, level: int = 2) -> dict:
    level = min(max(int(level or 2), 1), 5)
    for rx, rule in _RULE_COMPILED:
        if rx.search(message):
            return build_reply(rule, ctx, level)
    return build_reply(_FALLBACK, ctx, level)


def opening_message(user: models.User, ctx: dict) -> dict:
    ctx_txt = f" de `{ctx['project']}`" if ctx.get("project") else ""
    name = (user.display_name or user.username or "").split()[0]
    return {
        "role": "ai",
        "text": OPENING.format(name=name, ctx=ctx_txt),
        "chips": OPENING_CHIPS,
    }


def history_payload(db, user: models.User) -> dict:
    rows = db.execute(
        select(models.AiMessage)
        .where(models.AiMessage.user_id == user.id)
        .order_by(models.AiMessage.created_at.asc())
        .limit(50)
    ).scalars().all()
    messages = []
    for r in rows:
        m = {"role": r.role, "text": r.text, "project": r.project}
        extra = r.extra or {}
        for k in ("list", "footer", "chips"):
            if extra.get(k):
                m[k] = extra[k]
        messages.append(m)
    if not messages:
        messages = [opening_message(user, latest_context(db, user))]

    since = models.now() - timedelta(days=30)
    q = db.execute(
        select(models.AiMessage)
        .where(
            models.AiMessage.user_id == user.id,
            models.AiMessage.role == "user",
            models.AiMessage.created_at >= since,
        )
    ).scalars().all()
    queries = len(q)
    dep = "Low" if queries < 20 else "Medium" if queries < 50 else "High"
    return {
        "messages": messages,
        "context": {"project": latest_context(db, user)["project"]},
        "stats": {"queries": queries, "level": dep},
    }


def ask_payload(db, user: models.User, message: str, level: int = 2) -> dict:
    ctx = latest_context(db, user)
    reply = socratic_reply(message, ctx, level)
    db.add(models.AiMessage(
        user_id=user.id, role="user", text=message, project=ctx["project"],
    ))
    db.add(models.AiMessage(
        user_id=user.id, role="ai", text=reply["text"],
        extra={k: v for k, v in reply.items() if k in ("list", "footer", "chips")},
        project=ctx["project"],
    ))
    db.commit()
    return reply


# ---------------------------------------------------------------- review --
_FN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ \t\*]*\([^;{]*\)\s*$")


def _code_stats(files: list) -> tuple[int, int, str]:
    """(max_line_len, longest_function_lines, longest_function_name)."""
    max_line, longest, longest_name = 0, 0, ""
    for f in files:
        lines = (f.get("content") or "").splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            max_line = max(max_line, len(line))
            if line.strip() and _FN_RE.match(line):
                j = i
                while j < len(lines) and not lines[j].lstrip().startswith("}"):
                    j += 1
                if j - i + 1 > longest:
                    longest, longest_name = j - i + 1, line.strip().split("(")[0].strip()
                i = j
            i += 1
    return max_line, longest, longest_name


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def review_payload(db, user: models.User) -> dict:
    """AI Code Review — metrics + notes sur la dernière soumission CONCLUE
    (pending/running sont ignorés : on n'analyse pas un code en cours d'examen)."""
    subs = db.execute(
        select(models.Submission)
        .where(models.Submission.user_id == user.id)
        .order_by(models.Submission.created_at.desc())
        .limit(5)
    ).scalars().all()
    sub = next((s for s in subs if s.status in ("passed", "failed")), None)
    if sub is None or not sub.tests:
        pending = subs and subs[0].status in ("pending", "running")
        return {
            "metrics": None,
            "notes": [
                {
                    "tone": "info",
                    "text": (
                        "Ta dernière soumission est en cours d'analyse par la Moulinette — "
                        "reviens dans un instant."
                        if pending
                        else "Aucune soumission analysable — passe d'abord la Moulinette sur un projet."
                    ),
                }
            ],
        }

    tests = sub.tests or []
    by = lambda key: next((t for t in tests if key in t.get("name", "")), None)
    comp_t = by("Compilation")
    norm_t = by("Norme")
    leak_t = by("Fuites")
    run_t = [t for t in tests if t is not comp_t and t is not norm_t and t is not leak_t]

    run_ok = sum(1 for t in run_t if t.get("status") in ("pass", "skip"))
    correctness = _clamp(int(100 * run_ok / len(run_t)) if run_t else (sub.score or 0), 0, 100)
    memory = {"pass": 100, "skip": 88, "fail": 40}.get((leak_t or {}).get("status"), 88)
    quality = {"pass": 90, "warn": 60, "fail": 40}.get((norm_t or {}).get("status"), 75)

    max_line, long_fn, long_name = _code_stats(sub.files or [])
    long_name = " ".join(long_name.split())  # tabulation C → espaces
    complexity = _clamp(95 - max(0, long_fn - 25) - max(0, max_line - 100) // 5, 55, 95)
    readability = _clamp(98 - (max(0, max_line - 80) // 2), 70, 98)

    metrics = [
        {"label": "Correctness", "value": correctness},
        {"label": "Memory Safety", "value": memory},
        {"label": "Code Quality", "value": quality},
        {"label": "Complexity", "value": complexity},
        {"label": "Readability", "value": readability},
    ]

    notes = []
    for t in tests:
        if t.get("status") == "fail":
            notes.append({"tone": "warn", "text": f"Test échoué : {t['name']} — {t.get('detail', '')}"})
        if len(notes) >= 3:
            break
    if long_fn > 25:
        notes.append({
            "tone": "info",
            "text": f"La fonction « {long_name or '…'} » fait ~{long_fn} lignes — au-dessus des 25 de la norme. Concept suggéré : Separation of Concerns.",
        })
    if (norm_t or {}).get("status") != "pass":
        notes.append({
            "tone": "info",
            "text": "La norme n'est pas fully verte : commence par la plus longue fonction, le reste suit.",
        })
    if not notes:
        notes.append({
            "tone": "info",
            "text": "Aucun point bloquant détecté sur cette soumission. Garde ce niveau de rigueur pour la peer review.",
        })
    return {"metrics": metrics, "notes": notes[:4]}
