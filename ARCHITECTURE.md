# ROOT404 architecture — source-reconciled 2026-11-18

## Product direction retained
ROOT404 remains a project-based peer-learning platform with gamification, Socratic
mentoring, collaboration, competitive learning and portfolio/hiring ambitions.
See [product vision](docs/PRODUCT_VISION.md) for the full original design. A model,
route or screen is not proof that the corresponding product workflow is delivered.

## Implemented topology
```text
Browser: React 18 + Vite + Tailwind + Monaco
    /api (relative URLs)
    -> Vite development proxy OR intended Nginx production proxy
    -> FastAPI routers -> SQLAlchemy -> SQLite locally / PostgreSQL in production
                              |-> SQL OTP, request budgets, JWT revocations
                              |-> project/account/community records
                              |-> mentor interaction history (migration0003), privacy/session epoch (0004), private notifications (0005)
    -> SMTP SSL or STARTTLS delivery boundary (local verified STARTTLS mailbox; external unverified)
    -> fixed OpenAI HTTPS boundary (test-double verified)
    -> optional configured /v1/execute HTTP boundary (dispatcher supplied; Docker/runsc NOT runtime-verified)
Optional Redis: cache/readiness; NOT the authority for OTP or request throttles.
```

FastAPI entry: `backend/app/main.py`; API composition: `app/api/router.py`.
React entry/routes: `frontend/src/App.jsx`; client contracts: `src/services/api.js`.
No backend process executes submitted code directly. Browser code must use `/api`,
not sandbox localhost URLs. Preview/dev servers bind 0.0.0.0.

## Persistence and migrations
`backend/migrations/versions/0001_initial.py` is the frozen domain baseline;
0002 adds shared authentication state;0003 adds mentor interactions;0004 adds
private portfolio/directory preferences and a global session epoch;0005 adds private in-app notifications.
Production checks migration head and refuses an outdated database; create_all is
only a development convenience. Existing deployments need schema comparison,
backup/restore rehearsal, then migrations, never blind stamping or data deletion.
SQLite and actual PostgreSQL16.2 upgrades/data preservation are tested. Native
PostgreSQL limiter/OTP concurrency and pg_dump/restore pass locally; target deploy
PostgreSQL15/current patches and production operations remain unverified.

## Authentication and abuse controls
OTP HMAC, expiry, bounded attempts and atomic consumption use SQL. Email requests
have a shared budget; bearer JWT logout persists revocations. General configured
IP/auth/judge route limits use atomic SQL fixed windows, not process memory. Route
prefix + client IP prevents literal path churn bypass; forwarded IP headers are
accepted only through configured trusted proxies. These are route-scoped controls,
not comprehensive edge/DDoS protection. Cleanup of expired auth state is an operator
job. AI ask and both review routes share a SQL per-account hourly budget (default30).
SQL outage fails closed; targeted actual PostgreSQL concurrency passes. Deployment
load/high-volume/edge controls remain unverified.

## AI: actual boundaries and limitations
`app/services/ai_provider.py` sends bounded context to OpenAI, rejects redirects,
oversized/malformed/failed responses, and returns 503 on failure/unconfigured
provider. No random quality grades or template fallback in ask/review paths.
Successful responses and user questions are persisted with user ownership; review
history records a descriptor rather than the submitted code. Provider output may
itself quote code. Users may include secrets in questions: account deletion/export and explicit retention tooling exist; operator scheduling,
backup/provider erasure and consent processing policies remain outstanding. History is capped to the last 1–100 interactions;
there are no separate threads, no conversational replay to the model, no retrieval
pipeline or guaranteed Socratic quality. Mentor UI uses real APIs; attachments and
micro-challenge evaluation are disabled. Legacy scripted helper functions remain
in source but do not serve production ask/review. Lexical cheating/similarity and
complexity checks are heuristics, not proof or execution.

## Judge: implemented client versus missing executor
The client POSTs files/language/stdin/limits to configured `/v1/execute` with a
shared bearer secret, validates bounded results and compares output with DB-owned
hidden cases. No catalog case set means503. Four foundation stream-sum projects have versioned
cases across supported languages; advanced catalog harnesses remain missing.
`judge_sandbox/runners/common.py` compiles/runs trusted test programs with timeout,
resource/output bounds and cleanup. This subprocess utility is not a security
boundary for hostile code. Compose's optional `legacy-judge-cli` is a one-shot
container, not the dispatcher itself. Dedicated host-side dispatcher is in executor_service/;
it requires immutable image/gVisor/cgroupv2 and never mounts a Docker socket in jobs.

