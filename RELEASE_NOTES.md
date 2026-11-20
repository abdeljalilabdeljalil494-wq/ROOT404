# ROOT404 RC engineering checkpoint (not a released RC)

No RC/release tag or production-readiness claim. Original architecture, project
scope and stored data are preserved; existing application components were extended.

## Changes
- Reproducible real Docker+gVisor/systrap CI gate, immutable built image, authenticated
  local HTTPS dispatch, real hostile-job harness, whitelisted policy evidence and
  orphan failure gate. No runtime fallback or simulated Docker success.
- Explicit private CA verification option for worker TLS; strict TLS remains on.
- Runner compilation artifacts no longer share the tiny stdout file-size cap;
  bounded pipes and isolated guest process cap added.
- Real Chromium/Playwright journeys at1440x1000,820x1180,390x844 with axe checks.
- Fixed Settings Axios-payload contract discovered by real browser testing.
- Improved contrast, named progressbars, hidden mobile-sidebar focus behavior;
  removed unsupported OAuth promises, fake authentication marketing counters,
  misleading unread notification dot and nonfunctional search affordance.
- Connected public Rooms/RoomView to real persisted APIs: create/join/chat/reload/
  leave; no fake WebRTC/shared-terminal/session-report promises.
- Atomic room creation, correct latest-message window and full-room idempotent join.
- Validated future/time-bounded review slots, owned-submission booking precondition
  and atomic slot claim with actual linked correction; no fake booking success.
- Enforced streamed HTTP body bounds/deadline and hardened audit-log line handling.
- Added private opt-in live PG/Redis/SMTP+IMAP/OpenAI/Nginx/TLS verification script.

## Compatibility/data
New additive migration0005 stores private in-app notifications; upgrades/preserved rows/downgrade/reupgrade verified on SQLite and native PG. No developer/production data
purged or overwritten. Browser tests use disposable DB/accounts and development
OTP, not production mail or PostgreSQL evidence. Judge image base changes to
Ubuntu24.04; rebuild/scan/pin and pass real runtime gate before enabling it.

## Known blockers
Complete original-project harnesses, verified Docker worker/hostile tests,
independent security review, live production integrations, remaining core/gated
workflows and comprehensive browser/device/accessibility/operational acceptance.
Details: RELEASE_CHECKLIST.md, PROJECT_GRADING_MATRIX.md, SECURITY_REVIEW.md and
FINAL_ACCEPTANCE_REPORT.md.

## Autonomous continuation
- Distinct supervisor0/learner1000identities with exact capability policy; actual
  native fixed6check probe, updated real Docker hostile tests (still unexecuted).
- Private notification migration/APIs/menu, export/delete/explicit retention,
  transactionally-created review events; actual PG competing booking/review evidence.
- Connected review booking/detail/human feedback, profile/public portfolio,
  measured Journey/Skills/Analytics/leaderboard and privacy-filtered search.
- Self-hosted pinned Monaco/worker instead of CDN; provider-backed IDE review action
  with disclosure and failure states; larger lazy chunk warning acknowledged.
- AI retries only connection establishment once; never replays accepted paid POSTs.
- Unified test/setup/readiness commands and minimal external user guides supplied.
