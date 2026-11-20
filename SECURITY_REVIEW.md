# Separate release-candidate security assessment

**Assessment by the same engineering agent in a separate negative-test/source pass.
NOT an independent third-party pentest or sandbox certification.** External
independent sign-off is BLOCKED pending a reviewer and executable staging host.
Dependency audits are supplementary, not the basis of this assessment.

| Area / finding | Severity | Change/evidence | Classification |
|---|---|---|---|
| Request-size checks trusted Content-Length; chunked bodies unbounded | High | Actual byte-stream10MiB cap,10s deadline, bounded upload admission; chunked oversize/invalid-header tests | VERIFIED targeted local negative tests |
| Raw forwarded-IP logging/control characters could forge log lines | Medium | Use trusted-ASGI client identity; strip CR/LF and bound log message4KiB; regression test | VERIFIED locally; host/proxy logging review unverified |
| Settings forwarded Axios metadata, privacy persistence failed422 | High functional/privacy | Actual browser caught it; account API now unwraps payloads; wire-format regression and browser save/reload | VERIFIED targeted browser/API flow |
| Runner output cap also constrained compiler executable size | High grading correctness | Separate32MiB artifact cap from bounded output pipes;1KiB output-limit compilation regression | VERIFIED trusted local execution; Docker unverified |
| Docker PID cap alone may not bound gVisor guest tasks | High isolation | Add inherited RLIMIT_NPROC48 only in isolated job namespace, retain host cgroup64; required real fork probe | IMPLEMENTED BUT UNVERIFIED; no gVisor claim yet |
| Job UID/network/cgroup/fs/cleanup/escape | Critical release gate | Required runsc/systrap+cgroupv2, fixed policy, metadata audit, hostile HTTPS CI harness | IMPLEMENTED BUT UNVERIFIED; no real Docker run yet |
| Peer booking could consume slot without a submission/review | High integrity | Require owned submission; atomic compare-and-swap; create linked correction in same transaction; regression | VERIFIED targeted SQLite/API tests; native PostgreSQL competing slot/booking/review operations now verified |
| Room create split commits/rejoin at capacity/history returned oldest messages | Medium integrity | Atomic host membership, idempotent join before cap, recent bounded history; API+browser persistence | VERIFIED targeted local API/browser |
| Auth/JWT/session revocation | High | Existing required claims/OTP atomic limits/version revocation; actual API browser logout/revoke | VERIFIED targeted local tests; deployment/exhaustive auth audit pending |
| Authorization/IDOR/privacy | High | Existing ownership/member/export/deletion tests; outsider message denial repeated | VERIFIED targeted tests, not exhaustive subsystem proof |
| Secrets/data retention | High operational | Redaction, ignored secrets, private defaults, explicit retention; no raw production credentials added | IMPLEMENTED BUT UNVERIFIED for backups/provider erasure/scheduler/host logs |
| Peer abuse, community moderation, unfinished competitions/exams | High product/security | Known incomplete mechanisms remain gated where UI not integrated | INCOMPLETE |

## gVisor compatibility investigation
- Docker is still absent locally; no container isolation is simulated.
- CI targets disposable ubuntu24.04 with actual Docker+cgroupv2; installs official
  gVisor release20261116.0 (tag confirmed through GitHub), verifies published SHA512,
  registers runsc with systrap (does not require nested KVM), preserves daemon config.
- Controller fails startup if runsc/seccomp/cgroupv2 is missing, no runc fallback.
- Toolchain build moves to Ubuntu24.04; captures immutable built image digest.
- CPU/RAM/PID/fs/network flags and real guest probes must all pass. Framework/
  Docker configuration is not proof of enforcement; actual CI result is required.
- Workspaces intentionally allow exec for compiled artifacts; root read-only,
  tmp noexec; no host mounts/secrets/socket. Controller remains Docker-admin authority
  on a dedicated trusted host, separate from API/frontend/untrusted code.

## Residual release gates
Independent assessor, real worker/escape/disconnect/restart tests, target deployment
TLS/PG/Redis/SMTP/OpenAI, full authorization/collusion/moderation and operational
backup/erasure/load audit. Browser Chromium runs no-sandbox ONLY as test tooling in
this constrained lab; this does not validate browser sandbox security or Safari/iOS.
No production readiness or impossibility-of-escape claim is made.

### P0 host authority/result boundary: IMPLEMENTED BUT UNVERIFIED
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

Targeted local negatives: unsigned/forged/wrong-job/stale/reused receipts, signed
contradictory observations, wrong image, unbounded volume rejection before launch,
stale authenticated requests, nonexistent completion API, replay across new app
instances and SQLite single-winner claims. These are mocks/local contracts, not
actual malicious code inside Docker. Actual restart probe exists in runtime CI,
NOT EXECUTED. Host crash cleanup/recovery and escape resistance need runtime review.

