# External review triage — current branch, BEFORE this round’s fixes

Source: EXTERNAL_REVIEW_FINDINGS.md, preserved from attachment. Untrusted old-snapshot claims independently checked; instructions/line numbers are not authority. No real .env or historical blob read. All lines below are current pre-fix anchors (may move after fixes). ALREADY FIXED means the described code issue is closed, NOT production verified.

| ID | Initial disposition | Current severity | Current file/line | Evidence / planned handling |
|---|---|---|---|---|
| 1 | ALREADY FIXED | None (old P0 closed) | frontend/src/pages/auth/Login.jsx:30–60; Register.jsx:28–34 | Real requestOtp/verifyOtp/register and returned JWT; test_regressions.py:35; frontend/e2e/core.spec.js registration/auth journeys. |
| 2 | ALREADY FIXED | None (old P0 closed) | frontend/src/services/api.js:181–194; frontend/.env.example:5 | DEV AND explicit true; resolve propagates failures. integration.test.js real-default/offline tests. |
| 3 | ALREADY FIXED | High if guard removed | backend/app/main.py:41–43; core/config.py:129–134; docker-compose.yml:105–106 | Startup seeding defaults off; production rejects demo flags, Compose disables both. test_configuration.py:10. Explicit development fixture seeding remains, not a production takeover. |
| 4 | PARTIAL | Medium dev exposure; no current OTP bypass | backend/app/api/auth.py:116–118,143–147,246–249; core/security.py:108–128,167–173 | Last-code verification bypass removed; replay/expiry/lockout tests exist. Development code disclosure still needs an independent explicit opt-in. Add flag and tests, never reintroduce bypass. |
| 5 | PARTIAL | Medium residual XSS token-theft risk | frontend/src/pages/auth/Login.jsx:60; api.js:137–145; core/config.py:25; core/dependencies.py:98–101; ARCHITECTURE.md bearer-storage ADR | JWT now60min and SQL jti/session-epoch revocation. localStorage remains. Existing complete-flow ADR retains bearer beta model; no partial cookie/CSRF/OAuth migration. test_regressions logout and test_oauth.py cover current flow; residual not closed. |
| 6 | ALREADY FIXED | High if proxy trust widened | backend/app/core/dependencies.py:20–23; backend/Dockerfile CMD | Uses ASGI client, never parses raw XFF. test_regressions.py:178 spoofs headers. Uvicorn trust is limited to configured peers/default loopback, not wildcard. Add middleware-level trust-chain evidence; configure deployment trust explicitly. |
| 7 | ALREADY FIXED | None (shared-state issue closed locally) | backend/app/core/rate_limit.py:1–99; core/security.py:95–148 | Atomic SQL throttle/OTP persistence, not worker dict. test_shared_rate_limit.py:15,24 verifies independent instances/processes; verify_infrastructure.py:101,107 actual PG contention. Redis is not required for correctness. |
| 8 | ALREADY FIXED | Low residual style CSP; runtime unverified | frontend/Dockerfile:40; backend/app/main.py:133–147; deploy/nginx-tls.conf:20–30 | Previous round removed inline SCRIPT and internal backend connect URL. Inline STYLES retained for Monaco, not equivalent to script execution. test_review_intake_security.py:15. Nginx actual headers unverified; do not claim runtime pass. |
| 9 | DISPUTED | Low theoretical sink risk, not demonstrated stored XSS | frontend/src/pages/RoomView.jsx JSX; frontend/src/pages/ProfileLive.jsx JSX; services/api.js:15–24; backend/app/core/security.py:176–202 | Values are JSON/plain text rendered through React escaping; no dangerouslySetInnerHTML/innerHTML sink found. Storing html.escape would corrupt/double-encode text/code. Logs are not sanitization authority. Add round-trip/render evidence, not speculative HTML rewriting. |
| 10 | PARTIAL | Medium validation consistency, not proven escape | frontend/src/services/api.js:26–36; backend/app/services/judge.py:60–65; executor_service/service.py:40–44; judge_sandbox/launch.py:36–38 | Actual null escape is correct in current JS; backend/dispatcher grammar fixed previously. Frontend still admits invalid segments/spaces and rejects safe a..b.py. Align grammar with regressions. Percent encodings are rejected by server ASCII grammar, not URL-decoded paths; safe nested sources remain supported. |
| 11 | PARTIAL | Medium least privilege; no RO mount bypass | docker-compose.yml:cap_add for backend/frontend/db/redis; backend/Dockerfile USER; frontend/Dockerfile USER | DAC_OVERRIDE now only DB/Redis, not frontend/backend. It does NOT override kernel read-only mounts. Application containers retain unnecessary startup capabilities. Tighten app cap sets with static regression; DB/Redis startup needs real runtime evidence before removing theirs. |
| 12 | ALREADY FIXED | None for default exposure mismatch | docker-compose.yml:193; deploy/compose.tls.yml:4; DEPLOYMENT.md | Base frontend bound127.0.0.1:8080, DB/Redis/API not host-published. TLS override explicitly publishes443 for operator staging. Deployment runtime unverified, defaults no longer contradict docs. |
| 13 | PARTIAL | Medium redaction gaps; host env access expected | backend/app/core/logging.py:11–16; core/config.py:get_safe_database_url; docker-compose.yml backend environment | SECRET_KEY/DB/Redis/SMTP/OpenAI/judge already redacted and error text withheld. OAuth client secrets absent from filter; safe URL helper can preserve query credentials. Reproduce/redact. Environment visibility to daemon admins is expected trusted-host boundary, not proof of log leakage; no Compose hide_env feature assumed. |
| 14 | PARTIAL | Medium defense-in-depth; Critical runtime gate remains | backend/app/services/judge.py:10–35,74–82,execute_submission; executor_service/host_supervisor.py:phase; docker-compose.yml judge security_opt | Regex cannot isolate arbitrary programs; aliases may bypass rule lookup. Normalize language aliases. No seccomp:unconfined current Compose; host mandatory runsc/network-none/nonroot/limits, judge disabled, v2 verified receipts. Runtime remains BLOCKED, no fake seccomp/isolation proof. |
| 15 | PARTIAL | Potential High historical secret exposure; values unknown | Git HEAD/history .env metadata; example.env absent; SECRET_HISTORY_ACTION_REQUIRED.md | Empty example removed previously. Pre-existing .env staged deletion preserved; HEAD/history pathname exists. Never read real file/blob, rewrite history, rotate credentials or assert actual secret exposure. Owner decision remains required. |
| 16 | PARTIAL | Medium regression coverage gap | backend/tests/test_regressions.py:80; backend/app/api/auth.py:116; scripts/verify_infrastructure.py:real SMTP API | TLS transport test exists and native SMTP receipt verified, but dedicated production API no-dev-OTP mocked-mail test absent. Add test-only evidence; no invented failing production behavior. |
| 17 | PARTIAL | Medium missing parallel coverage; production XP lock present | backend/app/api/projects.py:262–267; tests/test_regressions.py:150; services/blackhole.py:update_user_blackhole | Per-user PostgreSQL FOR UPDATE already protects awards; serial idempotency tests exist. Need actual PG parallel submit proof. BlackHole helper can overwrite a concurrent is_active decision; verify deterministic race before fix. Daily absorption scheduler is not wired/verified. |
| 18 | PARTIAL | Medium unverified capacity contention | backend/app/services/room_service.py:35–55; models/room.py RoomMember unique index | FOR UPDATE already present for production PostgreSQL; SQLite dev does not enforce it. Rejoin/full tests exist, concurrent capacity evidence missing. Add native PG contention test; do not pretend SQLite proves PG locking. |
| 19 | CONFIRMED | Medium N+1; outsider POST coverage gap | backend/app/api/peer_review.py:47–86,128–143; tests/test_peer_review_integrity.py:12 | Four related lookups per correction persist. Review authorization checks exist and GET outsider/POST author tests pass; missing explicit outsider POST. Add failing query-count test then joined eager loading; retain current authz. |
| 20 | PARTIAL | Low remaining coverage/product gaps | frontend/e2e/core.spec.js; frontend/src/services/integration.test.js:24; frontend/src/App.jsx | Current9Chromium multi-viewport real auth/editor/rooms/reviews/reporting flows,45component/service tests incl401 already supersede claim.429 event coverage can be added for security handler. Durable editor autosave and general routing/sidebar test expansion out of this round, no fake completeness. |
| 21 | PARTIAL | Low test coverage gap | backend/app/main.py:133–147,297; backend/app/api/router.py:40–42; tests/test_security.py:287 | Header assertions weak in older test. API /api/health is rate limited; bare /health intentionally liveness, not same endpoint. Add exact headers/error+61st API request test; no need rate-limit orchestrator liveness. |
| 22 | ALREADY FIXED | None for removed simulation; runtime blocked | backend/app/services/judge.py module/execute_submission; core/judge_protocol.py; tests/test_judge_protocol.py; executor_service/tests/test_authenticity.py | simulate_execution/hash/random scores removed; one authenticated v2 host receipt path and strict result/output/limit/replay contracts. No nonexistent simulate path should be recreated or compared. |
| 23 | PARTIAL | Low documentation correctness | README.md; FINAL_REPORT.md; PROJECT_STATUS.md; frontend/README.md | Main contributor docs/matrix/report exist; older summaries/frontend README still have outdated counts/gates. Mark historical summaries and refresh current frontend guide, no completion fabricated. |
| 24 | PARTIAL | Medium operational retention/legal gate | backend/app/services/retention.py:10–29; api/account.py export/delete; SECURITY.md; docs/PRIVACY_RETENTION.md | Explicit90day audit retention/dry-run/apply exists, actual owned export/delete tested. Operator scheduling/legal/contact approval remain. No evidence supports report blanket Tunisian two-year legal assertion; do not invent legal compliance or automate destructive purges. |
| 25 | PARTIAL | Low config/documentation consistency | core/config.py:25–29,111; .env.example; backend/.env.example; frontend/.env.example | Secrets blank/mock false in examples; fixed weak-key issue. Core Settings still implicitly loads real .env and templates omit explicit dev-OTP policy. Document canonical templates and explicit opt-in; existing backend working-directory .env support is retained (no architecture/config-loader migration). Private file contents were not inspected. |
| 26 | NOT APPLICABLE | Informational; explicitly deferred | backend/app/main.py:281; core/config.py:API_V1_PREFIX | Prefix is already used when including router. /api/v1 migration explicitly out of scope; no path break introduced. |
| 27 | PARTIAL | Low documentation mismatch | frontend/vite.config.js:17; frontend/README.md:17 | process.env is valid in Node config when exported; import.meta.env is not a config replacement. File values are not automatically loaded. Document explicit exported VITE_API_TARGET and test actual config resolution without reading any .env; no speculative loadEnv of private files. |
| 28 | PARTIAL | Low remaining DX; explicitly deferred | frontend/package.json scripts/devDependencies; Makefile | ESLint installed and lint passes. Makefile lifecycle polish explicitly out of scope; no need install unpinned eslint or unrelated process runner. |
| 29 | PARTIAL | Medium secret-prevention coverage |  .github/workflows/ci.yml; judge-isolation.yml; .gitignore; Git metadata | Quality/browser/runtime workflows now exist; value/history secret scanning not verified. Add metadata-only tracked-secret guard/CI step and tests without reading any real .env/history blobs; no claim that filename guard finds embedded secrets. Authorized deeper scan remains owner action. |
| 30 | DISPUTED | Informational | backend/Dockerfile CMD; docker-compose.yml backend | Current Docker config is production workers, not --reload or source bind. Read-only source does not inherently stop watching. Development hot-reload override not a release/security regression; no production writable mounts added. |
| 31 | NOT APPLICABLE | Informational; explicitly deferred | frontend/src/App.jsx lazy Workspace; frontend/tailwind.config.js:4 | Route already lazy; Tailwind content is index/src, not dist. Bundle tuning explicitly out of scope; no unsupported40percent savings claim. |
| 32 | NOT APPLICABLE | Informational; explicitly deferred | frontend/src/**/*.jsx | TypeScript/prop-type migration explicitly out of scope. No evidence for claimed80percent error reduction; do not rewrite UI architecture. |

