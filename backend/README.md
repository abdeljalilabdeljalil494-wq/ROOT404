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
| POST | `/api/projects/{slug}/submit` | Enregistre une soumission `{files: [{path, content}]}` → `pending` (la Moulinette arrive à l'étape suivante) |
| GET | `/api/dashboard/stats` | 4 tuiles KPI (XP, projets, CP, valeur de compte) — calculées en direct |
| GET | `/api/dashboard/activity` | 5 derniers événements de la timeline |
| GET | `/api/dashboard/weekly` | Activité des 7 derniers jours |

## Structure

```text
backend/
├── app/
│   ├── api/            # Routers (auth, projects, dashboard)
│   ├── core/           # config (pydantic-settings), db (SQLAlchemy), security (JWT/OTP)
│   ├── services/       # serializers (ORM → JSON), seed (jeu de démo)
│   ├── models.py       # ORM : User, Project, UserProject, Submission, …
│   ├── schemas.py      # Schémas Pydantic (requêtes)
│   └── main.py         # Entrypoint FastAPI + CORS + lifespan (create_all + seed)
├── Dockerfile
└── requirements.txt
```

## Étapes suivantes (Phase 1)

- **Judge / Moulinette** : exécution sandboxée (Docker si dispo, sinon
  subprocess isolé avec limites CPU/RAM/réseau) + tests + score.
  Les soumissions sont déjà persistées en `pending` — rien à migrer.
- Rooms & chat, AI mentor, Leaderboard & Coalitions, Analytics.
