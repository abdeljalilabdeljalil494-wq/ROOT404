# ROOT404 next development round — acceptance checkpoint

## Verdict: NOT PRODUCTION READY; public judge remains DISABLED
Existing branch/architecture preserved. No commit/push. Real `.env` not read,
modified or printed. No invented original specifications or execution evidence.

## External32finding intake — BLOCKED, not completed
EXTERNAL_REVIEW_FINDINGS.md was not found under the supplied/alternate filename.
32finding statements/IDs are unavailable. EXTERNAL_REVIEW_TRIAGE.md records0assessed
in every requested disposition and32awaiting input; no per-ID closure fabricated.
Upload the report to complete mandated triage and ordered fixes.

Separate current observations reproduced BEFORE fixing:
- Backend source filename parity:5invalid paths accepted upstream and harmless
  a..b.py rejected upstream. Same grammar now enforced as dispatcher/launcher.
- Production script CSP unnecessarily permitted unsafe-inline; removed for scripts,
  retained required inline styles. Real Nginx policy enforcement remains UNVERIFIED.
Targeted run before:7failed/2passed; after:9passed. New regressions retained in full
suite. No source-regex claim of isolation/escape prevention.

Other changes: removed one-byte empty example.env (not real template); canonical
.env.example files preserved. Token-storage ADR retains complete revocable bearer
flow, explicitly records XSS risks and requirements for future atomic cookie+CSRF/
OAuth migration; no half migration. No speculative capability removal.

Metadata-only secret check: HEAD/history contain .env, with pre-existing staged
deletion. Actual historical secret content/exposure UNKNOWN; no real file/blob read.
SECRET_HISTORY_ACTION_REQUIRED.md gives owner-choice review/rotation/remediation
steps; no restore/history rewrite/commit/push/rotation performed.

Deferred: TypeScript, /api/v1, bundle/lazy tuning, Makefile polish, unrelated
frontend component tests. Other external findings cannot be assessed without input.

Files this intake pass: EXTERNAL_REVIEW_TRIAGE.md, SECRET_HISTORY_ACTION_REQUIRED.md,
backend/app/services/judge.py, frontend/Dockerfile, test_review_intake_security.py,
ARCHITECTURE.md, BUGS_AND_FIXES.md, FEATURE_COMPLETION_MATRIX.md, SECURITY_REVIEW.md,
this report; deleted empty example.env. Prior-round work below remains preserved.

## Prior-round review intake and actual fixes
Neither SECURITY_REVIEW_INDEPENDENT.md nor SECURITY_REVIEW_JUDGE.md exists in the
working tree. BUGS_AND_FIXES.md records intake as unavailable, not an audit pass.
Self-review fixes with regressions include non-conflicted administrator decisions,
reporter-deletion content resurrection, private export reviewer-ID redaction and
slow-poll overlap. SECURITY_REVIEW.md remains engineering self-review only.

## Actual executed results
| Check | Result | Exact scope |
|---|---|---|
| `bash scripts/validate.sh` | PASS | reports/validate.log/json; /tmp/root404-review-validation.log |
| Backend/controller |215passed,4warnings | Unit/API/trusted fixture/controller contracts, not Docker |
| Frontend |45passed/13files | Component/service/poll cancellation tests; lint/build PASS |
| Chromium |9passed,3viewports (~1.9min) | Prior core+register/OTP/submit503/no XP; progress/queue pages; member report→staff UI removal; selected axe |
| npm audit |0known vulnerabilities | Supplementary dependency check only |
| Python compilation/shell syntax/whitespace | PASS | Static checks, not deployment/runtime certification |
| Native PostgreSQL/Redis/local STARTTLS |10checks PASS | Real schema0007 fresh/upgrade/preserved row/dump+restore, API/review races,4parallel mission claims→one25XP winner, local mailbox |
| Nine grader inventory | INCOMPLETE/exit1 | Nine disabled; explicit templates, no authoritative original spec found |
| Docker/WSL/external real apps | NOT EXECUTED | Remain blocked/unverified, never inferred from local suites |

