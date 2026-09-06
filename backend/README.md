# ROOT 404 — Backend (FastAPI)

Phase 1 — Core MVP, étape « **Auth + Projects + Dashboard** ».
Le contrat d'API est défini par `frontend/src/services/api.js` — les réponses
miment exactement les formes de `frontend/src/data/mock.js`.

## Lancer

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # DEBUG=true → le code OTP est renvoyé dans la réponse
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Docs Swagger : http://localhost:8000/docs
- Health : `GET /api/health`
- Base de données : SQLite (`backend/data/root404.db`) par défaut, créée +
  seedée automatiquement au premier démarrage. Pour PostgreSQL :
  `DATABASE_URL=postgresql+psycopg2://…` (+ `pip install psycopg2-binary`).

## Authentification (OTP + JWT, sans mot de passe)

1. `POST /api/auth/otp` `{ "email": "abdeljalil@root404.tn" }`
   → `{ "sent": true, "email": "…", "dev_code": "123456" }` (dev_code seulement si `DEBUG=true`)
2. `POST /api/auth/verify` `{ "email": "…", "code": "123456" }`
   → `{ "token": "JWT…", "user": { … } }`
3. Tous les endpoints protégés attendent `Authorization: Bearer <token>`.

Compte de démo pré-seedé : **abdeljalil@root404.tn** (profil complet).
Tout autre e-mail valide crée un nouveau compte étudiant au premier
vérification — inutile de s'inscrire pour tester.

`POST /api/auth/register` (candidature Piscine) crée un compte `status: "piscine"`.

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/auth/otp` | Demande un code OTP (rate-limit 60 s, TTL 10 min, stocké hashé) |
| POST | `/api/auth/verify` | Vérifie le code → JWT (7 j) + user |
| POST | `/api/auth/register` | Candidature Piscine → compte pending |
| GET | `/api/auth/me` | Utilisateur courant |
| POST | `/api/auth/logout` | No-op (JWT stateless) |
| GET | `/api/projects` | Projets du parcours, statut par utilisateur (done / progress / failed / available / locked) |
| GET | `/api/projects/{slug}` | Détail d'un projet (404 si inconnu) |
| POST | `/api/projects/{slug}/submit` | Enregistre une soumission `{files: [{path, content}]}` → `running`, la Moulinette l'analyse en arrière-plan (throttle : 1 soumission en cours par projet) |
| GET | `/api/projects/{slug}/template` | Fichiers de départ du projet `{slug, files: [{name, lang, content}]}` (chargés dans l'éditeur) |
| GET | `/api/projects/{slug}/last-result` | Dernier résultat de la Moulinette `{status, score, tests, terminal, via, at}` (404 si aucune) |
| POST | `/api/judge/run` | Workspace « Exécuter » : compile + 1 run → `{lines, exit, via}` |
| POST | `/api/judge/moulinette/{slug}` | Moulinette complète : `{files?}` → `{tests, score, status, error?, lines, via}` (files → dernière soumission → template) |
| GET | `/api/peer-review` | `{upcoming, available, history, stats}` — slots de correction (mock-compatible) |
| POST | `/api/peer-review/slot` | `{project, when?}` — ouvre un créneau (projet validé à la moulinette requis) |
| POST | `/api/peer-review/{id}/reserve` | Je me propose comme correcteur (niveau ≥ l'étudiant) |
| POST | `/api/peer-review/{id}/cancel` | J'annule (étudiant) ou je me retire (correcteur → slot redevient open) |
| POST | `/api/peer-review/{id}/complete` | `{score, comment?}` — ≥75 : projet validé ; sinon échec + pénalité 2 j ; correcteur +20 CP / +50 XP |
| GET | `/api/ai/history` | Conversation AI Mentor persistée + contexte + stats (AI Dependency 30 j) |
| POST | `/api/ai/ask` | `{message, level? 1-5}` → réponse socratique contextuelle (jamais la solution) |
| GET | `/api/ai/review` | AI Code Review de la dernière soumission conclue `{metrics, notes}` |
| POST | `/api/ai/reset` | Nouvelle conversation |
| GET | `/api/dashboard/stats` | 4 tuiles KPI (XP, projets, CP, valeur de compte) — calculées en direct |
| GET | `/api/dashboard/activity` | 5 derniers événements de la timeline |
| GET | `/api/dashboard/weekly` | Activité des 7 derniers jours |

## Structure

```text
backend/
├── app/
│   ├── api/            # Routers (auth, projects, dashboard, judge)
│   ├── core/           # config (pydantic-settings), db (SQLAlchemy), security (JWT/OTP)
│   ├── services/       # serializers, seed, sandbox, moulinette, templates, progress
│   ├── models.py       # ORM : User, Project, UserProject, Submission, …
│   ├── schemas.py      # Schémas Pydantic (requêtes)
│   └── main.py         # Entrypoint FastAPI + CORS + lifespan (create_all + seed)
├── sandbox/Dockerfile  # Image runner (gcc 12, make, valgrind) — build :
│                       #   docker build -t root404-sandbox -f backend/sandbox/Dockerfile backend/sandbox
└── requirements.txt
```

## Judge / Moulinette (`app/services/`)

- `sandbox.py` — exécution sandboxée **hybride** : Docker
  (`root404-sandbox`, `--network none --memory 512m --cpus 1 --pids-limit 128
  --user 65534`) si dispo, sinon repli local avec `rlimits` (512 Mo RAM,
  12 s CPU, 16 Mo fichiers), timeout 12 s, sorties plafonnées à 1 Mo.
- `moulinette.py` — suites de tests par projet (compilation
  `-Wall -Wextra -Werror`, runs, norme statique, valgrind si présent),
  score `⌊100 × gained/total⌋`, passage si ≥ 95 sans `fail`.
- `templates.py` — fichiers de départ des 5 projets (C valides, compilables).
- `progress.py` — XP à la première validation + recalcul du niveau
  (3860 XP/niveau, max 21).
- `peer.py` — Peer Review : matching 0-100 (niveau 70 % + réputation 30 %),
  cycle de vie des slots (open → reserved → done / cancelled), récompenses
  (+20 CP / +50 XP au correcteur), validation du projet si note ≥ 75.
- `ai.py` — AI Mentor : moteur socratique par règles (12 sujets C/42 —
  segfault, pipes/fork, fuites, norme, compilation, pointeurs, threads,
  printf, EOF, complexité, GNL, refus de solution) avec contexte réel
  (dernière soumission, tests échoués) et 5 niveaux d'assistance ; AI Code
  Review calculé sur la dernière soumission conclue (metrics + notes).
  `ask()` est le point d'attache prévu pour brancher un vrai LLM ensuite.

## Étapes suivantes (Phase 1)

- Rooms & chat, Leaderboard & Coalitions, Analytics.
