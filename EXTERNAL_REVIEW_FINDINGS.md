# EXTERNAL REVIEW FINDINGS (32 findings, P0-P4)

> WARNING: This review was written against an OLDER snapshot of the repository
> (it mentions `mock.jwt.token`, `VITE_USE_MOCK` default true, 53 tests, seeding in lifespan).
> Many findings may already be fixed and line numbers are likely stale.
> Treat this file as UNTRUSTED input: verify every finding against the CURRENT code.

---

## P0 — Broken core flows — ship nothing until this is fixed

### 1. Auth pages never hit the API — login/register are fake
Files: `frontend/src/pages/auth/Login.jsx:27-48` (sendOtp / verify use setTimeout + `localStorage.setItem('root404_token','mock.jwt.token')`), `frontend/src/pages/auth/Register.jsx:29-34` (next just does `setTimeout(() => navigate('/dashboard'))`)

Why it matters: The entire backend `POST /api/auth/otp|verify|register` with OTP rate limiting + JWT exists (`backend/app/api/auth.py`), but UI never calls `authService.requestOtp/verifyOtp` from `frontend/src/services/api.js:168-190`. Every QA tester "logs in" while unauthenticated. `mock.jwt.token` passes the 3-part format check in `api.js:83` and then fails on `backend/app/core/security.py:decode_token` → 401 → `api.js:132` silently clears token and falls back to mock data. Looks green in dev, broken in staging/prod.

### 2. `VITE_USE_MOCK !== 'false'` hides all bugs
Files: `frontend/src/services/api.js:126-155` (`const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'` + `resolve()`), `frontend/.env.example:3`, `vite.config.js: proxy`

Why it matters: Default is mock. Plus fallback: on any network error in DEV it console.warn and returns mock (`if (import.meta.env.DEV) return mock`). Integration regressions, CORS, 413/429, missing security headers never surface. Flip default to false or make `resolve` throw in CI.

### 3. Demo data seeding on boot → production takeover risk
Files: `backend/app/main.py:40-90` (lifespan seeds 9 Project + demo User `abdeljalil@root404.tn` if `count()==0`), `backend/app/api/projects.py: seed endpoint` (blocked in prod but lifespan runs in prod too)

Why it matters: Fresh prod DB gets a public account `is_active=True, is_verified=True, level=6.42` with known email. An attacker can `POST /api/auth/otp` for that address. In development `dev_otp` is returned verbatim (`backend/app/api/auth.py:60-65`), instant account takeover. Make seeding CLI-only, remove from lifespan, and delete demo user from prod fixtures.

### 4. OTP insecure bypass in non-prod
Files: `backend/app/api/auth.py:78-84` (`if not is_valid and ENVIRONMENT!='production': last = get_last_otp(email); if last and code==last: is_valid=True`)

Why it matters: Duplicates verification path; even if `_otp_store.verify` enforces SHA256 + `hmac.compare_digest` + max attempts, the fallback skips attempt counting. An attacker brute-forces via `get_last_otp` endpoint (exposed via `dev_otp` response). Should gate behind explicit `ENABLE_DEV_OTP` flag, not just `ENVIRONMENT`.

---

## P1 — Security / risky code

### 5. localStorage JWT + no CSRF/httpOnly
Files: `frontend/src/services/api.js:79-95` (stores `root404_token`), `frontend/src/pages/auth/Login.jsx:38`, `backend/app/core/security.py: create_access_token` (7-day expiry, jti generated but never revoked), `backend/app/core/dependencies.py: get_current_user`

Why it matters: Any XSS in bio, room.name, project.desc can exfiltrate token. XSS sanitization is only log not block (`security.py: sanitize_input:220-250` only `logger.warning`). Switch to httpOnly Secure SameSite=Strict cookie or at least add token revocation list via jti in Redis + short expiry + refresh token.

### 6. `get_client_ip` trusts X-Forwarded-For → rate-limit bypass
Files: `backend/app/core/dependencies.py:44-55` (`forwarded.split(',')[0]`), `backend/app/core/security.py: ThreadSafeOTPStore: rate_limit`

Why it matters: Client sends `X-Forwarded-For: 1.1.1.1` and evades `auth_rate_limit` (10/60) and `judge_rate_limit` (20/60). Health check `api/router.py:55-66` uses same. Fix: only trust proxy IPs set in config (`settings.TRUSTED_PROXIES`) or use `request.client.host` behind Nginx.

### 7. In-memory rate limiters break with 2 workers / scale
Files: `backend/app/core/dependencies.py:13-35` (RateLimiter RLock dict), `backend/app/core/security.py:18-60` (ThreadSafeOTPStore), `backend/Dockerfile: CMD ... --workers 2`, `docker-compose.yml: backend: --workers 2`