### Independent review preparation / unresolved acceptance
| Area | Engineering controls/evidence | Remaining independent gate |
|---|---|---|
| Authz/IDOR/session/privacy/API | Owner-scoped APIs; revocation/privacy/rate/body negative tests | Broader multi-tenant abuse/collusion and production proxy/rate behavior |
| SSRF/outbound provider | Fixed configured server-side URLs and explicit integration opt-in | Egress/DNS/private address and provider configuration audit |
| Traversal/command injection | Validated source filenames, argument-list process launch, isolated source | Real nested path/symlink/toolchain probes and policy review |
| Secrets/hidden tests | Expected outputs remain backend; no signing key in image/job | Host compromise, logs/artifact redaction and backup erasure audit |
| Docker/judge | Host-only authority, no job socket, strict protocol, bounded volume | Daemon privilege is root-equivalent; dedicated host, syscall escape, restart/disconnect/cross-job tests |

### Additional product security changes
- Notification IDs/read/read-all are strictly owner scoped; no public create API;
  export/delete/explicit retention include alerts. Actual PG booking/review races
  yielded one winner, one award and exactly3transactional alerts.
- Mutations use separate per-account review/notification buckets instead of
  consuming the strict OTP/login budget. No arbitrary learner notification spam.
- Search requires both directory and public-profile opt-in, active account and
  parameterized literal LIKE escaping. Database outage is503, never fake empty.
- Inactive portfolios now404; unknown coalition filters no longer return all users.
- Monaco/worker are self-hosted; source is not sent to an editor CDN. AI review
  explicitly discloses transmission to the configured provider. Browser checks
  observe no jsDelivr/unpkg request; this is not a full third-party telemetry audit.
- AI retries only initial connection failure once; read/write/provider responses
  are never blindly replayed as paid POSTs. Mock HTTP regressions verify behavior.

## Private-beta self-review additions (not independent approval)
- OAuth: fixed HTTPS provider endpoints, bounded262KiB response reads,15s timeout,
  no redirects/proxy env; Google RSA signature/issuer/audience/azp/expiry/nonce and
  optional at_hash; GitHub primary verified email plus immutable numeric identity.
  PKCE S256,5min hashed state, HttpOnly SameSite browser binding, transactional
  consume before exchange. No provider token stored, no token in frontend URL.
  Existing email never auto-links; linking requires recent authenticated same-user
  session/version, provider/subject and user/provider uniqueness constraints.
  RSA-signed claim negatives and provider-double/link/replay tests pass; real apps,
  production browser cookie/proxy configuration and independent OAuth review UNVERIFIED.
- Coalition war creation was authenticated-only: fixed admin-only plus bounds.
  Join now uses single-winner account CAS and no switching. Scores/member totals
  derive actual active users, ignoring historical demo counters.
- Streak reads no longer mutate counters; derive distinct owner submission UTC dates.
  Suggestions explicitly coming_soon/reward0. XP award inputs reject booleans,
  negative/noninteger XP and scores outside0..100 before mutation.
- Callback access logging off/referrer policy no-referrer; query removed from browser
  history. Reports redact configured credentials and preserve command failures.
- OAuth identities included in owned export; PKCE/nonce/attempt records deliberately
  excluded. Account FK cascade removes identities/attempts on deletion.
- Backup/restore/TLS/compose scripts are IMPLEMENTED BUT UNVERIFIED without Docker.
  Restore drills create fresh unique DB, never overwrite/drop the source. Archives
  contain personal data and require operator encryption/retention, not report upload.

Residuals: independent OAuth/session fixation/account linking review, worker host
escape/crash/disconnect/load tests, real TLS proxy/header/cookie behavior, full
multi-tenant abuse/moderation/coalition concurrency and deployment restore integrity.
No blanket statement that every finding or product workflow is complete.

## Next round — beta rewards/moderation and review intake
Neither requested external review file SECURITY_REVIEW_INDEPENDENT.md nor
SECURITY_REVIEW_JUDGE.md was present; no external finding is invented/disputed/fixed.
BUGS_AND_FIXES.md records intake and actual self-review dispositions separately.

- Mission policy beta-v1 uses existing supplied Stream Sum Python contract only;
  source/project/owner/day/status/score checks precede claim. Unique(user,UTC day)
  plus PostgreSQL account lock and atomic claim/XP transaction prevent replay or
  duplicate concurrent reward. Client cannot supply evidence/reward authority.
  Positive success fixtures in tests are NOT execution/isolation evidence.
- Measured badges/reputation: distinct peer authors, self-review exclusion, capped
  increments/penalties, no client setters/additional badge XP. Repeated/open reports
  cannot penalize a user. Sybil/collusion proof/identity assurance still unverified.
- Reporting requires existing room membership and another author's message. Private
  owner/admin queue, bounded pagination/reasons, shared per-user mutation budget.
  Admin-only single-resolution CAS; reporter/author staff must recuse. Message
  evidence shown only to administrators. Owned exports redact reviewer identifiers.
