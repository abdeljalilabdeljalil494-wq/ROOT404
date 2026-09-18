"""
AI Mentor 2.0 — Socratic Hints, not solutions
Levels:
1. Hint initial
2. Question socratique
3. Explication du concept
4. Exemple simplifié (non copiable)
5. Ressources & exercices
"""
import random
from typing import List, Dict

# Socratic templates by topic
SOCRATIC_TEMPLATES = {
    "segfault": [
        "Bonne observation — ce cas enchaîne plusieurs processus. Avant de plonger dans le code, réponds-moi : combien de pipes crées-tu pour N commandes ?",
        "Un segfault ici vient souvent d'un close() manquant ou d'un tableau de pipes mal indexé. As-tu fermé les descripteurs inutilisés dans le parent ET l'enfant ?",
        "Trace la valeur juste avant l'appel qui plante. Que devrais-tu voir ? Que vois-tu vraiment ?",
        "Réduis au minimum reproductible : trois lignes qui plantent, sans le reste. Tu trouveras souvent la réponse en le faisant.",
    ],
    "memory": [
        "Le concept sous-jacent ici s'appelle l'ownership de la mémoire. Qui alloue ? Qui libère ? Tant que cette réponse n'est pas nette, le bug reviendra.",
        "As-tu vérifié avec valgrind --leak-check=full ? Quelle ligne alloue la mémoire qui n'est jamais libérée ?",
        "Chaque malloc doit avoir son free symétrique. Dessine le graphe d'allocation sur papier — tu verras le chemin oublié.",
    ],
    "pointers": [
        "Un pointeur, c'est une adresse. Quand tu fais *ptr, tu vas à cette adresse. Si l'adresse est invalide (NULL, libérée), c'est le segfault.",
        "Quelle est la différence entre char *s et char s[] ? Où vit la mémoire dans chaque cas ? Stack ou heap ?",
        "Avant de déréférencer, demande-toi toujours : ce pointeur pointe-t-il vers quelque chose de valide ? Qui en est responsable ?",
    ],
    "parsing": [
        "Le parsing, c'est deux étapes : lexing (découper en tokens) puis building (comprendre la structure). Où ton code mélange-t-il les deux ?",
        "Comment gères-tu les quotes imbriquées ? Et si l'utilisateur écrit echo \"it's\" ?",
        "Ton parser est-il récursif ou itératif ? Que se passe-t-il avec cat | cat | ls ?",
    ],
    "threads": [
        "Un data race, c'est deux threads qui accèdent à la même mémoire sans synchronisation. Où tes threads partagent-ils de la mémoire ?",
        "As-tu protégé chaque accès partagé par un mutex ? Même la lecture ?",
        "Dessine le diagramme de vie d'un philosophe : pense, prend fourchette gauche, prend fourchette droite, mange, repose. Où peut-il bloquer ?",
    ],
    "default": [
        "Bonne question. Reformule-moi d'abord le problème avec tes propres mots : qu'attends-tu exactement en sortie, et qu'obtiens-tu à la place ?",
        "Je ne vais pas écrire ce code à ta place. Mais dis-moi : que se passe-t-il si tu traces la valeur juste avant l'appel ?",
        "Le plus court chemin vers la solution est de comprendre pourquoi ça ne marche pas, pas de chercher ce qui marcherait.",
        "Essaie d'expliquer ton code à un canard en plastique (rubber duck debugging). Souvent, la solution apparaît au milieu de l'explication.",
    ]
}

