# ROOT404 backend — current implementation

FastAPI + SQLAlchemy; PostgreSQL production target, SQLite local/test support.
Optional Redis cache/readiness; SQL is authoritative for OTP/throttles/revocations.
**Development implementation, not production verified.** Full setup: ../INSTALLATION.md.

From repository root (Python3.11):
```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
# Configure ignored .env from .env.example; do not commit secrets.
.venv/bin/alembic -c backend/alembic.ini upgrade head
PYTHONPATH=backend .venv/bin/python -m app.manage seed-catalog
PYTHONPATH=backend .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Run `.venv/bin/pytest backend/tests -q` from root: 113backend tests pass (plus6controller tests). Production
checks head0004, not silent create_all. Existing DBs require schema/backup rehearsal;
see ../DEPLOYMENT.md. Never stamp unknown schemas to hide differences.

## Actual service boundaries
- SQL auth: HMAC OTP/expiry/atomic attempts, JWT revocation, account authorization.
- SQL fixed-window IP budgets and shared account AI budget (AI_REQUESTS_PER_HOUR=30).
- EMAIL_PROVIDER=smtp: SSL or STARTTLS; real local STARTTLS delivery verified; Internet delivery unverified. Development mail mode is
  not production delivery and must never be enabled in production.
- AI_PROVIDER=openai plus private OPENAI_API_KEY: real ask/review HTTP requests;
  bounded results, persisted owner history, no canned fallback/random grades.
  Disabled/failed provider returns503. Tests use MockTransport, not real OpenAI.
  History is displayed, not replayed as model context; privacy controls incomplete.
- Judge calls external authenticated `/v1/execute`. Dedicated Docker/runsc host dispatcher supplied; runtime unverified.
  CLI runners are trusted-test primitives, not public isolation. Missing executor
  or executable catalog suites returns503; keep judge disabled.
- Hiring/exam/mentorship prototypes require explicit development demo mode. Other
  domain routes include partial workflows, not a complete product backend.

`/health` is liveness, `/ready` checks SQL/optional Redis, `/api/health` is throttled
API health. Production docs visibility is configuration dependent. Schedule
`PYTHONPATH=backend .venv/bin/python -m app.manage cleanup-auth` for expired state.
Actual native PostgreSQL16.2/Redis/local SMTP integration passes; no Docker,
Internet email/OpenAI or production deployment evidence exists here.
See ../FEATURE_COMPLETION_MATRIX.md and ../SECURITY.md for scope/security boundaries.

Account Settings routes: /api/account/privacy, /profile, /export,
/sessions/revoke-all, DELETE /account. Private defaults/global revocation in0004.
Retention CLI: `python -m app.manage retention` (dry-run), --apply only after review.
Foundation suites: `python -m app.manage seed-execution-projects`.
See ../docs/LIVE_SERVICE_VERIFICATION.md and ../docs/PRIVACY_RETENTION.md.