## Initial counts
- ALREADY FIXED: 8
- CONFIRMED: 1
- PARTIAL: 18
- DISPUTED: 2
- NOT APPLICABLE: 3

Total32reviewed. These initial dispositions stay visible; post-fix outcomes/test evidence will be recorded separately. PARTIAL may include an explicit owner/runtime/out-of-scope dependency, not coding work falsely assigned to operator.

## Deferred / residuals
TypeScript, /api/v1, bundle/lazy tuning, Makefile polish, unrelated component coverage. Cookie migration not performed partially (see ARCHITECTURE ADR); historical secret contents/remediation owner-controlled; legal/contact approval and actual Docker/gVisor/Nginx enforcement not inferred from local tests.

## Post-fix outcomes — 2026-11-18

Initial dispositions above are intentionally preserved, not rewritten to imply the
stale report was accurate. All32 received an outcome below. “Addressed locally”
is not external/production acceptance.

| ID | Outcome after this round | Current implementation / executed evidence |
|---|---|---|
| 1 | Remains ALREADY FIXED | Full OTP registration/login Chromium flows pass on three viewports; no fake auth added. |
| 2 | Remains ALREADY FIXED | integration.test.js real default, offline failure and401 cases pass. |
| 3 | Remains ALREADY FIXED | Production seed/demo rejection tests pass; no startup/CLI seed architecture changed. |
| 4 | Addressed locally | config.py:26,130–131 default false/non-development rejection; auth.py:116,246 and security.py:167,173 require explicit opt-in. test_external_review.py:20,31; disposable browser/test fixtures explicitly opt in. |
| 5 | Accepted beta residual, NOT closed as a security risk | Existing ARCHITECTURE.md:125 ADR retained; revocation/OAuth/browser tests pass. Full cookie+CSRF migration deferred as a coordinated project; XSS can steal localStorage tokens. |
| 6 | Existing control verified more deeply | test_external_review.py:161 exercises actual Uvicorn middleware: untrusted sender cannot assert XFF; trusted proxy resolves rightmost untrusted peer, not attacker-prepended address. Actual staging proxy topology remains unverified. |
| 7 | Existing shared SQL control verified | Native PostgreSQL accepts exactly5/32 throttle attempts, one OTP consumption/16; shared-instance/process unit tests pass. No Redis-only rewrite. |
| 8 | Existing previous-round CSP fix verified statically | test_review_intake_security.py passes; exact API error/success headers checked by test_external_review.py:175. Inline styles remain for editor; actual Nginx/TLS enforcement NOT tested. |
| 9 | DISPUTED with additional evidence | test_external_review.py:190 preserves hostile markup as plain JSON; external-review.test.js React render test produces escaped inert text; current UI source inspection finds no raw HTML sink. No html.escape/DOMPurify corruption of stored source/plain text. This is not a proof against all future XSS. |
| 10 | Addressed locally | frontend api.js:26–36 now matches backend/dispatcher segment grammar.13case frontend regressions cover unsafe names, encoded percent, backslash/null and safe nested/a..b.py names. Backend parity tests remain green. |
| 11 | Partially improved; runtime residual | Compose backend:121 drops ALL with no added caps; frontend:198–201 adds only NET_BIND_SERVICE for port80. Static regression test_external_review.py:85 failed before and passes now. DB/Redis startup caps retained pending runtime evidence. Read-only mounts never claimed bypassed by DAC_OVERRIDE. |
| 12 | Remains ALREADY FIXED | Base frontend127.0.0.1:8080 only; actual Compose/TLS runtime not executed. |
| 13 | Addressed identified logging gaps locally | logging.py:13–14 redacts configured OAuth secrets; config.py:172 safe DB log emits only scheme, never credentials/query/path. test_external_review.py:41,49 failed before and pass now. Trusted daemon/host environment access remains outside this log-control guarantee. |
| 14 | Partially improved; isolation gate BLOCKED | judge.py:51 normalizes six alias/case forms before lexical checking, regression:56. Regex bypasses remain possible in principle: mandatory isolation is primary. No Docker/runsc execution or seccomp acceptance claimed; public judge stays disabled. |
| 15 | Owner-controlled residual | Historical .env pathname only; contents/exposure UNKNOWN. Staged deletion preserved, no private file/blob inspection, rotation/history rewrite. SECRET_HISTORY_ACTION_REQUIRED.md remains applicable. |
| 16 | Coverage addressed locally/native | test_external_review.py:131 production-config API sends to mocked SMTP transport, returns no dev_otp, accepts delivered code once and rejects replay/invalid code. Native verifier also issues through actual local STARTTLS mailbox with no dev_otp. Neither is Internet SMTP acceptance. |
| 17 | Partially addressed; successful evaluation race gate remains | blackhole.py:51–52 now locks and refreshes stale state before freeze. SQLite reproducer:93 failed before; real PG stale-session check passes. Native parallel disabled-judge submit returns503/no submissions/noXP; native daily reward fixture permits one25XP claim. No fabricated successful evaluation or new mock scoring. Successful real evaluation→XP concurrent submissions remain blocked by unavailable runtime; scheduler not represented as operational. |
| 18 | Capacity concern verified on actual PostgreSQL | Native13check suite includes six simultaneous joins for one remaining seat: exactly one200/five409 and final membership count2. Existing locking code unchanged; SQLite is not claimed sufficient. |
| 19 | Confirmed N+1 fixed; authz strengthened by tests | peer_review.py:53–69 joinedloads submission/project/author/corrector once per role. Six-correction query-count regression:61 fails before and passes with ≤6SELECTs including auth. Outsider POST explicitly403; existing finality/author/notification tests pass. |
| 20 | Security coverage improved; unrelated feature tests deferred | Added429 event/error propagation test; existing401/browser selected workflows retained. No autosave feature invented or unrelated sidebar component suite expanded. Intermittent Monaco cold-start timing remains documented below. |
| 21 | Coverage addressed locally | test_external_review.py:175 asserts exact production CSP/nosniff/frame/HSTS on200/429/404 and61st /api/health request with Retry-After. Bare /health remains orchestrator liveness, deliberately distinct. |
| 22 | Remains ALREADY FIXED | Current strict v2 client/receipt/authenticity suites pass; removed simulation is not resurrected. Real runtime separate. |
| 23 | Documentation refreshed | frontend/README.md is current contributor guide with working commands, integration limits, no stale hardcoded totals. FINAL_REPORT.md/PROJECT_STATUS.md explicitly historical and link to authoritative reports. |
| 24 | Existing privacy controls verified; legal/ops residual | Native owned export/deletion cascade and unit retention dry-run/apply pass. Audit retention is90days in code; automatic scheduling/legal approval not claimed. No unsupported Tunisian statutory retention assertion adopted. |
| 25 | Configuration docs addressed | Root/backend canonical examples explicitly ENABLE_DEV_OTP=false; INSTALLATION.md:40 documents sources, precedence and trusted-disposable opt-in; frontend example clarifies proxy export. Real .env untouched. Existing implicit backend .env loading retained; no half loader migration. |
| 26 | NOT APPLICABLE / deferred | /api/v1 migration explicitly excluded; used router prefix retained. |
| 27 | Documented and verified actual config contract | frontend README/export command and vite-config.test.js check actual process.env target import without loading .env. No loadEnv/import.meta.env substitution needed for documented exported-variable contract. File-only proxy setting explicitly unsupported; not falsely claimed fixed by adding file values. |
| 28 | Existing lint verified; remaining work deferred | ESLint/build actually pass. Makefile/DX process changes remain explicitly out of scope. |
| 29 | Metadata prevention added; content/history scan residual | scripts/check_tracked_secrets.py rejects private config/key filenames in index without reading blobs. Test:113 first failed for absent guard, now tests reject synthetic .env/allow canonical template. Guard runs in CI and validate.sh. It does NOT detect embedded or historical secrets; owner-authorized deeper scan/rotation still unperformed. |
| 30 | DISPUTED / no implementation change | Production workers/no bind source mount are not a broken hot-reload promise. No writable production source mount added. |
| 31 | NOT APPLICABLE / deferred | Bundle tuning remains out of scope; no invented size-reduction percentage. |
| 32 | NOT APPLICABLE / deferred | No TypeScript/prop-type migration; no invented error-reduction percentage. |

