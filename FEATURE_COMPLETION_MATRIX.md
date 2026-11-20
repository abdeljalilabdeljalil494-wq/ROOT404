# ROOT404 source/evidence feature matrix

**NOT PRODUCTION READY. No feature is production-verified.**
A=implemented; B=unit/component tested; C=integration tested (boundary named);
D=externally verified outside this engineering lab; E=production verified.
Partial means the full original scope remains unfinished, not merely awaiting keys.
A model, route, gated prototype or empty state does not complete a product feature.

| Feature | A | B | C: actual boundary | D | E | Genuinely incomplete engineering / remaining acceptance |
|---|---|---|---|---|---|---|
| Registration/OTP/JWT/logout/revocation | Yes | Yes | SQLite APIs, native PG races/local STARTTLS mailbox; Chromium login/revoke | No | No | Target deployment delivery/abuse/independent security |
| SMTP implicit TLS/STARTTLS | Yes | Yes | Actual local certificate-verified STARTTLS/API receipt | No | No | External recipient/TLS465/provider reputation/bounce operational checks |
| Profile/privacy/settings | Basic complete | Yes | Owner SQL APIs/Chromium saves, new profile view | No | No | Wider privacy/consent and backup/provider erasure review |
| Dashboard/activity | Partial | Yes | Actual account/submission aggregates + browser navigation | No | No | Full mission/widget lifecycle, schedule and reward abuse controls |
| Notifications | In-app review events complete | Yes | Owner list/read/read-all/export/delete/retention; actual PG transaction/race; Chromium read-all | No | No | Other event producers, push/email delivery, real-time stream, preferences |
| Global search | Basic complete | API | Actual API and desktop/tablet browser links; both privacy opt-ins required | No | No | Search page/mobile search UX, scale/full-text/index tuning |
| Catalog/requirements/detail | Partial | Yes | API and Chromium catalog; data-preserving existing catalog | No | No | Complete authoritative subjects/resources/artifact contracts |
| Learning Journey | Basic personal view | Component | Chromium API-backed progress/prerequisite links | No | No | Enrollment/track authoring, full path/adaptive lifecycle |
| Skill Graph | Basic stored indicator view | Backend | Chromium selected-state axe; actual stored values | No | No | Assessment calibration, richer graph/proficiency evidence |
| Analytics | Basic measured view | Component | Actual submission aggregates, Chromium | No | No | Rich event telemetry, time-to-solve, calibrated forecasts (never invented) |
| Piscine | Partial backend; prototype gated | Targeted | Day/progress records only | No | No | Real exercise content, attempts, grading/progression lifecycle |
| Monaco | Self-hosted4language editor | Build | Actual Chromium loads local editor/worker without jsDelivr/unpkg; disabled judge503 | No | No | Multi-file management, durable drafts, full IDE keyboard/a11y/performance |
| Run/compile/submit/history/report | Partial | Yes | API/client double and trusted native references; no live container grading | No | No | Approved isolated grader + full product evaluation workflow |
| Judge controller | Implemented | Yes | HTTP control/preflight/cleanup test engine only | No | No | Real Docker/runsc/hostile acceptance and independent host review |
| Host supervisor / learner boundary | Host-only authority, minimal UID1000 image | v2 forgery/replay/observation/cleanup contract tests | No current real Docker evidence; native old UID probe is superseded | No | No | IMPLEMENTED BUT UNVERIFIED: runsc/process/IPC/volume/escape and cross-job runtime evidence |
| Foundation grading |4specific foundation exercises | Yes | Trusted GCC/G++/Python/Node references, wrong/boundary/loop/error/resource probes | No | No | Real isolated execution/score/reward E2E; not original project coverage |
| Original9project grading | No complete harnesses | No | None | No | No | See PROJECT_GRADING_MATRIX.md; these are coding gaps, not user tasks |
| AI Mentor/debug/explanation | Basic provider ask/history | Yes | Mock HTTP+SQL, UI component API doubles; no actual OpenAI | No | No | Live key verification, quality/consent, multi-thread/context replay |
| AI code review | Provider+IDE action implemented | Yes | HTTP test transport; connection-only retry, no paid read-timeout replay | No | No | Real provider acceptance; richer validated structured suggestions |
| Recommendations | Partial heuristic | Targeted | Stored skill gaps only | No | No | Calibrated adaptive workflow/executable micro-challenges |
| Peer review | Booking/detail/human feedback connected | Yes | SQLite APIs, actual PG competing slot/booking/review award, actual Chromium two-account flow | No | No | Cancellation/rescheduling, qualification/collusion, timezone/device/scale review |
| Rooms/text messaging | Basic create/join/history/send/leave | Yes | Actual persisted API/Chromium reload; membership negative tests | No | No | Realtime/voice/video/shared terminal, invitations and moderation |
| Community/direct messaging | Partial/gated original prototype | Limited | No complete workflow | No | No | Forum/feed/DM/moderation/abuse/report lifecycle |
| Coalitions | Basic UI/API connected | Yes | Owner membership CAS, real active-account XP/member aggregates, Chromium/axe page | No | No | Wars coming soon; distributed abuse/moderation and actual PG coalition race acceptance remain |
| Mentorship | Development prototype gated | Limited | No full scheduling service | No | No | Persistent request/consent/schedule/history/notification workflows |
| XP/levels | Partial | Yes | Targeted award/idempotency formulas; native review award race | No | No | Full reward-source lifecycle and economy abuse review |
| Achievements/badges/streaks/daily missions | Beta-v1 implemented | Yes | HTTP claim/date/owner/replay, SQLite+actual PG claim race, UI/Chromium selected pages | No actual isolated mission execution | No | Four measured current-record badges, daily Stream Sum25XP; judge-positive journey BLOCKED |
| Leaderboard | Basic opt-in ranking view | API | Chromium, actual SQL rankings; no invented trend/score | No | No | Full ranking lifecycle/performance/abuse/season logic |
| Reputation | Measured beta-v1 | Yes | API/portfolio consistency, distinct peers, staff-only removal penalties | No | No | Not identity assurance; sybil/collusion/operational calibration remains |
| Arena/competitions/matchmaking | Partial, UI gated | Targeted | Create/join records only | No | No | Atomic lifecycle, real problem bank/deadlines/evaluation/winner/anti-abuse |
| Developer portfolio | Basic public/owner preview connected | API | Chromium public opt-in/owner data; inactive/private denial | No | No | Rich curation/embed/consent/hiring handoff; independent privacy review |
| Hiring | Development prototype gated | Gate only | No employer-delivery integration | No | No | Persistent employers/jobs/applications/consent/delivery |
| Exams | Development prototype gated | Gate only | No persistent graded sessions | No | No | Question bank/session/time/grade/proctoring policy |
| Alembic0001–0007 | Yes | Yes | Actual SQLite+native PG upgrade/preserved rows/downgrade/reupgrade/dump-restore | No | No | Production version/backup/restore/operator staging rehearsal |
| PostgreSQL/Redis | Configured | Yes | Actual PG16.2 and Redis8.10.3local lab; NOT target deployment | No | No | Target patched images/TLS/HA/backup/load/monitoring |
| Retention/export/deletion | Active-DB controls | Yes | Real PG export/delete; notification dry-run/apply and owner tests | No | No | Operator scheduling, backups/provider erasure ledger, legal review |
| Docker/Compose/Nginx/TLS | Prepared | Static/control | No actual Docker/Nginx deployment | No | No | Real build/start/runtime/volumes/proxy/cert/backup/restore acceptance |
| Testing/CI | Unified local scripts and prepared CI | Yes | Backend+frontend+actual browser+native services | No | No | Docker and remote CI unexecuted; full product/device/independent audit |

