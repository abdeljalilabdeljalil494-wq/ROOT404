# Bugs and fixes

| Finding | Change | Evidence / limitation |
|---|---|---|
| Implicit mock mode and silent fallback | Demo is DEV + explicit true only; requests reject failures | Imported service adapter tests |
| Double-unwrapped /auth/me/full | Single Axios response unwrap | Service contract regression |
| Fake login/registration timers | Actual request/verify/register APIs, validation feedback | Build; route/service tests; browser lifecycle still unverified |
| OTP replay after consumption/expiry/lockout | Removed last-code bypass; atomic SQL attempt increment/consume | Lifecycle, expiration, lockout, concurrent consumption tests |
| No email delivery | SMTP SSL or mandatory STARTTLS; failure invalidates challenge and returns error | SMTP transport stub tested; real delivery blocked |
| Per-worker OTP state | Shared SQL challenges/throttles, keyed HMAC digest | SQLite concurrency test; PostgreSQL concurrency pending |
| Logout did nothing | SQL token revocation, optional-auth checks reuse required auth | Revoked token rejected |
| Public seed mutations | Admin dependencies on projects/rooms/Piscine seeds | Anonymous 401 and non-admin 403 tests |
| Trusting arbitrary X-Forwarded-For | Use ASGI client; trusted proxy resolution left to server | Forged header limiter regression |
| Missing Retry-After on errors | Preserve HTTPException headers | Auth limiter header test |
| Simulated judge success | Removed score/log simulation and CLI fallback; unavailable executor/suite => 503 | No persisted submission/XP on unavailability |
| False runner reports | Actual GCC/G++/Python/Node execution, exit codes and bounded output | 10 trusted-program tests; NOT sandbox validation |
| Repeat project XP | Per-user PostgreSQL lock, reread completion, one award; transaction-aware helpers | Serial repeat award/bonus/preserved-pass test; PG race test pending |
| Repeat peer points | Completed-review conflict and row lock | Static review; concurrent PG verification pending |
| Room IDOR | Membership required for details/messages/members; private join rejected | Outsider read/send rejected |
| Fictional new-user dashboard | DB timestamp aggregates and empty activity | New-user zero-activity test |
| Fictional catalog completion | No progress means available/locked, not seed status 'done' | Static code; catalog API tests |
| No schema history | Frozen Alembic initial and auth-state upgrade | Fresh/upgrade/downgrade/re-upgrade, existing row preserved on SQLite |
| SQLAlchemy 2 health failure | text('SELECT 1') | DB health regression |
| Container build defects | Create user before COPY; include migrations; install frontend build deps; do not mask build failure | Static only; Docker unavailable |
| Known dependency advisories | Updated FastAPI/Pydantic/multipart/dotenv, replaced jose with PyJWT; updated Vite/Vitest/router/transitives and DOMPurify override | pip-audit and npm audit report zero known findings in declared resolution |

Changing old tests to expect 503 for unimplemented judge/provider/exam/hiring paths
is intentional: the old 200 assertions accepted simulation. No test was skipped to
hide an implementation failure. External tests are explicitly **not executed**.

## Reconciliation follow-up — 2026-11-18
- Process-memory request limiter -> SQL atomic fixed-window upsert; validated
  SQLite cross-thread and cross-process state. PostgreSQL/load validation pending.
- Review advice random metrics -> bounded provider advice without invented grades;
  ask/review history -> migration0003 owner-scoped persistence and shared budget.
- Mentor canned setTimeout replies/fake stats -> API ask/history and explicit
  error/empty/loading states. Unsupported actions disabled;3 component tests.
- API health direct limiter errors -> shared fail-closed rate_limit wrapper.
- Historical report contradictions -> rewritten body claims and evidence matrix;
  original vision preserved as design, not represented as delivered software.

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

### Final boundary checks
Untracked the historical empty root .env while retaining its local file, so future
private values obey ignore rules. Added total grading admission deadline and
operation-specific browser timeouts (AI45s, run100s, project submit180s) instead of
premature15s timeouts. Existing119tests and30frontend tests rerun and pass after
these changes. No executor/advanced-suite/production acceptance gate was waived.