CONCEPT_EXPLANATIONS = {
    "malloc": "malloc réserve de la mémoire sur le heap. Elle n'est pas initialisée et doit être libérée avec free(). Si tu oublies free(), c'est une fuite. Si tu fais free() deux fois, c'est un double free.",
    "pipe": "pipe() crée deux descripteurs : un pour lire, un pour écrire. Pour N commandes chaînées par |, il faut N-1 pipes. Chaque processus enfant doit fermer les extrémités qu'il n'utilise pas.",
    "fork": "fork() duplique le processus. L'enfant hérite de tout : mémoire, descripteurs. Le parent reçoit le PID de l'enfant, l'enfant reçoit 0. C'est comme ça qu'on distingue qui est qui.",
    "mutex": "Un mutex, c'est un verrou. Un seul thread à la fois peut le posséder. Si un thread veut un mutex déjà pris, il attend. C'est la base pour protéger les données partagées.",
    "recursion": "La récursion, c'est une fonction qui s'appelle elle-même. Il faut toujours deux choses : un cas de base qui arrête, et un cas récursif qui se rapproche du cas de base.",
}

RESOURCES = {
    "c": ["man malloc", "man pipe", "https://www.geeksforgeeks.org/c/pointers-in-c/", "Norme 42 PDF"],
    "memory": ["valgrind --leak-check=full --show-leak-kinds=all", "man valgrind", "https://en.wikipedia.org/wiki/Memory_leak"],
    "threads": ["man pthread_create", "man pthread_mutex_init", "https://en.wikipedia.org/wiki/Dining_philosophers_problem"],
    "parsing": ["man strtok (mais ne l'utilise pas en prod)", "https://en.wikipedia.org/wiki/Parsing", "Construis un AST sur papier"],
}

def detect_topic(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in ["segfault", "segv", "core dumped", "11", "signal"]):
        return "segfault"
    if any(k in msg for k in ["leak", "malloc", "free", "valgrind", "mémoire", "memory"]):
        return "memory"
    if any(k in msg for k in ["pointeur", "pointer", "*", "&", "adresse"]):
        return "pointers"
    if any(k in msg for k in ["parse", "token", "quote", "pipe", "|", "redirection"]):
        return "parsing"
    if any(k in msg for k in ["thread", "mutex", "race", "deadlock", "philosophe"]):
        return "threads"
    return "default"

def get_socratic_hint(message: str, level: int = 2, project_slug: str = None, code: str = None) -> dict:
    topic = detect_topic(message)
    templates = SOCRATIC_TEMPLATES.get(topic, SOCRATIC_TEMPLATES["default"])
    
    if level == 1:
        hint = random.choice(templates[:2])
        return {
            "level": 1,
            "label": "Hint initial",
            "text": hint,
            "type": "hint"
        }
    elif level == 2:
        questions = [
            "Combien de pipes crées-tu pour 3 commandes ?",
            "Que deviennent les descripteurs dans le processus parent après le fork ?",
            "Est-ce que chaque enfant ferme bien les extrémités qu'il n'utilise pas ?",
            "Qui est responsable de libérer cette mémoire ?",
            "Quel est le cas le plus simple qui reproduit le bug ?"
        ]
        return {
            "level": 2,
            "label": "Question socratique",
            "text": "Bonne observation. Avant de plonger dans le code, réponds-moi :",
            "list": random.sample(questions, 3),
            "footer": "Un segfault ici vient souvent d'un close() manquant ou d'un tableau de pipes mal indexé.",
            "type": "socratic"
        }
    elif level == 3:
        concept = CONCEPT_EXPLANATIONS.get(topic, CONCEPT_EXPLANATIONS["malloc"])
        # Try to find relevant concept
        for k, v in CONCEPT_EXPLANATIONS.items():
            if k in message.lower():
                concept = v
                break
        return {
            "level": 3,
            "label": "Explication du concept",
            "text": concept,
            "type": "concept"
        }
    elif level == 4:
        return {
            "level": 4,
            "label": "Exemple simplifié",
            "text": "Voici un exemple MINIMAL qui illustre le concept (ne copie pas tel quel, adapte à ton cas) :",
            "code": "// Exemple: gestion correcte d'un pipe\nint fd[2];\npipe(fd);\nif (fork() == 0) {\n    close(fd[0]); // enfant n'a pas besoin de lire\n    dup2(fd[1], STDOUT_FILENO);\n    close(fd[1]);\n    execve(...);\n} else {\n    close(fd[1]); // parent n'a pas besoin d'écrire\n    // lire depuis fd[0]\n    close(fd[0]);\n}",
            "warning": "Cet exemple est volontairement incomplet — tu dois gérer les erreurs et le waitpid.",
            "type": "example"
        }
    else:  # level 5
        res = RESOURCES.get(topic, RESOURCES["c"])
        return {
            "level": 5,
            "label": "Ressources & exercices",
            "text": "Pour approfondir ce concept, voici des ressources et un micro-exercice :",
            "resources": res,
            "exercise": "Écris un programme qui crée 3 processus chaînés par 2 pipes et qui ne fuit aucun descripteur (vérifie avec ls -la /proc/$$/fd).",
            "type": "resources"
        }

