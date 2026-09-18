# ROOT 404 — Architecture Documentation

## Overview

ROOT 404 is a full-stack **Developer Learning Operating System**, inspired by École 42, built for Tunisian coders. It combines:

- **Frontend**: React 18 + Vite 5 + Tailwind + Monaco Editor
- **Backend**: FastAPI + SQLAlchemy + SQLite/Postgres + JWT OTP
- **Sandbox**: Docker Ubuntu 22.04 isolated runners (C, C++, Python, JS)
- **AI Mentor**: Socratic hints, 5 levels, anti-cheating
- **Real-time**: Rooms, Peer Review, Arena (WebSocket-ready)

## System Diagram

```
                    ┌─────────────────────────────────────────┐
                    │   Front-End: React + Monaco Editor      │
                    │   PublicLayout / AppLayout / Workspace  │
                    └────────────────────┬────────────────────┘
                                         │ REST / WS
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │    Back-End API Engine (FastAPI)        │
                    │  Auth (OTP), Judge, AI, Peer Review     │
                    │  Black Hole, Coalitions, Gamification   │
                    └──────┬──────────────┬──────────────┬────┘
                           │              │              │
          ┌────────────────┘              │              └────────────────┐
          ▼                               ▼                               ▼
┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
│  PostgreSQL /     │           │ Docker Containers │           │  AI Assistant API │
│  SQLite DB        │           │ Ubuntu + Runners  │           │ Socratic Hints     │
│  Users, Projects  │           │ Moulinette Engine │           │ & Code Review      │
│  Submissions,     │           │ Polyglot          │           │                    │
│  Rooms, etc.      │           │                   │           │                    │
└───────────────────┘           └───────────────────┘           └───────────────────┘
                           │
                           ▼
                ┌───────────────────────┐
                │  WebRTC Correction     │
                │  Rooms (Peer Review)   │
                └───────────────────────┘
```

## Backend Modules

### Core
- `config.py`: pydantic-settings, env vars, defaults to SQLite
- `database.py`: engine, SessionLocal, Base, init_db()
- `security.py`: JWT creation/verification, OTP generation (hashed, 10min expiry, in-memory store for dev), bcrypt
- `dependencies.py`: get_current_user (JWT Bearer), rate limiting (in-memory)

### Models (SQLAlchemy)
- `User`: id, username, email, display_name, level (float 0-21), xp, projects_done, correction_points, campus, coalition_id, blackhole_days_left, is_active, is_mentor, skills (JSON), badges (JSON)
- `Project`: slug, name, description, level, lang, tags, xp, difficulty, requires (slug), objectives, constraints
- `UserProjectProgress`: user_id, project_id, status (locked/available/progress/passed/failed), progress %, score, attempts, best_score
- `Submission`: user_id, project_id, files (JSON), language, status, score, tests (JSON), logs, ai_review, similarity_score
- `Correction`: submission_id, author_id, corrector_id, status, score, checklist (JSON), scheduled_at, room_id
- `CorrectionSlot`: corrector_id, project_id, start_time, end_time, is_booked
- `Room`: name, type (study/correction/pair/competition/mentor/live), project, host_id, capacity, tags
- `RoomMember`, `RoomMessage`
- `Coalition`, `CoalitionMember`, `CoalitionWar`
- Additional: `DailyMission`, `Badge`, `UserBadge`, `AuditLog`, `ArenaMatch`, `PiscineDay`, `UserPiscineProgress`