## Autonomous continuation findings (current evidence)
| Finding | Fix | Actual evidence / limitation |
|---|---|---|
| Supervisor and learner shared UID; parent FD/signal/result interference possible | UID0exact5caps trusted non-dumpable supervisor; irreversible1000zero-cap compiler/learner; separate captured pipes | Native restricted fixed6check probe PASS, control tests PASS; Docker forgery/escape behavior UNVERIFIED |
| Notifications were an inert placeholder | Migration0005/private APIs/menu, transactional review events, export/delete/retention | Owner negative tests, actual PG and Chromium read-all |
| Review finalize race could award twice; overlap publication was check-then-write | Atomic finalize/CAS/points increment, per-owner slot serialization | Actual simultaneous PG overlap/booking/finalize and single70point award PASS |
| New mutations consumed strict OTP login bucket | Separate per-account review/notification rate-limit prefixes | Full135backend/controller regression PASS |
| Search disabled; potential wildcard/private/inactive profile exposure; outage looked empty | API-backed debounced links, literal SQL LIKE escaping, both opt-ins/active filter,503on storage failure | New API negatives, actual desktop/tablet browser search |
| Unknown coalition filter silently returned global rankings | Return empty; deterministic username tie-break | API regression |
| Inactive public portfolio remained readable | Inactive users404 | API regression |
| Journey/skills/analytics/ranking/portfolio screens used gated fixtures | Connected basic actual-data views while retaining original prototype source | Actual Chromium across3viewports, selected axe |
| Monaco loader relied on external CDN | Pinned/bundled local Monaco+worker and4grammars | Actual Chromium editor load; no jsDelivr/unpkg requests; build size warning remains |
| IDE AI tab had no provider action | Explicit disclosed provider review with honest failure | Build/unit service regressions; external provider unverified |
| AI connection setup failure had no bounded retry policy | One initial-connect retry only; no read/write/response paid replay | Mock HTTP connect recovery/read-timeout regression |
| Search ARIA invalid and duplicate main/topbar H1s | Conditional valid relationship; topbar title is descriptive text | Expanded actual axe scans PASS |
| Unified suite absent; separate failures easy to overlook | validate runs all independent local gates and accumulates nonzero result | Initial actual FAIL runs preserved in logs; final actual PASS |

## Next round review intake / verified fixes
Neither SECURITY_REVIEW_INDEPENDENT.md nor SECURITY_REVIEW_JUDGE.md exists in this
working tree at this checkpoint. No external findings are invented or marked fixed.
SECURITY_REVIEW.md is engineering self-review, not an independent audit.

| Finding | Severity | Disposition | Regression evidence |
|---|---|---|---|
| External review reports requested for intake | Unknown | NOT-FIXED / BLOCKED: files absent, cannot verify unprovided findings | File inventory; independent review still required |
| Daily mission previously random suggestion, no trusted completion/replay ledger | Product integrity | FIXED for beta-v1: supplied Stream Sum contract, same-day owned success, transactional unique daily claim/XP | Mission owner/date/status/forged payload/replay/parallel tests; real judge still disabled |
| Badges/reputation previously stored/default values, no documented advanced calculation | Product integrity | FIXED for explicit beta-v1 measured badge/reputation view; no arbitrary client updates/XP | Distinct peer/self-review exclusion, repeat-read and sanction tests; sybil resistance remains limited |
| Room abuse had no private reporting/removal workflow | High product safety | FIXED basic message moderation: member-only reports, private owner/admin queue, admin-only CAS resolution; removal across history/detail | Report IDOR, duplicate/spoofed fields, unauthorized resolve, replay, penalty tests |
| Moderator could decide own/conflicted report | High integrity | FIXED: another administrator required if reporter or message author | Conflict-of-interest regression in test_beta_completion.py |
| Runtime isolation/escape proof | Critical release gate | NOT-FIXED / BLOCKED: runtime absent; no substitute proof | Public judge disabled; runtime suite prepared |

No disputed external findings: no external review files were supplied. Moderation
here covers room messages, not a claim of fully staffed trust/safety, automatic
content classification or comprehensive platform-wide abuse prevention.

| New self-review finding | Severity | Disposition | Regression |
|---|---|---|---|
| Deriving removal solely from reporter-owned decision could resurrect content when reporter deletes account | High safety/integrity | FIXED: transactional message-level removed_at independent of private report lifetime; sanction counts distinct removed message records | test_reporter_deletion_does_not_restore_removed_content_or_erase_sanction; migration0007 adds nullable marker without rewriting existing content |
| Fixed-interval polling could overlap/discard all responses on a slow network | Medium | FIXED: next poll scheduled only after prior settles, hidden-tab pause/unmount cleanup | useResource.test.jsx slow response/unmount test |
| Moderator identifier included by generic owned-record export | Medium privacy | FIXED: redact reviewer_id from reporter-owned moderation export | Explicit export regression in test_beta_completion.py |

