# ROOT404 Release Candidate checklist

**RC DESIGNATION WITHHELD.** Only these classifications are used:
VERIFIED (specific listed scope), IMPLEMENTED BUT UNVERIFIED, INCOMPLETE, BLOCKED.
A verified local scope is never promoted to independent production verification.

| Requirement | Classification | Required release evidence / current boundary |
|---|---|---|
| Full backend/controller unit/regression tests | VERIFIED |135passed,4warnings,no skips |
| Frontend unit/integration tests | VERIFIED |35passed |
| Frontend lint/production build/audits | VERIFIED | Refreshed command results in FINAL_ACCEPTANCE_REPORT.md |
| Chromium desktop/tablet/mobile targeted journeys | VERIFIED |6tests, real disposable API, screenshots/axe/settings/rooms/logout/error states |
| Exhaustive browser/accessibility/device/product coverage | INCOMPLETE | Manual SR/keyboard, Safari/Firefox/actual devices and remaining workflows |
| Dedicated isolated dispatcher implementation | IMPLEMENTED BUT UNVERIFIED | No local Docker runtime; real CI gate prepared |
| Real Docker/runsc hostile acceptance | BLOCKED | Requires actual green CI artifact for this exact source; pipeline presence is not a pass |
| Independent host/isolation/security sign-off | BLOCKED | Separate agent pass is not external independent review |
| Original project-specific suites | INCOMPLETE | All9original projects lack complete harnesses; see grading matrix |
| Foundation4language suites | VERIFIED | Actual trusted references/wrong/boundary programs, not original-project grading |
| Real isolated grading/reward end-to-end | BLOCKED | Original suites/approved worker absent |
| Native lab PostgreSQL/Redis/STARTTLS checks | VERIFIED | Rerun9checks; PG16.2lab, not deployed versions |
| Production PostgreSQL/Redis/TLS/Nginx | BLOCKED | Exact private opt-in configuration and probes supplied |
| OpenAI/external SMTP receipt | BLOCKED | No approved key/recipient/egress; SMTP acceptance alone insufficient |
| Basic account/profile/privacy/export/session workflows | VERIFIED | Targeted API+browser evidence; provider/backup erasure not covered |
| Public rooms create/join/chat/history/leave | VERIFIED | Basic persisted/manual-refresh flow, not realtime/voice/video/moderation |
| Peer review booking/final feedback integrity | VERIFIED | Actual PG competing slot/booking/finalize awards and Chromium two-account flow; qualification/collusion/cancellation still incomplete |
| Learning indicators/leaderboard/analytics views | VERIFIED | Basic measured API-backed Chromium views; full paths/gamification/scheduler lifecycle remains INCOMPLETE |
| Persistent notifications | VERIFIED | Scoped private review-event list/read/read-all/export/delete/retention; native PG transaction and browser flow. Push/email/other event sources incomplete |
| Retention operations/provider/backup erasure | INCOMPLETE | CLI exists, production schedule/restore-erasure not verified |
| Public judge disabled by default | VERIFIED | Default false retained; CI never flips public deployment configuration |

No release tag, published release or production deployment is authorized by this
checklist. Resolve critical/high gates and attach exact-commit evidence first.

Additional non-waivable gate: distinct supervisor/learner identities are implemented
and native fixed probe verified, but **IMPLEMENTED BUT UNVERIFIED in Docker**.
The trusted root supervisor exact5capability surface and real protocol-forgery/
process-boundary behavior still require real CI plus independent assessment.