### Outcome counts (mutually exclusive)
- 8 already-fixed findings remain verified:1,2,3,6,7,8,12,22.
- 11 addressed locally this round (code, tests or documentation as applicable):4,10,13,16,18,19,21,23,25,27,29. ID29 still has a separate owner-authorized content/history-scan limitation.
- 4 partially improved with explicit remaining gates:11,14,17,20.
- 3 retain explicit accepted/owner/operational residuals:5,15,24.
- 1 partially stale DX finding with remaining work explicitly deferred:28.
- 2 disputed with evidence:9,30.
- 3 not applicable/explicitly deferred:26,31,32.
Total32. Do not turn these counts into “32vulnerabilities fixed.”

## Executed gates and reproduction evidence

Implementation regressions were added before the corresponding fixes:
- `/tmp/root404-external-before.log`:14backend failures (OTP gating/default,
  OAuth/DB log redaction,6language aliases, N+1 and capability allowlists).
- `/tmp/root404-external-frontend-before.log`:7failed/6passed of13filename cases;
  HTTP transport stubbed to avoid unintended real network calls.
- `/tmp/root404-external-before2.log`:2new failures/14passed (stale BlackHole
  activity freezing and missing tracked-secret guard).
- After corresponding fixes those targeted sets passed. Additional passing
  coverage-only tests did not require gratuitous implementation changes.