### Services
- `judge.py`: `run_moulinette()` simulates deterministic scoring based on code hash, `run_code_in_sandbox()` checks forbidden patterns, `JudgeService.check_plagiarism()` Jaccard bigram similarity, `analyze_complexity()`
- `ai_helper.py`: `detect_topic()` keyword matching, `get_socratic_hint()` 5 levels, `analyze_code_review()` metrics + notes, `AIMentorService.ask()`, `detect_cheating()`
- `blackhole.py`: `calculate_days_left()` = total - inactive_days + projects_last_30d*7 + level*2, warning <=7, absorbed <=0, `run_daily_check()` cron
- `correction.py`: `find_best_corrector()` scoring: reputation*0.5 + level proximity + campus bonus - recent pairs*30 + open slots*10 + random, `get_checklist_for_project()`, `calculate_correction_points()`
- `coalition.py`: leaderboard, auto-assign to smallest, add_points, wars
- `room_service.py`: create, join (capacity check), leave, members, messages, list, details
- `gamification.py`: XP thresholds exponential `1000*1.25^n`, `xp_to_level()`, `add_xp()`, `complete_project()` with bonus, `generate_daily_mission()` based on weakest skill, `check_streak()` + burnout detection
- `skill_graph.py`: groups C/Algorithms/Systems/Tooling, project→skill weight map, `update_from_submission()` gain = weight*score/100*0.1, gaps <50
- `integrity.py`: 5 factors (similarity, typing, submission pattern, AI dependency, peer review), `check_plagiarism()` fingerprint MD5 + Jaccard tokens, `log_action()` to AuditLog

### API Routers
All under `/api` prefix:
- `auth`: OTP request/verify, register, me, me/full (with skills, integrity, daily mission, streak)
- `projects`: list with filters (status, lang, q), by slug, submit (runs moulinette, plagiarism, unlocks next, XP, skill update), submissions, seed
- `dashboard`: stats, activity, weekly, overview (aggregates), heatmap
- `leaderboard`: global with campus/coalition filters, coalitions, campus, arena
- `rooms`: list, create, get details, join/leave, messages, members, seed
- `judge`: run code, moulinette/{slug}, review, plagiarism, complexity, runners list
- `ai`: history, ask, review, levels, gaps, detect-cheating
- `analytics`: overview (velocity, consistency, tolerance, timeToSolve), skills, journey, heatmap, reputation, integrity, blackhole, velocity
- `peer_review`: list (by role), request, get, review (score + checklist), slots create/list/book
- `coalitions`: list, join, wars, me
- `piscine`: days (with user progress), stats, seed
- `arena`: modes, live matches, create/join match, leaderboard
- `portfolio`: by username (public), me, widget
- `hiring`: companies, challenges, apply, fair
- `exam`: tracks, start (random exercises), submit, history, gates
- `mentorship`: mentors list, request, schedule, sessions, become-mentor
- Root: health, search

## Frontend Structure

```
src/
├── main.jsx              # ReactDOM + ThemeProvider + BrowserRouter
├── App.jsx               # All routes lazy-loaded
├── styles/index.css      # Tailwind layers + .card/.chip/.input
├── data/mock.js          # Single source of demo content
├── services/api.js       # Axios + all services with mock fallback
├── hooks/
│   ├── useTheme.jsx      # dark/light, localStorage
│   └── usePageHeader.js  # pushes title into AppLayout topbar
├── layouts/
│   ├── PublicLayout.jsx  # Navbar + Outlet + Footer
│   └── AppLayout.jsx     # Sidebar + AppTopbar + Outlet
├── components/
│   ├── Logo.jsx          # ROOT 404 glyph SVG
│   ├── ui/               # 14 primitives: Icon, Button, Badge, etc.
│   ├── layout/           # Navbar, Sidebar, AppTopbar, Footer
│   └── landing/          # 8 marketing sections
└── pages/
    ├── Home.jsx          # Landing with Hero, Pathways, etc.
    ├── Dashboard.jsx     # Welcome + level + KPI + activity + mission
    ├── Projects.jsx      # List/grid with filters
    ├── ProjectDetail.jsx # Objectives, constraints, tabs, submissions
    ├── Workspace.jsx     # Monaco + file explorer + terminal + moulinette
    ├── Rooms.jsx / RoomView.jsx
    ├── PeerReview.jsx
    ├── Leaderboard.jsx
    ├── Coalitions.jsx
    ├── Piscine.jsx
    ├── Journey.jsx       # Code Journey map
    ├── SkillGraph.jsx    # Skill bars
    ├── Analytics.jsx     # 360° dashboard
    ├── Arena.jsx         # Modes + live duels + leaderboard
    ├── Mentor.jsx        # Chat with AI, levels, gaps
    ├── Profile.jsx       # User profile + stats + heatmap
    ├── Portfolio.jsx     # Public portfolio
    ├── Hiring.jsx        # Companies + challenges + fair
    ├── Exam.jsx          # Tracks + gates + history
    ├── Settings.jsx
    └── auth/Login.jsx, Register.jsx
```