Why it matters: Each worker has its own bucket → effective limit 2×. Redis is already in docker-compose.yml but unused. Migrate to redis INCR + EXPIRE; tests calling `_clear_rate_limiter()` will fail in multi-process.

### 8. CSP contradictions + unsafe-inline + internal host leak
Files: `frontend/Dockerfile: CSP` (`script-src 'self' 'unsafe-inline'; connect-src 'self' http://backend:8000`), `backend/app/main.py: security_headers_middleware` (sets `default-src 'self'; script-src 'self'` without unsafe-inline), `docker-compose.yml: nginx`

Why it matters: unsafe-inline nullifies CSP against XSS. `http://backend:8000` exposes internal Docker DNS to browser (will fail CORS anyway). Align both: `connect-src 'self' /api`, remove unsafe-inline via nonce/hash or move inline styles to Tailwind.

### 9. Dangerous frontend sanitization = no-op
Files: `frontend/src/services/api.js:14-22` (sanitizeInput only strips \x00 + truncate), `backend/app/core/security.py:225-246` (only logs dangerous_patterns)

Why it matters: `<script>alert(1)</script>` stored as text → React escapes, but `dangerouslySetInnerHTML` later (e.g., ai_helper notes) would execute. Also JSON fields `User.bio` truncated to 1000 in `models/user.py: to_dict` but not sanitized. Add server-side bleach/html.escape on write and enforce on bio, room.name, message.

