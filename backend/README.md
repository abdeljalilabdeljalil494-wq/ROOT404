# ROOT 404 — Backend API

> FastAPI + SQLAlchemy + Docker Sandbox + AI Mentor + Peer Review

## Quick start

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set env (optional, defaults to SQLite)
cp .env.example .env

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/api/docs

## Architecture

```
app/
├── core/
│   ├── config.py       # Settings via pydantic-settings
│   ├── database.py     # SQLAlchemy engine + SessionLocal + init_db
│   ├── security.py     # JWT + OTP + password hashing
│   └── dependencies.py # get_current_user, rate_limit
├── models/
│   ├── user.py         # User + XP/Level/BlackHole
│   ├── project.py      # Project + UserProjectProgress
│   ├── submission.py   # Submission + Moulinette results
│   ├── correction.py   # Correction + CorrectionSlot
│   ├── room.py         # Room + RoomMember + RoomMessage
│   ├── coalition.py    # Coalition + CoalitionMember + CoalitionWar
│   └── __init__.py     # DailyMission, Badge, AuditLog, ArenaMatch, PiscineDay
├── schemas/
│   ├── auth.py
│   ├── project.py
│   ├── judge.py
│   └── room.py
├── services/
│   ├── judge.py        # Moulinette + Polyglot runners + plagiarism
│   ├── ai_helper.py    # Socratic hints, 5 levels, anti-cheating
│   ├── blackhole.py    # Survival timer, warning zone, absorption
│   ├── correction.py   # Smart Peer Matchmaking
│   ├── coalition.py    # Coalition scoring, wars
│   ├── room_service.py # Collaboration rooms
│   ├── gamification.py # XP, Level 0-21, badges, streak, daily missions
│   ├── skill_graph.py  # Dynamic skill measurement, gaps, micro-challenges
│   └── integrity.py    # Trust score, plagiarism, audit trail
└── api/
    ├── auth.py         # OTP + JWT + register + me
    ├── projects.py     # CRUD + submit + moulinette + unlock
    ├── dashboard.py    # stats, activity, weekly, overview
    ├── leaderboard.py  # global, coalitions, campus, arena
    ├── rooms.py        # list, create, join, messages, members
    ├── judge.py        # run, moulinette, review, plagiarism, runners
    ├── ai.py           # ask, review, levels, gaps, history
    ├── analytics.py    # overview, skills, journey, heatmap, reputation
    ├── peer_review.py  # request, review, slots, booking
    ├── coalitions.py   # leaderboard, join, wars
    ├── piscine.py      # days, stats, seed
    ├── arena.py        # modes, live, match, leaderboard
    ├── portfolio.py    # public portfolio, widget
    ├── hiring.py       # companies, challenges, fair
    ├── exam.py         # tracks, start, submit, gates
    ├── mentorship.py   # mentors, request, schedule, become-mentor
    └── router.py       # aggregates all routers under /api
```

## Auth Flow — Email OTP

1. `POST /api/auth/otp` with email → generates 6-digit code, stored hashed, expires in 10 min
2. In dev, `dev_otp` returned in response. In prod, sent via email (SMTP not wired yet).
3. `POST /api/auth/verify` with email+code → returns JWT `access_token`
4. Client stores token in `localStorage.root404_token`, axios interceptor adds `Authorization: Bearer <token>`

## Projects Lifecycle

```
LOCKED → AVAILABLE → IN_PROGRESS → SUBMITTED → MOULINETTE → PEER_REVIEW → AI_ANALYSIS → PASSED → UNLOCK_NEXT
```

- `POST /api/projects/{slug}/submit` with `{files: {filename: content}, language}` runs moulinette via `services/judge.py`
- Score >=80 → `passed`, unlocks next projects where `requires == slug`, awards XP via `gamification.py`, updates skill graph
- Plagiarism check against last 20 submissions for same project via `integrity.py`

## Moulinette / Judge Engine

- `judge_sandbox/` contains isolated runners: `runner_c.py`, `runner_cpp.py`, `runner_python.py`, `runner_js.py`
- `runner.py` is entry point inside Docker container `ubuntu:22.04`, no network, 512m, 1 vCPU
- In dev (`JUDGE_ENABLED=false`), `services/judge.py` simulates execution deterministically based on code hash
- `GET /api/judge/runners` lists available languages and isolation config