Mission-positive tests use trusted DB success fixtures; **no learner program was
executed through Docker or a public judge to earn these results**.

## Implemented this round / files changed
- `backend/app/models/beta.py`, `0007_beta_workflows.py`, model registration and
  RoomMessage.removed_at: unique daily claims, private reports, durable removal.
- `services/beta_progress.py`, `api/beta.py`, router: executable foundation mission,
  UTC25XP claim checks, computed four-badge catalog/reputation, member-only reporting,
  owner/admin bounded queue, non-conflicted staff CAS remove/dismiss.
- room service/API, account export, dashboard/auth, analytics/portfolio: removal
  filtering/privacy, authoritative mission/achievement data. `manage.py` and
  `scripts/set-admin.sh`: explicit trusted existing-account role change/session revoke.
- `BetaProgress.jsx`, `Moderation.jsx`, App/Profile/Dashboard/RoomView and polling
  hook: wired progress/reporting,5s/10s sequential polling, visible failures, no fake XP.
- New workflow/authz/IDOR/replay/concurrency/deletion/admin tests; component tests,
  polling test; browser_server's disposable moderator fixture and expanded Chromium
  actual member/staff reporting journey. Existing coverage retained.
- Migration assertions/native/external/restore revision expectations updated0007;
  native verifier adds actual PG four-way reward race (fixtures clearly identified).
- Rewritten Windows11/WSL2 USER_ACTION_REQUIRED.md and USER_TESTING_GUIDE.md;
  BETA_REWARDS_MODERATION policy, BUGS_AND_FIXES, security/grading/progress/feature/
  engineering/readiness/README records updated. Prior working-tree changes preserved.

## Gate status
| Gate | Status | Remaining limitation |
|---|---|---|
| Local quality regression | VERIFIED | Named local boundaries above only |
| Daily mission reward/badges/reputation | VERIFIED local contracts | Positive isolated judge→mission reward BLOCKED; current-record badges, not permanent certificates |
| Room reporting/moderation/polling | VERIFIED locally | No claim of classifier/platform-wide coverage/appeals/SLA or sybil proof |
| Host-only judge authority/envelopes/replay | IMPLEMENTED BUT UNVERIFIED | Real isolation/hostile/crash/escape proof required |
| Docker/gVisor/WSL2 runtime acceptance | BLOCKED | No Docker/runtime here; WSL setup documented but unexecuted |
| Nine original graders | INCOMPLETE | No approved original subjects, no adapters enabled; generic bypass denied |
| Real OAuth/external services | IMPLEMENTED BUT UNVERIFIED / BLOCKED | Real private apps/SMTP/OpenAI/targetPG+Redis/TLS missing |
| Compose/TLS/admin provisioning/restore Docker wrappers | IMPLEMENTED BUT UNVERIFIED | Actual WSL/VM stack and operational drill required |
| Independent security assessment | BLOCKED | Review files/reviewer not supplied; self-review cannot substitute |
| Audio/video/presence/platform-wide moderation | INCOMPLETE | Clearly unavailable; room/queue polling only |

## Ordered operator actions (Windows11 corrected)
Exact preparation/commands/expected checks/report files: USER_ACTION_REQUIRED.md.
1. WSL2 Ubuntu24.04+systemd+Docker Engine inside Linux+runsc; checkout at~/ROOT404,
   NOT/mnt/c; Desktop integration off. Prefer disposable Ubuntu VM for hostile
   separation; unsupported WSL policy means BLOCKED, never runc fallback.
2. Run one-command hostile test; return reports/test-judge-linux.* and
   reports/judge-isolation/, plus nonsecret Windows/WSL/kernel status.
3. Reproduce local validate; authorized staging stack/schema0007 and actual-mail
   browser checklist (includes separate member/moderator reporting). Judge stays off.
4. Authorized external services/real Google+GitHub apps; physical mobile LAN/TLS
   checks using scoped Windows/Hyper-V networking or bridged disposable VM.
5. Supply approved nine subject templates and any independent review findings;
   agent retains grader implementation/testing, not assigned as user coding.

