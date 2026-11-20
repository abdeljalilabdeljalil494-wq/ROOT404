# Implementation progress

## 2026-11-18 baseline
- Clean branch confirmed. Source inventory generated; historical completion reports not trusted.
- Declared Python requirements installed into .venv (system Python is externally managed).
- npm ci completed from frontend lockfile.
- Baseline: backend 53 passed; frontend 14 passed; production build passed.
- Baseline lint failed: eslint is not declared/installed.
- Docker and PostgreSQL command-line tools absent. External network restricted; real SMTP/provider journey cannot be verified here.
- Root .env contains only whitespace; no credentials found there. No secret values copied.

## Implementation and verification
- Repaired implicit frontend mock/fallback and double-unwrapping behavior.
- Wired auth/dashboard/catalog/detail/editor actions, account shell, protected routes,
  logout revocation; unfinished pages are explicit-demo gated, not declared complete.
- Added SQL-backed atomic OTP state/rate limits, SMTP TLS delivery, failure invalidation;
  removed replay bypass. Added verified account enforcement and required token claims.
- Removed judge simulation and CLI fallback. Implemented bounded authenticated
  executor client and actual server-owned output comparison. Executor service absent.
- Replaced C/C++/Python/JS runner simulations with real trusted-program execution.
- Added Alembic frozen baseline/upgrade; data-preserving SQLite migration test.
- Closed seed access, room message membership, repeat project XP/review awards;
  replaced fake activity metrics; production no longer auto-seeds demo users.
- Repaired Dockerfile build ordering/devDependency omission/error masking; hardened
  Compose secrets/ports/profiles. Only YAML/static validation possible here.
- Original dependency audit found vulnerable packages; upgraded/adapted and reran
  tests/build. Current npm and declared Python audits show zero known findings.
- Earlier checkpoint: backend97 passed, no skips. Frontend: 27 passed; lint/build pass after
  clean npm ci. Trusted runner tests are not sandbox isolation tests.
- Added CI (not executed remotely), installation/deployment/troubleshooting and
  explicit feature classifications. Full acceptance remains unsatisfied.

## Verification chronology
- Reinstalled declared Python development requirements into a separate clean venv:
  earlier80 tests passed; reconciliation rerun reached97, no skips.
- Frontend: 27 tests across five files, including Login component request/error/
  verification behavior; lint and production build passed after clean npm ci.
- Started API and Vite on 0.0.0.0. Live HTTP smoke: website root 200, proxied
  /api/health 200, anonymous /api/projects/ 401, backend /ready 200.
  This is not a browser end-to-end or production Nginx test.
- Skill initialization now starts at zero, nested skill updates are explicitly
  persisted, catalog prerequisites enforced on submission, and XP-to-next derives
  from backend thresholds rather than an inconsistent default.

- Added context-specific Docker ignore files to exclude local env secrets, dependencies, caches and database files from image contexts; removed backend apt/build error masking. Container builds remain unexecuted.

## Reconciliation implementation
SQL-shared request budgets and provider-backed review/history/account budgets are
implemented and locally tested. Mentor now uses real API instead of canned replies.
Historical document bodies reconciled; product vision preserved separately. Latest
97 backend/27 frontend tests and lint/build pass. No isolated HTTP executor or
live service verification; product acceptance remains incomplete, not final release.

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

## Autonomous mission continuation — current checkpoint
- Preserved current branch and all existing edits; no commit or push performed.
- Historical in-container UID0 supervisor and native6check identity probe were
  superseded by the host-only design below; they are NOT current isolation evidence.
- Added migration0005/private notifications, owner APIs, read/read-all/export/delete/
  explicit retention, transactionally-created booking/final-review events and UI.
- Connected review publication/booking/detail/human feedback UI; atomic review award
  and per-owner slot serialization. Real PostgreSQL competing operations verified.
- Connected profile/portfolio, Journey/Skills/Analytics, opt-in leaderboard and
  desktop/tablet global search; removed fake metrics in these active views.
- Self-hosted Monaco/worker via pinned monaco-editor dependency; no editor CDN.
  Actual browser loads it and receives honest503 with public judge disabled.
- Added connection-establishment-only AI retry; never replay accepted/read-timeout
  paid requests. Tested with mock HTTP transport, no actual provider call.
- Added unified setup/validation/test/readiness entrypoints and required user guides.
- Current feature status is FEATURE_COMPLETION_MATRIX.md (A/B/C/D/E); original
  grading and remaining advanced workflows are explicitly incomplete engineering.

- Historical pre-critical-redesign comprehensive command `bash scripts/validate.sh` actually passed:
  135backend/controller (4warnings),35frontend/8files, lint/build/npm audit0,
  6actual Chromium tests~1.2minutes, compileall and whitespace. Native real
  infrastructure9checks passed; native fixed identity6checks passed. No Docker/
  provider/deployed/international-device verification is claimed.