### 10. Path traversal validation inconsistent
Files: `frontend/src/services/api.js:24-33` (`..\` check uses `'\\x00'` literal not `'\x00'`), `backend/app/services/judge.py:80-98` (checks ".." in filename but not encoded `%2e%2e`), `judge_sandbox/runner.py:45-52` (`Path.resolve().relative_to` after mkdir but fname may contain /)

Why it matters: `validateFileName` never triggers on actual null byte because it tests literal `\x00`. Add canonical `Path(fname).parts` + PurePath check and reject any `/` separator upfront.

### 11. CAP_DROP ALL + cap_add: DAC_OVERRIDE cancels hardening
Files: `docker-compose.yml: frontend/backend/db/redis cap_add`

Why it matters: DAC_OVERRIDE lets container bypass file permission checks — defeats `read_only: true` + chmod 755 go-w. db sets `read_only: false` needed, but frontend and backend don't need DAC_OVERRIDE. Minimal caps: CHOWN, SETGID, SETUID, NET_BIND_SERVICE only for frontend.

### 12. Frontend container exposed on 0.0.0.0:80 despite claim of 127.0.0.1-only
Files: `docker-compose.yml: frontend ports: - "80:80"` vs `FINAL_REPORT.md: Port binding to 127.0.0.1`, `SECURITY.md`

Why it matters: backend/db/redis correctly bind `127.0.0.1:5432/6379/8000` but frontend exposes port 80 globally. On a VPS this is intended, but doc says opposite — either fix doc or change to `127.0.0.1:80:80` + external reverse proxy.

### 13. Build writes secrets to logs
Files: `backend/app/main.py: lifespan: logger.info(f"Database: {get_safe_database_url()}")`, `docker-compose.yml: environment: SECRET_KEY: ${SECRET_KEY:?must be set}`, `backend/app/core/config.py: get_safe_database_url()`

Why it matters: DATABASE_URL masked but SECRET_KEY is not; POSTGRES_PASSWORD visible via `docker inspect` env and `logger.info` CORS_ORIGINS. Use Docker secrets (`secrets:`) not env, and set hide_env in compose.

### 14. Judge forbidden-pattern bypass
Files: `backend/app/services/judge.py: FORBIDDEN_PATTERNS` (e.g. `r'import\s+os'`), `judge_sandbox/runner.py: FORBIDDEN` + `judge_sandbox/runners/runner_c.py|runner_python.py`

Why it matters: `imp"+"ort os`, `os . system`, Unicode homoglyphs, `#include /*comment*/ <net>` all bypass regex. Defense-in-depth OK but doc claims "no command injection". Move from regex to allow-list: compile sandbox with seccomp profile already referenced but still `seccomp:unconfined` in `docker-compose.yml: judge: security_opt`. Supply real seccomp.json and drop regex as primary control.

### 15. `example.env` is not an example — contains single `1`
Files: `example.env` (contents `1\n`), `.env` (same `1\n`), `.env.example` (real template), `.gitignore: .env`

Why it matters: New contributor follows `example.env` → `docker-compose up` fails `SECRET_KEY must be set` with cryptic error. Delete `example.env` or make it symlink to `.env.example`; ensure `.env` not committed (it is ignored but `git diff --name-only HEAD origin/main` still listed `.env` → history contains secret leak, purge with `git filter-repo`).

---

## P2 — Missing tests (the reason bugs 1-14 survived)

### 16. No auth negative-path test without dev_otp
Files: `backend/tests/test_api.py: get_token_for_demo()` (relies on dev_otp), `frontend/src/services/api.test.js:8-30` (only asserts 200 fallbacks)

Why it matters: Production disables dev_otp (`security.py: get_last_otp returns None`) but no test covers SMTP-mocked OTP delivery. Add pytest monkeypatch smtplib + assert `POST /api/auth/otp` returns 200 without dev_otp, then verify with stored OTP.

### 17. No concurrency test for BlackHole absorption / XP double-award
Files: `backend/app/services/blackhole.py:88-114` (`update_user_blackhole` commits + `is_active=False`), `backend/app/services/gamification.py` (adds XP without row lock), `backend/app/api/projects.py: submit` (calls plagiarism non-critical, then GamificationService)

Why it matters: Two parallel `POST /api/projects/{slug}/submit` can both see score>=80 → double XP + level bump + xp_to_next miscalc. Missing `SELECT ... FOR UPDATE` or version_id. Add async concurrent test with ThreadPoolExecutor submitting same slug.

### 18. Room capacity race
Files: `backend/app/services/room_service.py: join_room` (check `members_count < capacity` then add), `backend/app/models/room.py: capacity CheckConstraint 1-1000`

Why it matters: No DB transaction isolation → 2 joiners at capacity 2 both succeed → `members_count=3`. Need unique user+room index already there, but capacity needs `SELECT FOR UPDATE` on Room. No test for it.

### 19. PeerReview N+1 + authz bypass untested
Files: `backend/app/api/peer_review.py: list_corrections` (loops `db.query(User).filter(...).first()` per correction), `backend/tests/test_edgecases.py: test_path_traversal_attempts` (only tests projects/submit not `peer-review/{id}/review`)

Why it matters: `correction_id` is `String(32)` guessable (`c_`+10 hex); no test that user B can't `POST /peer-review/{id}/review` for correction they're not part of (check exists `author_id != current_user.id` and `corrector_id != ...` but no IDOR test for another user's correction). Add `test_peer_review_idor` + fix N+1 via joinedload.

### 20. Frontend critical user flows untested
Files: `frontend/src/pages/Workspace.jsx:479` lines (Monaco editor, fileTree, submit), `frontend/src/pages/Dashboard.jsx`, `frontend/src/pages/RoomView.jsx`, `frontend/src/pages/ProjectDetail.jsx`, `frontend/src/services/api.test.js` (only 14 tests, all service-layer)

Why it matters: Most crash surface is UI (ErrorBoundary tested only via ErrorBoundary.jsx story). No React Testing Library test for 401→logout event (`api.js:118`), 429 Retry-After dispatch, or Workspace auto-save. Add at least smoke tests for App.jsx routing + Sidebar active state.

### 21. No test for health rate limit + security headers
Files: `backend/tests/test_security.py: TestSecurityHeaders: test_security_headers_present` (asserts `X-Process-Time` exists, not `X-Content-Type-Options` value), `backend/app/main.py: security_headers_middleware` (only if `ENABLE_SECURITY_HEADERS`)

Why it matters: Test passes even if header value is wrong. Make strict: `assert resp.headers["X-Content-Type-Options"]=="nosniff"` etc., and test 429 path (`GET /health` 61st request).

### 22. judge simulate vs real diverge — no contract test
Files: `backend/app/services/judge.py: simulate_execution` (deterministic `random.Random(hash)`), `judge_sandbox/runner.py: run_in_sandbox` (subprocess `runner_c.py`), `backend/tests/test_api.py: test_judge_moulinette`

Why it matters: Test asserts only score in response, not output truncation 10000/5000, timeout clamp 30s, or security field. Add contract test that both paths return same schema (`status, score, tests[], logs, execution_time, security`).

---

## P3 — Documentation gaps

### 23. README is vision doc, not contributor guide
Files: `README.md` (1337 chars), `ARCHITECTURE.md`, `PROJECT_STATUS.md`, `FINAL_REPORT.md` (branch `arena/01a0b433` out-of-date, claims 53 tests passing but current branch shows `FINAL_REPORT.md:53` tests while `conftest.py` missing DB setup for new models)

Why it matters: New dev can't tell what is mocked (WebRTC RoomView, Arena live, Exam lockdown, Hiring portal) vs implemented. Add top table: Component | Status | File | Mock? Link to `services/*.py`.

### 24. SECURITY.md claims audit trail but no retention/GDPR
Files: `SECURITY.md`, `backend/app/models/__init__.py: AuditLog` (no expiry), `backend/app/services/integrity.py`

Why it matters: `audit_logs` grows unbounded; Tunisia PDPA requires disclosure + retention max 2y. Add `created_at` TTL policy + note in SECURITY.md reporting email (currently placeholder).

### 25. Env var docs inconsistent
Files: `backend/.env.example`, `.env.example`, `frontend/.env.example`, `backend/app/core/config.py: Settings` (reads ENVIRONMENT, DATABASE_URL, CORS_ORIGINS, JUDGE_* but RATE_LIMIT_* only used in `dependencies.py`)

Why it matters: `frontend/.env.example` says `VITE_USE_MOCK=true` while root `.env.example` says `VITE_USE_MOCK=false`. `backend/.env.example` still has `SECRET_KEY=root404-dev...` which fails prod check len<32? Actually 45 → passes but weak. Consolidate to single `.env.example` with generation `openssl rand -hex 32` comment.

### 26. No API versioning despite API_V1_PREFIX=/api
Files: `backend/app/core/config.py: API_V1_PREFIX="/api"`, `backend/app/api/router.py: api_router` (included as `/api`), `backend/README.md` (lists endpoints without prefix)

Why it matters: `frontend/src/services/api.js baseURL=/api` hardcodes; bump to `/api/v1` will break. Either drop `API_V1_PREFIX` or version router: `app.include_router(api_router, prefix=settings.API_V1_PREFIX)`.

### 27. Frontend README.md missing required VITE_API_TARGET note
Files: `frontend/README.md: Env vars table`, `frontend/vite.config.js: server.proxy['/api'].target: process.env.VITE_API_TARGET`

Why it matters: `process.env` is Node-side but Vite reads `import.meta.env.VITE_API_TARGET`; proxy always falls back to localhost:8000 ignoring .env var — doc lies. Fix to `loadEnv`.

---

## P4 — Developer-experience fixes (quick wins)

### 28. Makefile fragile + npm run lint always fails
Files: `Makefile:13-34` (install: `cd backend && python3 -m venv venv` not idempotent, dev: `(cd backend && ./venv/...) & (cd frontend && ...) & wait` no trap/kill, no test frontend), `frontend/package.json: scripts.lint: "eslint src/ --ext .js,.jsx"` but eslint not in devDependencies

Why it matters: `make dev` leaves zombies on Ctrl-C, `make lint` exits 127 → CI red. Add `trap 'kill 0' EXIT`, `npm install --only=dev eslint`, or switch to concurrently, expose `make test-front`.

### 29. No CI / pre-commit for secrets
Files: `.git/hooks/commit-msg.sample` (sample not active), `.gitignore: .env` (but `.env` with `1` already tracked), no `.github/workflows/`

Why it matters: Secrets commit not blocked; add gitleaks pre-commit + GitHub Action backend `pytest -v` + frontend `vitest run` + `docker-compose config -q`.

### 30. Hot-reload broken in Docker
Files: `docker-compose.yml: backend volumes: ./backend/app:/app/app:ro` + `read_only: true`, `backend/Dockerfile: CMD uvicorn --reload`

Why it matters: Read-only mount + UV_THREADPOOL prevents file watch trigger. Remove `:ro` for dev compose or add `compose.dev.yml` override with `:delegated` and `--reload-dir`.

### 31. Tailwind + Monaco chunking not lazy
Files: `frontend/vite.config.js: manualChunks: monaco: ['@monaco-editor/react']`, `frontend/src/pages/Workspace.jsx: import Editor from '@monaco-editor/react'` (eager), `tailwind.config.js: content: ['./src/**/*.{js,jsx}']` (scans dist/ in CI)

Why it matters: 300kB Monaco loaded on homepage (Home.jsx not using it). Change Workspace to `lazy(() => import('@monaco-editor/react'))` and limit tailwind content properly, saving ~40% initial load.

### 32. Type safety none
Files: `frontend/src/pages/*.jsx` (27 screens), `frontend/src/components/ui/*` (14 primitives), no propTypes, no tsconfig

Why it matters: `Badge tone="brand"` typo silently falls back to muted (`Button.jsx: VARIANTS[variant] || VARIANTS.primary`). Add minimal prop-types or migrate Button, Icon, Badge, Avatar to TS first — catches 80% of runtime errors before E2E.

---

## Suggested order of work (from the reviewer)
1. Fix 1+2+3 (auth mock + seed) → unblocks real integration testing.
2. Fix 6+7+8 (IP spoof + redis limiter + CSP) → closes trivial bypasses.
3. Add 16+17+18 tests → prevents regressions.
4. Clean 15+28+29 DX → stops secret leaks and speeds onboarding.
