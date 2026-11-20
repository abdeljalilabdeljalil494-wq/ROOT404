# Executed verification — 2026-11-18

## Current production-engineering checkpoint
| Command / operation | Actual result |
|---|---|
| Declared backend/controller/integration requirements installation | Passed in verification venv before interpreting tests |
| `.cache/verification-venv/bin/python -m pytest backend/tests executor_service/tests -q` |119passed,4warnings,no skips;113backend+6controller;15.21s |
| `cd frontend && npm run lint` | Passed |
| `cd frontend && npm test` |30passed across6files |
| `cd frontend && npm run build` | Passed |
| `cd frontend && npm audit --audit-level=moderate` |0known vulnerabilities |
| `pip-audit -r backend/requirements.txt -r executor_service/requirements.txt` |No known vulnerabilities found |
| `scripts/verify_infrastructure.py` with explicit disposable local PG admin DSN |8real-service checks pass; see LIVE_SERVICE_VERIFICATION.md |
| Real Redis stop/restart then authenticated read |AOF restored expected key; then removed |
| `python -m compileall -q executor_service scripts backend/app judge_sandbox/job.py` |Passed |
| Compose YAML/static isolation/default-disabled assertions |Passed; not Docker runtime |
| Reconciled local documentation links and `git diff --check` |Passed |
| `docker version` |FAILED/blocked:command absent,exit127 |
| `scripts/verify_executor.py` |NOT RUN; approved Docker/runsc/TLS worker absent |
| Live OpenAI |NOT RUN; no approved credentials/egress |
| Internet SMTP recipient |NOT RUN; actual local mailbox only |
| Browser/mobile/accessibility/deployed Nginx E2E |NOT RUN |

## What the tests prove (and do not)
- Executor6tests prove HTTP auth/admission/strict validation, bounded concurrent
  calls, fixed Docker policy argv, immutable-image/runtime/seccomp/cgroup preflight
  and failure behavior using a fake engine. They do not launch a container.
- Grading tests run real trusted C/C++/Python/JavaScript reference/wrong programs
  and validate foundation boundaries. Local loops/resource tests are trusted,
  limited process tests, not hostile sandbox security evidence.
- Account tests verify private defaults, bounded export ownership, confirmation/
  recent-auth, revocation, deletion cascade and preserved other-user access.
- Provider tests use HTTP MockTransport, never a paid/live provider. No scripted
  outage fallback or random quality grade is accepted.
- Native PostgreSQL16.2 tests are separate from backend/tests/conftest.py (which
  intentionally selects SQLite). Production-config startup checks Alembic head.
  Actual STARTTLS/server/mailbox/API flow is separate from SMTP transport doubles.
- Native services are lab infrastructure, not the approved patched production
  versions, Compose deployment or independent security sign-off.

## Evidence provenance / failures repaired
Original baseline53backend/14frontend passed despite missing integrations; later
accepted baseline97/27. Current119/30 supersedes those counts. New suite cases
initially exceeded the10KiB stdin cap; adjusted boundary inputs while retaining
64-bit sum and1000-element coverage. Local PostgreSQL provisioning initially used
SQL_ASCII; verifier now explicitly provisions UTF8. Reserved .test email was
rejected by EmailStr; local nonrelay mailbox accepts example.com for API flow.
All repaired and rerun; no failing assertion was converted to a skipped test.

Ephemeral logs (not committed): `/tmp/root404-phase-final-tests.log`,
`/tmp/root404-phase-frontend-final.log`, `/tmp/root404-phase-build-final.log`,
`/tmp/root404-real-infrastructure-final.log`, `/tmp/root404-phase-pip-audit.log`.
No raw mail, private credentials, binary toolchains or datasets are tracked.