Exact commands: USER_TESTING_GUIDE.md. External actions only:
USER_ACTION_REQUIRED.md. Original vision remains docs/PRODUCT_VISION.md.
No implementation gap above is assigned to the user as coding work.

## Critical release gate classifications
| Critical gate | Classification | Actual evidence / remaining requirement |
|---|---|---|
| Host-only judge authority and protocol v2 | IMPLEMENTED BUT UNVERIFIED | Host supervisor outside learner containers; local contract tests pass, actual Docker boundary unrun |
| Real Docker/gVisor CI and hostile execution | BLOCKED | Docker/runsc absent here; prepared workflow is NOT execution evidence |
| Original nine project-specific graders | INCOMPLETE | Subjects absent; no approved project harnesses; hard503 prevents generic-suite bypass |
| OpenAI/external SMTP/production PG+Redis/Nginx TLS | BLOCKED | Probe code and mocked negative tests exist; no authorized live configuration or target verification |
| Independent security assessment | BLOCKED | Engineering negative tests/source review only; independent reviewer/staging required |
| Local quality regression | VERIFIED | Local unit/API/component/browser boundaries only, not release authorization |

## Private-beta classification (current)
| Scope | Implemented | Unit tested | Integration tested | Externally verified | Production verified |
|---|---|---|---|---|---|
| Nine original graders | Interface/templates only; actual adapters INCOMPLETE | Fail-closed registry/scoring | API503 bypass tests | No | No |
| Google/GitHub OAuth/linking | Yes, schema0006 | Provider doubles + real RSA claim negatives | SQLite HTTP state/link/replay/export/delete + migrations | No, real apps UNVERIFIED | No |
| Coalition basic membership/ranking | Yes | API/UI | HTTP + Chromium page; no actual coalition PG race claim | No | No |
| Peer review / Rooms / Notifications / Settings | Existing basic workflows + room abuse limits | API/UI | HTTP, actual native PG review races, Chromium core workflows | No | No |
| Analytics/skills/profile/rankings | Basic measured/stored-data views | API/UI | Chromium selected views/privacy | No | No |
| Daily missions | Executable Stream Sum Python + durable daily25XP claim | Owner/day/success/replay/input tests | SQLite and actual PG4parallel claim race; browser disabled state | No isolated execution | No |
| XP/levels | Trusted project/review award path with input validation and repeat-award protection | Yes | API/native PG races; disabled browser submit awards0 | No actual isolated judge→XP | No |
| Badges/reputation measured beta-v1 | Four current-record badge criteria + capped server reputation | Distinct peer/self exclusion, sanction/read tests | HTTP/portfolio; private reporting/removal browser | No independent abuse proof | No |
| Community landing / realtime audio/video / coalition wars | Clearly gated/coming soon | Gate tests/basic API controls | No complete workflow | No | No |
| Compose migration/TLS/logging/backup/restore | Code/config prepared | YAML/static checks only | Docker paths UNVERIFIED | No | No |