## AI Mentor 2.0

5 levels of assistance, never gives final solution:

1. Hint initial
2. Question socratique
3. Explication du concept
4. Exemple simplifié (non copiable)
5. Ressources & exercices

- `POST /api/ai/ask` with `{message, level, project_slug, code}` returns socratic hint
- Anti-cheating: `detect_cheating` flags large pastes with low interaction
- Code review: `analyze_code_review` returns metrics (Correctness, Memory Safety, Code Quality, Complexity, Readability) + notes

## Peer Review — Smart Matchmaking

- `find_best_corrector` scores candidates by:
  - Reputation
  - Level proximity (prefer +0..3 levels above)
  - Same campus bonus
  - Avoid recent same pairs (last 7 days)
  - Open slots availability
  - Random factor for load balancing
- Checklist generated per project type (e.g., minishell adds builtins, pipes, signals)

## Black Hole

- Each user has `blackhole_days_left` / `blackhole_total` (default 120)
- `calculate_days_left`: base - days_since_active + bonus (7 days per project in last 30 days) + level*2
- Warning zone <=7 days, absorbed <=0 → `is_active=False` (frozen)
- `POST /api/analytics/blackhole` returns status + recommendation
- Cron `run_daily_check` checks all active users

## Skill Graph

- Groups: C, Algorithms, Systems, Tooling
- Each project maps to skill weights (e.g., minishell → C.Pointers 25, Systems.Processes 20)
- On submission with score, skills increased by `weight * score/100 * 0.1`
- Gaps = skills <50, sorted lowest first
- `GET /api/analytics/skills` returns graph, `GET /api/ai/gaps` returns gaps + micro-challenges

## Gamification

- XP → Level 0.00-21.00 via exponential thresholds: `threshold[n] = threshold[n-1] + 1000 * 1.25^n`
- `add_xp` updates level, xp_to_next, jetons on level up
- `complete_project`: XP * score%, +15% bonus if 100%, updates accuracy
- Daily Mission: generated per user, expires in 24h, based on weakest skill
- Streak: +1 if last activity yesterday, reset if >1 day gap, burnout detection if >20

## Coalition

- 4 default: The Phoenix, Neon Wolves, Data Vipers, Sand Foxes
- Auto-assign to smallest coalition for balance
- Points += on project completion, wars, etc.
- `POST /api/coalitions/wars` creates 48h competition

## Rooms

- Types: study, correction, pair, competition, mentor, live
- `RoomService`: create, join (capacity check), leave, members, messages
- Messages stored in `room_messages`, would be WebSocket in prod
- Seed creates 6 demo rooms

## Integrity / Trust Score

- Factors: Code Similarity (from submissions), Typing Pattern (keystroke dynamics placeholder), Submission Pattern (rapid submissions), AI Dependency (mentor usage), Peer Review validity
- `calculate_score` returns total 0-100 + rows with tone ok/warn/danger
- `check_plagiarism`: normalizes code (remove whitespace/comments), Jaccard on tokens, fingerprint via MD5
- `AuditLog` records every sensitive action

## Seeding

On startup, if DB empty:
- 9 projects (get_next_line → ft_transcendence)
- 4 coalitions
- Demo user abdeljalil (Level 6.42, XP 24780)

Manual seed endpoints:
- `POST /api/projects/seed`
- `POST /api/rooms/seed`
- `POST /api/piscine/seed`

## Testing

```bash
# Install test deps
pip install pytest httpx

# Run
pytest tests/ -v
```

## Docker

```bash
docker-compose up --build
# Frontend → http://localhost:5173
# Backend  → http://localhost:8000/api/docs
# DB       → localhost:5432
```

## Public API

- `GET /api/portfolio/{username}` → public developer portfolio
- `GET /api/portfolio/public/{username}/widget` → embeddable widget
- `GET /api/hiring/companies` → partner companies
- Swagger at `/api/docs` is the interactive public API docs

## Environment

See `.env.example` for all vars. For prod, set `DATABASE_URL` to Postgres and `SECRET_KEY` to a strong random value.