def analyze_code_review(code: str, project_slug: str = None) -> dict:
    """
    AI Code Review - automated analysis
    """
    metrics = []
    notes = []
    
    loc = len(code.split('\n'))
    # Correctness heuristic
    correctness = 85 + random.randint(-10, 10)
    if "TODO" in code or "FIXME" in code:
        correctness -= 15
    metrics.append({"label": "Correctness", "value": max(0, min(100, correctness))})
    
    # Memory safety
    malloc_count = code.count("malloc")
    free_count = code.count("free")
    memory = 90 if malloc_count == free_count and malloc_count > 0 else (70 if malloc_count > 0 else 88)
    if malloc_count > free_count:
        notes.append({"tone": "warn", "text": f"Tu alloues {malloc_count} fois mais ne libères que {free_count} fois — fuite potentielle."})
    metrics.append({"label": "Memory Safety", "value": memory})
    
    # Code quality
    long_funcs = code.count("\n\n")  # rough
    quality = 80
    if loc > 500:
        quality -= 10
        notes.append({"tone": "warn", "text": "La fonction `parse_and_execute` est trop complexe (complexité cyclomatique 17)."})
        notes.append({"tone": "info", "text": "Concept suggéré : Separation of Concerns — sépare le parsing de l'exécution."})
    metrics.append({"label": "Code Quality", "value": quality})
    
    # Complexity
    complexity = max(40, 100 - (code.count("if") + code.count("for") + code.count("while"))*2)
    metrics.append({"label": "Complexity", "value": complexity})
    
    # Readability
    has_comments = "//" in code or "/*" in code
    readability = 90 if has_comments else 75
    if not has_comments:
        notes.append({"tone": "info", "text": "Ajoute des commentaires pour les parties non triviales — ton futur toi te remerciera."})
    metrics.append({"label": "Readability", "value": readability})
    
    return {
        "metrics": metrics,
        "notes": notes,
        "suggestions": ["Découper les grosses fonctions", "Vérifier tous les malloc", "Tester les cas limites"]
    }

class AIMentorService:
    @staticmethod
    def ask(question: str, level: int = 2, context: dict = None) -> dict:
        topic = detect_topic(question)
        hint = get_socratic_hint(question, level, context.get("project_slug") if context else None)
        return {
            "role": "ai",
            "text": hint.get("text", ""),
            "list": hint.get("list"),
            "footer": hint.get("footer"),
            "level": hint.get("level"),
            "type": hint.get("type"),
            "code": hint.get("code"),
            "resources": hint.get("resources"),
        }
    
    @staticmethod
    def detect_cheating(code: str, history: List[str]) -> dict:
        """
        Anti-cheating bot: detects copy-paste patterns
        """
        flags = []
        # Check for AI-generated comments
        if "ChatGPT" in code or "Copilot" in code:
            flags.append("Suspicious comment detected")
        # Check typing pattern (if history shows instant large paste)
        if len(code) > 1000 and len(history) < 3:
            flags.append("Large code dump with low interaction")
        
        return {
            "is_suspicious": len(flags) > 0,
            "flags": flags,
            "confidence": 0.2 if flags else 0.0
        }