### Design System
- Colors sampled from mockups: brand 500 #F8851F, root 950 #04090E, etc. in `tailwind.config.js`
- Typography: Inter (UI), JetBrains Mono (code), Noto Kufi Arabic (RTL)
- Utilities: .card, .chip, .input, .select, .container-page, .no-scrollbar, bg-grid, bg-dots
- Dark by default, light variant via `useTheme`

### API Integration
- `services/api.js` has `USE_MOCK = VITE_USE_MOCK !== 'false'`
- `resolve(mockValue, request)` either returns mock after delay or real HTTP
- When `VITE_USE_MOCK=false`, all services hit `/api/...` proxied to `VITE_API_TARGET` (default http://localhost:8000)
- JWT from `localStorage.root404_token` added by interceptor, 401 clears it

## Judge Sandbox

```
judge_sandbox/
├── runner.py             # Main entry, creates temp workdir, writes files, calls language runner
├── Dockerfile.runner     # ubuntu:22.04 + gcc, python3, node, valgrind, user judge, no network
└── runners/
    ├── runner_c.py       # Norminette sim, Makefile check, compilation, valgrind, functional
    ├── runner_cpp.py     # C++98 check
    ├── runner_python.py  # py_compile + execution with timeout
    └── runner_js.py      # node --check + execution
```

In production, backend would spawn `docker run --network none --memory 512m --cpus 1 --pids-limit 64` with `judge_sandbox` image.

For dev, `services/judge.py` simulates with deterministic random based on code hash.

## Security

- OTP hashed with SHA256, 10min expiry, max 5 attempts, in-memory store (would be Redis in prod)
- JWT HS256, 7 days expiry, Bearer
- Sandbox: no network, 512m, 1 vCPU, 30s timeout, 64 pids limit, read-only rootfs, tmpfs /tmp
- Plagiarism: AST-like fingerprint (normalize + MD5 + Jaccard tokens)
- Integrity Score: 5 factors, human review required if <50
- AuditLog: every sensitive action logged with user_id, action, resource, ip
- Rate limiting: in-memory per IP, 100 req/60s

## Gamification & Learning

- Level 0.00-21.00 continuous, exponential XP curve
- XP earned = project XP * score% + 15% bonus if 100%
- Jetons on level up, account value
- Streak + anti-burnout (detects >20 streak + high workload)
- Daily Mission based on weakest skill
- Skill Graph: 4 groups, dynamic update, gaps detection, micro-challenges
- Black Hole: survival timer, warning zone, absorption, recommendations
- Coalition Wars: 48h hackathons, points from member achievements

## Deployment

- `docker-compose.yml`: db (postgres:15), redis, backend (FastAPI), judge (no_internet network), frontend (nginx)
- `frontend/Dockerfile`: multi-stage node:20 build + nginx with SPA fallback + /api proxy
- `backend/Dockerfile`: python:3.11-slim + uvicorn workers 2 + healthcheck
- `Makefile`: install, backend, frontend, dev, build, docker-up/down, seed, test

## Future Work (Phase 2-6)

- WebSocket for rooms (currently REST polling)
- WebRTC for correction rooms
- Real SMTP for OTP
- Redis for OTP and caching
- Alembic migrations
- OpenAI integration for AI Mentor (currently mock socratic)
- Corporate dashboard for hiring portal
- CTF track, AI/ML bootcamp, System Design Labs content
- Multi-campus tournament logic
- Mobile app

## Testing

- Backend: `pytest tests/test_api.py` covers health, auth, projects, dashboard, judge, AI, leaderboard, rooms, analytics, portfolio, hiring, exam
- Frontend: `npm run build` ensures no build warnings, chunks <900kB warning limit, vendor splitting