## Critical-gate continuation (current)
The trusted `executor_service/host_supervisor.py` runs on the dispatcher host,
OUTSIDE compile/run containers. The job image copies only `launch.py`; learner and
compiler are UID/GID1000 with all capabilities dropped. No supervisor source,
signing key, host IPC, hidden expected outputs or Docker socket is mounted into
jobs. The trusted host necessarily has Docker daemon authority (root-equivalent;
dedicated worker required); this is not permission to expose its socket to learners.

Separate compile/run containers share a unique Docker-managed64MiB tmpfs volume,
not a host bind. Host checks volume driver/options, bounds output, enforces deadlines,
reads terminal Docker State/ExitCode/OOM independently, and removes containers and
volume. Cleanup uncertainty taints the engine. runsc/network-none/read-only root,
cgroup/PID/rlimit limits and no-new-privileges remain mandatory; actual enforcement
is IMPLEMENTED BUT UNVERIFIED here.

HTTPS+bearer authenticates the restricted backend/worker channel. Protocol v2 HMAC
receipts bind fresh request ID, canonical files/language/stdin/limits digest,
timestamp, host observations and result. SQLite transactional claims reject replay
including controller restart; retention is bounded. Backend checks freshness,
request and approved immutable `JUDGE_EXPECTED_IMAGE`, phase/container consistency,
exit/OOM/deadline/output contradictions before trusted hidden-test comparison and
scoring. Sandbox stdout is only untrusted bytes. **A signature authenticates a
receipt; it does NOT attest execution correctness, isolation, kernel integrity or
an honest/uncorrupted host.** Real hostile and independent review remain gates.

- Final `bash scripts/validate.sh`: PASS (`/tmp/root404-critical-final-validation.log`):162 backend/controller tests,4 warnings,15.63s;35 frontend tests in8files; lint/build/npm audit0known vulnerabilities;6 Chromium tests across desktop/tablet/mobile (~1.2min); Python compilation and whitespace PASS.
- External probe command returns five BLOCKED statuses (private configuration absent), exit1; grading inventory returns INCOMPLETE/exit1; production readiness intentionally returns NOT READY/exit1. None counts as external/runtime success.
- Previous actual native PostgreSQL16.2/Redis8.10.3/local certificate-verified STARTTLS:9checks. This is historical local integration evidence, NOT production TLS/provider delivery.
- Dependency audit: previously0known declared Python vulnerabilities; no independent security assurance inferred.
- Real Docker/runsc, provider, production integration and original-project execution: NOT RUN/NOT VERIFIED. No fabricated acceptance.

| Critical gate | Classification | Actual evidence / remaining requirement |
|---|---|---|
| Host-only judge authority and protocol v2 | IMPLEMENTED BUT UNVERIFIED | Host supervisor outside learner containers; local contract tests pass, actual Docker boundary unrun |
| Real Docker/gVisor CI and hostile execution | BLOCKED | Docker/runsc absent here; prepared workflow is NOT execution evidence |
| Original nine project-specific graders | INCOMPLETE | Subjects absent; no approved project harnesses; hard503 prevents generic-suite bypass |
| OpenAI/external SMTP/production PG+Redis/Nginx TLS | BLOCKED | Probe code and mocked negative tests exist; no authorized live configuration or target verification |
| Independent security assessment | BLOCKED | Engineering negative tests/source review only; independent reviewer/staging required |
| Local quality regression | VERIFIED | Local unit/API/component/browser boundaries only, not release authorization |

## Private beta continuation — item 1
Inspected catalog/READMEs/project definitions/docs. Added nine explicit subject
intake templates and fail-closed typed trusted-grader extension boundary, no dynamic
imports or automatic activation. No authoritative original subject exists in the
repository; nine actual graders remain INCOMPLETE, not fabricated. Added negative
registration and scoring validation tests. Public judge remains disabled.

## Private beta continuation — workflow/OAuth work in progress
Item1 full validate PASS (176 backend/controller,35frontend,6Chromium plus
lint/build/audit/compile/whitespace). Added report wrapper preserving actual exit
codes and redacting configured credentials into ignored reports/.
Coalition UI now uses real account-derived totals; assignment single-winner and
non-switchable; war creation admin-only. Repeated streak reads now derive distinct
owner submission dates and cannot increment stored counters. Suggestions explicitly
coming_soon and award0XP. No claim of completed executable Daily Missions.
Added Google OIDC/GitHub authorization-code flows, fixed endpoints, PKCE, one-use
browser-bound state, verified emails, signature/issuer/audience/nonce checks,
explicit authenticated recent-session linking (never email auto-link), schema0006,
frontend callback and entrypoints. Local provider-double tests only; real apps UNVERIFIED.
Workflow/OAuth full validate PASS:183backend/controller (4warnings),39frontend,
6Chromium; lint/build/audit/compile/whitespace. Report:reports/validate.log/json.
Added direct RSA-signed Google token claim negatives and GitHub unverified-email
negative; these remain mocked network/provider evidence, not live OAuth signoff.

