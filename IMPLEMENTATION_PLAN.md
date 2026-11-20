# Implementation plan

1. Reproduce baseline, inventory source, inspect secrets without disclosure.
2. Remove implicit demo behavior and repair API response unwrapping; protect routes.
3. Secure OTP consumption, configured SMTP, shared production state and logout revocation.
4. Stop simulated judge results; define authenticated remote execution contract. Never execute untrusted code in API process.
5. Add Alembic baseline and incremental auth-state migration, verify fresh and upgrade paths.
6. Replace dashboard activity fabrication with database aggregates; harden infrastructure defaults.
7. Add regression tests, run all available quality gates, report actual limitations.

Full product acceptance additionally requires implementing remaining subsystem workflows,
project-specific executable test suites, browser end-to-end coverage, and validating a deployed
isolated executor, PostgreSQL, Redis, SMTP and AI provider. These are not implied by local tests.

## Reconciliation checkpoint
Completed SQL request limiter, provider review/history, account budgets and real
Mentor screen with tests; reconciled historical docs against code. Next priorities
remain secure per-job execution/catalog suites, real infrastructure verification,
privacy/retention controls, remaining gated workflow integration and browser E2E.
Do not remove gates or mark roadmap phases complete without their acceptance tests.

## Production-engineering checkpoint — 2026-11-18
Implemented dedicated authenticated Docker/runsc dispatcher (runtime unverified),
per-job stdin protocol/limits/cleanup,4foundation suites, privacy/session migration0004,
owner export/delete/revoke/preferences, real Settings UI, retention CLI and log
redaction. Corrected invalid-coalition success and fabricated coalition rank.
119backend/controller+30frontend tests pass, lint/build and refreshed dependency
audits pass. Actual local PostgreSQL migrations/pg_dump-restore/concurrency/privacy,
Redis auth/AOF restart, SMTP STARTTLS/mailbox/API auth checks pass. No Docker/runsc,
OpenAI, Internet mail, full browser E2E or independent production sign-off. Advanced
catalog suites and many original gated workflows remain implementation work.
See ENGINEERING_REPORT.md and PRODUCTION_READINESS.md; mission is NOT complete.