Implemented topology, still requiring live and independent review: authenticated dispatcher ->
fresh isolated unprivileged job per request -> bounded result -> guaranteed cleanup.
Enforce network denial, cgroups/CPU/memory/PID/wall/output/filesystem limits and
kernel policies. Never expose a Docker socket to the API or submitted code, never
use unconfined seccomp/AppArmor. Runtime attacks and recovery tests must precede
public execution. Keep JUDGE_ENABLED=false until that exists and is verified.

## Incomplete product components
Rooms have persistence but no implemented WebSocket/collaborative audio/video.
Peer review lacks full matching/booking/collusion lifecycle; Arena lacks verified
winner/evaluation/deadline lifecycle. Scheduled Black Hole/mission/streak operations
are not demonstrated as a deployed scheduler. Hiring/exam/mentorship routes are
development-demo gated; their fixtures are not external integrations. Many frontend
pages remain PrototypeFeature-gated. There is no delivered multi-campus tenancy,
public developer ecosystem, hiring delivery or production analytics prediction.

## Verification levels
119local backend/controller tests and30frontend tests plus lint/build pass. HTTP test-double
integration proves API/provider contract/persistence behavior, not live provider
quality or Internet SMTP delivery. Real local STARTTLS mailbox receipt and actual
PostgreSQL/Redis integrations pass; see docs/LIVE_SERVICE_VERIFICATION.md. No Docker build/start, target PostgreSQL15 deployment test,
production Nginx/TLS deployment, hostile sandbox or full browser journey was run.
See FEATURE_COMPLETION_MATRIX.md; nothing is production-verified.

## Privacy control plane
Migration0004/API account routes + Settings implement owner profile/preferences,
export/deletion/recent-auth and atomic all-session epoch revocation. Public portfolio
and directory are opt-in. Explicit CLI retention defaults30/90days and defensive
log redaction are supplied. Backup/provider deletion and independent audit remain
release gates; docs/PRIVACY_RETENTION.md names exact limitations.

## Current distinct-identity worker and product event paths
Host controller -> immutable Docker/runsc image -> trusted UID0 bounded protocol
supervisor -> forked compiler/learner UID/GID1000, zero groups/capabilities.
Supervisor has exactly5capabilities and no-new-privileges; it owns the only trusted
result stdout. Learner pipes are captured/limited and treated purely as data.
Host controls image/argv/runtime, never learner commands. Hidden expected outputs
remain server-side. Native fixed identity probe is real; Docker enforcement is NOT
yet verified, so public judging remains disabled. See executor_service/README.md.

Review slot booking/final feedback writes owner-scoped notifications in the same
transaction. PostgreSQL row locks/CAS and atomic reward increments prevent duplicate
bookings/awards; SQLite/API and actual native PG competing calls are tested. Read
APIs are bounded, private and no-store. Explicit retention includes notifications.
Active React views now connect basic review/notification/profile/portfolio,
measured learning indicators/analytics/leaderboards/search. Gated original
advanced prototypes remain source-preserved. Monaco and worker are built locally,
not fetched from CDN. Full IDE/multifile/realtime scope is still incomplete.

## ADR — beta bearer-token storage (external-review intake round)
Decision: retain the existing localStorage bearer JWT + server-side revocation for
this beta; do NOT partially migrate auth/OAuth to cookies. localStorage is exposed
to same-origin XSS; revocation does not prevent theft/reuse before revocation.
HttpOnly Secure SameSite cookies would reduce JS token access but require a complete
atomic migration: all OTP/OAuth issuance, API/WebSocket clients, logout/revoke,
credentialed origins, CSRF tokens/origin validation, callback behavior and browser
regressions. Cookies alone do not stop same-origin malicious actions. No claim that
bearer storage is safer overall or production-approved. Revisit after supplied
review/independent assessment; keep XSS prevention/CSP and narrow token lifetime.
Current work narrows script CSP without changing OAuth callback/token contracts.