No OTP/state/code/token/keys/private mailbox/backups in returned artifacts. Wrapper
PASS means exit0 only; manual results are operator-reported. HMAC receipts are not
execution attestation. No production readiness, deployment or public enablement.

## Latest acceptance checkpoint — actual external report, 2026-11-18
**NOT PRODUCTION READY. Public judge remains disabled.** This section supersedes
older missing-report/count checkpoints; it does not overwrite historical evidence.

EXTERNAL_REVIEW_TRIAGE.md was written BEFORE this round’s implementation with
one row per supplied finding, current anchors, severity and disposition. Initial
32finding totals:8ALREADY FIXED,1CONFIRMED,18PARTIAL,2DISPUTED,3NOT APPLICABLE.
After work:8remain already-fixed;11locally addressed;4partially improved;
3retain explicit accepted/owner/operational residuals;1DX remainder deferred;
2disputed;3not applicable. These are NOT32security vulnerabilities fixed.

| Executed gate | Actual latest outcome |
|---|---|
| `bash scripts/validate.sh` | exit0, local PASS |
| Backend/controller |235passed,5warnings |
| Frontend service/component/config |61passed across15files |
| Chromium desktop/tablet/mobile |9passed,1.8min |
| ESLint / Vite build / npm audit | PASS / PASS /0reported vulnerabilities |
| Python compile / git whitespace / tracked-secret filenames | PASS / PASS / PASS |
| Native disposable PostgreSQL/Redis/local STARTTLS |13checks passed, exit0 |

**Reliability qualification:** a preceding unchanged validation run failed desktop
Monaco mount (route still “Chargement…” at5seconds), with8browser passes. Existing
assertions,5second timeout and retries=0 were NOT weakened or changed. Latest full
unchanged rerun passed. Intermittent cold editor readiness is still an open residual,
so browser stability is not certified. Earlier harness failures (Node process import
and production constructor inheriting fixture dev-code opt-in) were corrected;
no production guard or assertion was removed to obtain green results.

Regression-first fixes cover dev-OTP exposure, frontend filenames, capability
allowlists, OAuth/DB diagnostic leaks, judge regex alias bypass, stale BlackHole
activity, correction-list N+1 and missing metadata CI guard. Additional coverage
checks actual Uvicorn XFF trust, production-config API mail without dev_otp,
corrector-only POST, health rate/header/error behavior,429 propagation and inert
React text. Contributor/env instructions are current. Per-ID test names and
red→green logs are recorded in EXTERNAL_REVIEW_TRIAGE.md.

### Unchanged acceptance gates
- Docker/gVisor outside-container host supervisor, actual Compose/TLS/Nginx CSP/caps:
  BLOCKED/NOT RUN. Static configuration and signatures are not execution proof.
- Successful real learner evaluation→XP and successful project-award concurrency:
  BLOCKED. Native parallel disabled-judge requests503/noXP and daily reward fixture
  are explicitly different evidence; no fake scoring/provider response added.
- Original nine subject-specific executable graders: incomplete/unapproved.
- External SMTP/AI/OAuth/provider, backup operations, independent review and legal
  acceptance: unverified. Native restore/STARTTLS are not production acceptance.
- Existing beta localStorage ADR retained, token theft by XSS residual explicit;
  no half cookie/CSRF/OAuth migration. Historical .env values/exposure UNKNOWN,
  owner-authorized content review/rotation decision remains; no history rewrite.
- Retention scheduling/legal/contact approval remain operational decisions, not
  proof of a specific Tunisian statutory retention requirement.
- TypeScript,/api/v1,bundle/lazy tuning,Makefile and unrelated component tests deferred.

No real .env was inspected/edited/printed by tools; no historical secret blobs read;
pre-existing staged deletion preserved. No commit or push. Working branch remains
arena/bf97d7c1-root404. Latest logs `/tmp/root404-external-validation.log`,
`/tmp/root404-external-native.log`; preserved redacted local gate summary in triage
and reports/validate.{json,log}. No private/paid external probe was initiated.