- Test harness repair: production Settings constructor tests now clear the
  workflow fixture's explicit ENABLE_DEV_OTP opt-in; Node config test imports
  node:process for ESLint. No production assertion weakened.

| Gate | Actual current result | Boundary |
|---|---|---|
| `bash scripts/validate.sh` | Latest run exit0/PASS | One prior unchanged browser run failed; see below. |
| Backend/controller tests |235PASS,5warnings | Includes20new external-review cases; test DB/transport fixtures, not learner execution. |
| Frontend tests |61PASS across15files |16new cases, including Node config export and React inert-text evidence. |
| ESLint / Vite build | PASS / PASS | Build is not runtime Nginx acceptance. |
| Chromium |9PASS across3viewports on latest run | Earlier run8PASS/1FAIL: desktop Monaco lazy route remained loading past5second existing assertion; no assertion/timeouts/retries relaxed. Intermittent cold-start remains a reliability residual, not hidden by final rerun. |
| npm audit |0reported vulnerabilities | Dependency audit only, no pentest claim. |
| Python compilation / whitespace | PASS / PASS | Source/static checks. |
| Tracked-secret filename guard | PASS | Index metadata only; real/historical values unknown. |
| Native PG/Redis/local STARTTLS verifier |13PASS, exit0 | Fresh random disposable databases/roles cleaned up; real local services, NOT production/Internet providers. |
| Docker/gVisor host supervisor / Compose TLS/Nginx | NOT RUN / BLOCKED | No runtime available/accepted; static caps/CSP not execution proof. |
| Real successful evaluation→XP | BLOCKED | No fabricated scoring or runtime evidence. Disabled failure path only. |
| External SMTP/AI/OAuth, independent security/legal acceptance | NOT VERIFIED | No paid/private probe or reviewer credentials fabricated. |

Latest detailed validation log: `/tmp/root404-external-validation.log`; earlier
cold-route failure retained at `/tmp/root404-external-validation-cold-failure.log`.
Native log: `/tmp/root404-external-native.log`. Auto-redacted validation reports:
`reports/validate.json`, `reports/validate.log`. This document preserves results
when ephemeral tmp logs are no longer available. No commit/push was made.