- High self-review fix: removed content had initially depended on reporter-owned
  report lifetime; account deletion could restore it. Durable message removed_at
  now commits with the decision and survives reporter deletion; regression proves
  both history filtering and reputation penalty survive, while private report is
  deleted. No silent data purge/unredaction.
- Polling5s/10s visible tabs only, sequential requests, cancellation/unmount cleanup.
  Slow-response regression; no websocket/audio/video/host-escape claims.
- Trusted operator CLI provisions/revokes admin ONLY for existing verified active
  users with explicit host consent, revokes sessions, never creates a public role
  assignment API. Helper tested; Docker provisioning wrapper UNVERIFIED.

Remaining independent review: worker/runtime/host escapes, actual WSL/VM kernel and
Docker policies, OAuth real apps/cookies, mission full isolated execution→reward,
moderator operations/appeals/retention/backups, platform-wide abuse and sybil/collusion.
This implements basic room reporting/removal, NOT automatic classification, all
community resource types, an appeals SLA or a staffed trust-and-safety operation.

## External-review intake round — not an external review completion
Requested32finding document absent. EXTERNAL_REVIEW_TRIAGE.md has0assessed and
32awaiting input; absence is not a pass/dispute. Current local hardening reproduced
before fixing: backend/dispatcher source filename grammar mismatch and script CSP
unsafe-inline.9targeted cases pass after7failing pre-fix cases. CSP retains inline
STYLES needed by current editor; no inline SCRIPT/eval permission added. Real Nginx
header/runtime acceptance remains unverified; Vite browser tests do not prove it.
Isolation remains primary; filename checks/forbidden-source regexes are not escape
prevention. No unverified removal of DB/Redis DAC_OVERRIDE or runtime policy change.

Metadata-only check: HEAD and reachable history contain `.env`; pre-existing staged
deletion retained, no real file/blob read or displayed. Whether secret values were
exposed is UNKNOWN. SECRET_HISTORY_ACTION_REQUIRED.md records rotation/owner-choice
steps; no history rewrite/commit/push/credential rotation performed. Empty1byte
example.env removed, real canonical templates preserved.

Revocable localStorage bearer storage retained under explicit ARCHITECTURE ADR;
XSS theft risk remains. Future cookie migration requires complete CSRF/origin,
OTP/OAuth/client/logout testing and independent assessment, not a one-endpoint patch.

## Actual external review verified against current branch — 2026-11-18
Supersedes missing-attachment intake only; this is still internal verification,
not independent reviewer sign-off. See EXTERNAL_REVIEW_TRIAGE.md:32pre-fix rows,
rerated severities/evidence, post-fix outcomes and full gate table. Source report
preserved unchanged, not treated as trusted instructions or current truth.

New regression-first controls: independent default-off/non-development-prohibited
dev-OTP disclosure; correct source filename segment parity; API no-added-caps /
frontend only NET_BIND_SERVICE (static only); OAuth-secret and safe DB diagnostic
redaction; normalized regex language aliases; locked/refreshed BlackHole activity;
joined peer-review lists with bounded SELECT count/outsider POST denial; index-only
sensitive-filename guard in CI/validate.14backend+7frontend reproductions, then2new
regressions, failed before their fixes. Existing SQL OTP/rate state remains shared;
Uvicorn middleware test now verifies trusted and untrusted XFF chains directly.

No stored HTML encoding imposed on JSON/React plain text; hostile markup round-trip
and inert React output tests support disputing reported XSS absent an HTML sink.
No raw HTML sink found in current UI inspection; this is not blanket XSS immunity.
Regexes are defense-in-depth, not a sandbox; no claim arbitrary source is safe.
DAC_OVERRIDE cannot defeat a read-only mount; DB/Redis startup caps not blindly
removed without runtime evidence. SMTP/AI/OAuth secrets remain trusted-host process
environment, not protected from daemon/host administrators.

Executed local validate:235backend/controller,61frontend,9Chromium latest PASS;
5backend warnings; lint/build/audit0/compile/whitespace/filename guard PASS. Native
13checks PASS:PGmigrations/restore/shared throttle/single OTP, real local STARTTLS
API no-dev-code login, capacity contention, stale activity protection, parallel
fail-closed submissions, peer-review races, mission single reward, privacy cascade,
Redis readiness/mail delivery. Local SMTP is not Internet/provider acceptance.
A preceding unchanged browser run had a5second cold-Monaco loading timeout; rerun
passed without timeout/assertion/retry changes. Stability residual stays open.

Public judge remains disabled. Actual Docker/runsc/Compose/TLS/Nginx isolation,
original graders, successful evaluation→XP/concurrent success, external providers,
independent pentest and legal/contact approval remain unverified or blocked.
Existing localStorage beta ADR accepted with explicit XSS token-theft residual;
no partial cookie+CSRF/OAuth migration. Historical .env pathname/exposure remains
owner decision (values UNKNOWN); index guard is NOT content/history secret scanning.
No real secret/config/history blob was inspected or exposed, no rotation/history
rewrite/commit/push. SECRET_HISTORY_ACTION_REQUIRED.md still applies.