## Next round — moderation/polling and platform correction
| Scope | Implemented | Unit tested | Integration tested | External | Production |
|---|---|---|---|---|---|
| Room reporting/removal | Yes, member-only/private queue/non-conflicted staff CAS | IDOR/replay/spoof/export/deletion negatives | Actual HTTP + Chromium member→staff removal at3viewports | No | No |
| Room/queue polling | Yes5s/10s visible-tab sequential | Slow-response/no-overlap/unmount regression | Chromium rooms/reports | No | No |
| Operator admin provisioning | Host-only explicit grant/revoke existing verified account; session invalidation | Yes | Helper HTTP token rejection, Docker wrapper UNVERIFIED | No | No |
| Windows11 WSL2/systemd/LinuxEngine/runsc setup | Runbooks prepared | Static/shell checks only | NOT executed on WSL | No | No |

Current local suite215backend/controller,45frontend/13files,9Chromium, lint/build/
audit/compile PASS. Native local10checks include actual PG0007 migrations/restore/
reward concurrency (trusted submission fixtures), Redis and verified STARTTLS.
No independent review files supplied, no original graders invented. Automated
classifiers/platform-wide moderation/appeals/audio/video/presence remain INCOMPLETE,
not implied by the basic room workflow.

## External-review intake limitation
EXTERNAL_REVIEW_FINDINGS.md absent:32reported findings remain UNASSESSED, no per-ID
closure claimed. Separate current filename-validation/CSP regression fixes are
implemented/locally tested, not external findings certified closed. Nginx/runtime,
Docker and public judge gates unchanged. HEAD/history `.env` metadata requires owner
review/possible rotation/remediation; no secret values read. See triage/security
and SECRET_HISTORY_ACTION_REQUIRED.md. Empty example.env removed; use canonical
.env.example templates. No TypeScript/API-version/bundle/Makefile work performed.

## External-review evidence delta — 2026-11-18 (actual report received)
The previous “32awaiting attachment” limitation is superseded by
EXTERNAL_REVIEW_TRIAGE.md. All32 checked against current branch; initial counts:
8already fixed,1confirmed,18partial,2disputed,3not applicable.

| Area | New evidence / implementation | Still not accepted |
|---|---|---|
| Auth | Default-off independent dev-code flag, non-development rejection; mock-SMTP production API and real local STARTTLS no-dev-code flow | External SMTP/OAuth, full cookie+CSRF migration (existing bearer ADR retained) |
| Proxy/shared limits | Actual Uvicorn middleware trusted/untrusted chain test; PG32contenders/5budget and16contenders/1OTP | Real staging proxy topology |
| Judge boundary | Filename grammar parity, alias lexical checks, noXP on parallel disabled503 | Real Docker/runsc execution/receipt/isolation and successful evaluation→XP |
| Least privilege/logs | Static API zero added caps, Nginx only low-port cap; OAuth secret and DB query credential redaction | Compose/Nginx startup/enforcement; DB/Redis cap removal |
| Rooms | Native PG6joins/one remaining seat:1accepted/5conflicts | Advanced collaborative/WebRTC features |
| Progress | Stale BlackHole activity regression fixed; native daily mission single reward | Successful real project-award contention and operational BlackHole scheduler |
| Peer review | Joined eager lists bounded SELECT count; outsider POST denied; native booking/review races | All human-review/product quality scenarios |
| Privacy/secret hygiene | Existing retention/export/delete verified; index-only sensitive-filename CI guard | Legal/contact approval, scheduled retention, authorized historical/content secret review |
| UI reliability | Latest61unit/service tests +9Chromium pass | Prior unchanged cold Monaco timeout disclosed; no durable autosave/all-route certification |

Latest whole validation235backend/controller,61frontend/15files,9Chromium,
lint/build/audit0/compile/whitespace/filename guard PASS; native13checks PASS.
Local test success is not feature completion or production authorization. TypeScript,
API versioning, bundle/lazy tuning, Makefile and unrelated component tests deferred.