## Private beta — runtime/integrations/frontend/deployment checkpoint
Expanded actual Chromium journey to register→OTP→dashboard→project→editor→submit503
and unchanged XP, plus coalition axe scan at three viewports:9browser tests pass.
No successful isolated evaluation/XP is claimed. Prior full run191backend,39frontend,
9Chromium/lint/build/audit/compile/whitespace PASS. Added further award-input,
report-redaction, OAuth config and export/deletion tests; final suite rerun follows.
Actual native PG schema0006 migration/data-preservation/API/race checks, Redis and
verified local STARTTLS all passed again (9checks). Not production/external evidence.
Added one-command Linux judge acceptance with runtime/artifact reporting, config
checker, stack health probe, explicit migration dependency, bounded Docker logs,
TLS override, sensitive backup and fresh-DB restore drill scripts. These Docker/
Nginx/restore paths are IMPLEMENTED BUT UNVERIFIED here (Docker absent).
External probes automatically join validation only with explicit operator opt-in;
mail/paid calls never run merely because a credential happens to be present.
Rewrote native Linux user runbooks and exact Google/GitHub console instructions.
Final private-beta validation after room abuse limits and all current source changes:
195backend/controller (4warnings),39frontend/10files,9Chromium (~1.6min), lint/build/
npm audit0/compile/whitespace PASS; reports/validate.log/json. Shell syntax PASS.
No Docker, external provider or real OAuth success is inferred. Entire requested
mission is NOT claimed complete: remaining INCOMPLETE engineering explicitly in
FEATURE_COMPLETION_MATRIX.md/FINAL_ACCEPTANCE_REPORT.md. Public judge stays disabled.

Final OIDC self-review additionally rejects multi-audience tokens lacking azp,
wrong authorized party and mismatched at_hash (direct signed-token regressions).
Latest complete validate PASS:198backend/controller (4warnings),39frontend,
9Chromium (~1.5min), lint/build/npm audit0/compile/whitespace. reports/validate.*
is current. Earlier counts above are historical checkpoints, not latest totals.

## Next development round — Windows11 correction and implemented beta policies
- External SECURITY_REVIEW_INDEPENDENT.md / SECURITY_REVIEW_JUDGE.md absent. Logged
  intake without fabricating findings; BUGS_AND_FIXES distinguishes self-review fixes.
- Added schema0007 durable daily claims/private reports/message removal marker.
  Executable mission reuses supplied Stream Sum Python spec and existing trusted
  submission pipeline; unique UTC daily25XP award, own/success/day checks, replay
  and concurrent claims. Public judge stays disabled; no successful execution faked.
- Added computed four-badge catalog criteria and transparent capped reputation;
  distinct peer/self exclusion/no repeated-read XP. UI/analytics/portfolio connected.
- Member-only reporting/private owner+admin paginated queue; non-conflicted admin
  CAS remove/dismiss; removed content hidden across history/detail. High self-review
  fix ensures reporter deletion cannot restore removed message or erase sanction.
  Export hides reviewer identifier. Operator-only admin role helper/wrapper added.
- Visible-tab room5s/queue10s non-overlapping polling/unmount cleanup; no A/V/presence.
- Browser now exercises member reporting→private queue→separate staff UI removal and
  disappeared content at three viewports, plus prior registration/disabled-submit.
- Wrote Windows11/WSL2 Ubuntu24.04 systemd/Engine-inside-WSL/runsc instructions; Linux
  filesystem checkout, no Docker Desktop/Microsoft drive workspace, VM fallback and
  scoped Windows LAN/TLS guidance. WSL installation itself UNVERIFIED here.
- Native actual PG schema0007 fresh/incremental/restore/API checks and parallel daily
  claim: one of4wins, +25XP once; total10checks incl Redis/local verified STARTTLS.
- No original specifications found; all nine templates clear, hard gates unchanged;
  grading inventory INCOMPLETE/exit1. No commit/push/real.env read or modification.

Final current full validate PASS:206backend/controller (4warnings),45frontend/13files,
9actual Chromium (~1.8min), lint/build/npm audit0/compile/whitespace. reports/validate.*
(/tmp/root404-next-final2.log). Earlier checkpoints are historical. Final native
schema0007 checks10PASS, not Docker/WSL/external production proof.
