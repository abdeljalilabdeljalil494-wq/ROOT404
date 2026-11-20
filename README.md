# ROOT404 — École 1337 / TounsiCoder-AI

A Tunisian, 42-inspired peer-learning platform: project-based programming, community,
Socratic mentoring and a long-term competitive learning ecosystem.

**Private beta engineering checkpoint — NOT production ready.** No feature has
production-verification evidence. This README describes the code, not the full vision.
The [original Arabic product vision](docs/PRODUCT_VISION.md) is preserved separately
as planned design; it has not been dropped or relabeled as completed work.

## What works locally
- FastAPI/SQLAlchemy authentication, SQL OTP/expiry/attempts and JWT revocation;
  configurable SMTP TLS transport (actual local verified STARTTLS receipt; external delivery unverified).
- React 18/Vite authenticated shell, API-backed dashboard/project catalog/details,
  Monaco run/submit actions, Mentor conversation/history and real account Settings. Explicit loading,
  empty and failure states replace silent mock fallbacks.
- SQL-shared fixed-window request limits and per-account AI ask/review budget.
- Provider-backed AI ask/review and owner-scoped stored interaction history.
  Missing/failed provider returns 503, never a scripted successful reply.
- Alembic migrations0001–0007; SQLite and native PostgreSQL16.2 preserved-row upgrades.
- Trusted C/C++/Python/JavaScript CLI execution primitives with real exit/output
  results; these are **not safe public sandbox infrastructure**.

## What is not delivered
The API judge contract and dedicated Docker/runsc dispatcher are implemented,
but no actual Docker/runsc execution has been verified. Four foundation projects
have real suites; the original advanced catalog still lacks complete harnesses. Run/submit cannot succeed without these dependencies;
503 is intentional and must not become fake passing grades. Docker/Nginx configuration
has only static evidence, not built/deployed isolation evidence. Native PostgreSQL16.2, Redis8.10.3 and real local STARTTLS mailbox delivery are
integration-tested; production hosts, Internet email and OpenAI are not.

Community/rooms, peer review, leaderboards, coalitions, Piscine, journey/skills/
analytics, Arena, profile/portfolio, hiring and exam screens remain
prototype-gated. Some have real backend records, not complete end-to-end workflows.
Hiring/exam/mentorship backend prototypes require explicit development demo mode;
fixture listings and fake acknowledgements there are not production functionality.

## Run and verify
Follow [INSTALLATION.md](INSTALLATION.md) for dependency installation, private env
setup, migrations, catalog seeding and the two development servers. Defaults disable
judge, AI and demo features. Never commit filled env files.

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements-dev.txt
.venv/bin/alembic -c backend/alembic.ini upgrade head
.venv/bin/pytest backend/tests -q
cd frontend
npm ci
npm run lint
npm test
npm run build
```

Python 3.11 and Node 22.12+ are the verified local toolchain. GCC/G++/Node are needed
for trusted runner tests. Production requires PostgreSQL; SQLite is local/test only.

## Evidence and architecture
- [Feature-by-feature verification matrix](FEATURE_COMPLETION_MATRIX.md)
- [Current status](PROJECT_STATUS.md) · [Engineering report](ENGINEERING_REPORT.md)
- [Architecture](ARCHITECTURE.md) · [Security](SECURITY.md)
- [Readiness / release blockers](PRODUCTION_READINESS.md)
- [Executed verification](docs/VERIFICATION_RESULTS.md)
- [Deployment](DEPLOYMENT.md) · [Troubleshooting](TROUBLESHOOTING.md)

Local evidence: **135 backend/controller tests,35frontend tests; lint/build/audits pass;6actual Chromium tests pass**.
AI-provider integration tests use an HTTP test double. PostgreSQL/Redis/local SMTP
checks use actual services; see [live evidence](docs/LIVE_SERVICE_VERIFICATION.md). These are not production deployment or hostile sandbox verification. Separate actual Chromium journeys and selected axe scans now pass; they are not comprehensive device/accessibility certification.

## New execution and privacy controls
`executor_service/README.md` describes the trusted dedicated worker (no Docker
socket mounted into API/frontend/job containers) and unexecuted hostile harness.
Account Settings now supports real profile/privacy/export/delete/session-revoke
APIs; retention is explicit dry-run/apply. See docs/PRIVACY_RETENTION.md.
After normal catalog setup, optionally seed the four runnable foundation projects:
`PYTHONPATH=backend .venv/bin/python -m app.manage seed-execution-projects`.
Judge remains disabled until actual isolated infrastructure is independently accepted.


## Unified autonomous-checkpoint verification
```sh
bash scripts/setup-testing.sh
bash scripts/validate.sh
```
Basic persisted rooms/reviews/notifications, profile/public portfolio,
Journey/Skills/measured Analytics/opt-in leaderboard/search are now connected.
Monaco and its worker are self-hosted (large lazy chunk warning acknowledged).
Judge authority now runs on the host OUTSIDE minimal non-root job containers;
superseded native UID checks do not prove this boundary. Actual Docker/gVisor remains unverified and
public judging disabled. Full9original grading suites and advanced workflows remain
incomplete coding, not tasks assigned to you. See FEATURE_COMPLETION_MATRIX.md,
USER_ACTION_REQUIRED.md and USER_TESTING_GUIDE.md for precise boundaries.

## Current private-beta checkpoint
- Local regression:206backend/controller,45frontend,9Chromium; lint/build/audit/
  compile checks PASS (see FINAL_ACCEPTANCE_REPORT.md for final result).
- Nine subject-intake templates + fail-closed trusted grader interface; no original
  project grader enabled. No subject invented. Foundation exercises are separate.
- API-backed coalitions now use active-account XP/member totals; single assignment;
  ordinary users cannot create wars. Daily Stream Sum mission uses trusted same-day success and one25XP claim, never simulated.
- Google OIDC/GitHub OAuth+explicit linking implemented, locally tested, real apps
  UNVERIFIED. Schema0007. docs/OAUTH_SETUP.md provides exact console steps.
- Native Linux operator scripts write redacted reports/. Real Docker/runsc/TLS/
  external apps/services and independent review remain required. No public judge.
- Community landing/prototype routes and unavailable product features remain clearly
  marked coming soon; measured missions/badges/reputation and private room moderation
  are implemented under docs/BETA_REWARDS_MODERATION.md; A/V/automatic moderation are not.
Runbooks: INSTALLATION.md, DEPLOYMENT.md, USER_ACTION_REQUIRED.md, USER_TESTING_GUIDE.md.

Windows11 operator setup: WSL2 Ubuntu24.04 + systemd + Docker Engine INSIDE WSL,
Linux-filesystem checkout (not /mnt/c), runsc or disposable Ubuntu VM. Corrected
USER_ACTION_REQUIRED.md / USER_TESTING_GUIDE.md include reports/ and WSL/LAN caveats.
Basic rooms poll5s; report queue10s. Staff removals survive reporter account deletion.