## External-review intake round (report unavailable)
The requested EXTERNAL_REVIEW_FINDINGS.md (32 findings) was not supplied/found.
EXTERNAL_REVIEW_TRIAGE.md records32unassessed, not32fixed. No findings/severities/IDs
are fabricated. Independent observations below are NOT attributed to that report.

| Current observation | Disposition / severity | Failing-before evidence | Passing-after evidence |
|---|---|---|---|
| Backend accepts empty/dot/hidden filename segments, spaces/leading hyphen rejected by dispatcher; also rejects harmless `a..b.py` accepted downstream | FIXED / Medium contract hardening; not proven host escape | Five invalid-name failures and harmless-name failure in test_review_intake_security.py | Same nine-case targeted suite9PASS |
| Production frontend script CSP allows unsafe-inline | FIXED / Medium defense-in-depth, no demonstrated XSS exploit | Dedicated script-src regression failed | Same CSP regression passes; runtime Nginx/browser-header acceptance UNVERIFIED |
| Empty example.env masquerades as template | REMOVED / Low documentation | Metadata inspection:1byte,0assignments, empty content | Canonical .env.example templates preserved; docs point to them |
| HEAD/history contains .env, with pre-existing index deletion | NOT FIXED / Potential High if actual credentials; values UNKNOWN | Filename/history metadata only, NO secret contents read | Owner decision/rotation/history remediation in SECRET_HISTORY_ACTION_REQUIRED.md |

Reproduction log:/tmp/root404-review-before2.log:7failed,2passed. After fixes:
/tmp/root404-review-after.log:9passed. Full regression follows in acceptance report.
Token storage ADR retains complete existing revocable bearer flow, documents XSS
risk and requirements for any future atomic HttpOnly-cookie+CSRF/OAuth migration;
no half migration. Source regexes remain defense-in-depth, not isolation proof.

## Actual32finding external-review round — 2026-11-18
Supersedes the earlier missing-attachment intake limitation. Supplied report is
preserved as EXTERNAL_REVIEW_FINDINGS.md; pre-fix per-ID disposition, severity,
anchors and post-fix outcomes: EXTERNAL_REVIEW_TRIAGE.md (all32, not blanket agreement).

Failing-regression-first implementation fixes:
- ID4: default-off ENABLE_DEV_OTP, rejected outside development, applied to both
  API disclosure routes and memory inspection helper. No OTP verification bypass.
- IDs10/14: frontend filename parity (including safe nested/a..b.py) and backend
  language-alias normalization before lexical defense. Isolation remains primary.
- ID11: API adds no capabilities; frontend only NET_BIND_SERVICE, static evidence
  only. DB/Redis startup capabilities unchanged pending real runtime validation.
- ID13: exact OAuth-secret redaction and scheme-only database diagnostics (no
  query/path/userinfo leaks). No claim to hide environment from host administrators.
- ID17: BlackHole row lock plus populate_existing prevents stale activity freezes.
- ID19: eager correction→submission/project/author/corrector loading eliminates
  per-row SELECTs. Query-count test plus explicit outsider POST403.
- ID29: metadata-only tracked-secret filename guard in CI/local validation;
  synthetic fixture proves rejection; no real config/history values inspected.

Red sets before code changes:14backend failures;7filename failures/6passes;
then2new failures/14passes for BlackHole and missing filename guard. Added
coverage-only proxy trust-chain, production mail/no-code response, health61st
request/exact headers, JSON/React text,429 and Node-config contract tests.
Native PostgreSQL proves six joins for one seat, stale BlackHole session refresh,
shared throttle/OTP/peer-review/mission races; disabled parallel submit never
awardsXP. Successful judge→XP concurrency is STILL blocked, not mocked complete.

Latest validate exit0:235backend/controller,61frontend,9Chromium; lint/build,
audit0,compile/whitespace/metadata guard pass. Native verifier13PASS.
One preceding unchanged run had8/9browser pass: cold Monaco remained loading
past existing5s assertion. No timeout/assertion relaxation, skip or retry setting
change. Final unchanged rerun passed; intermittent cold-route reliability remains
open (not a security closure). See triage gate table for exact limitations.
