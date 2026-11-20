# ROOT404 next-round engineering report

## Decision / preservation
NOT PRODUCTION READY. Continued arena/bf97d7c1-root404 in place. No commit/push,
no real `.env` read/modify/print, public judge disabled. Existing architecture/data
preserved. Current migration0007. No external review files were present.

## Implemented and verified local boundaries
- Executable daily mission reuses authoritative supplied foundation Stream Sum
  Python spec, not any original project. Trusted owned same-day successful DB
  submission only; daily unique ledger+XP commit, PostgreSQL account lock.25XP/day.
- Four measured current-record badge criteria and capped transparent reputation;
  distinct reviewed authors/self exclusion, no badge XP or client reward authority.
  APIs/portfolio/UI connected; policy in docs/BETA_REWARDS_MODERATION.md.
- Room reports membership/author/duplicate validation, private owner/admin queue,
  non-conflicted staff remove/dismiss CAS. Message-level removed_at persists after
  reporter deletion; exports hide reviewer IDs. Explicit host-only admin provisioning
  revokes sessions. Report body never interpreted as markup/executable content.
- Sequential visible-tab room5s/queue10s polling; slow-request/unmount tests.
- Browser tests now include actual member reporting/private queue/separate staff UI
  removal at three viewports. Existing auth/settings/peer/notification tests retained.

## Actual results
Final validate PASS:206backend/controller,4warnings;45frontend/13files;9Chromium
(~1.8min), lint/build/npm audit0known/compile/whitespace. reports/validate.*.
Native actual PG0007 migration/preserved rows/dump/restore/API/review races and
four simultaneous mission claims (one25XP winner), Redis and verified local
STARTTLS:10checks PASS. Success records are trusted fixtures, NOT executed learner
programs or Docker/isolation proof. No failing tests skipped/weakened.

## Judge architecture/gates retained
Trusted HostSupervisor outside compile/run containers; job image only UID1000
launcher/no caps. No supervisor keys/process/IPC/socket/hidden expected outputs
mounted into jobs. Host captures bounded bytes, independently reads Docker exit/
OOM state, enforces deadlines and bounded inspected tmpfs workspace+cleanup.
TLS+bearer and v2 HMAC receipts bind fresh ID/job/stdin/time/image/observations,
SQLite claims reject replay, backend rejects contradictions and scores hidden tests.
Dedicated Docker daemon authority is root-equivalent; no claim of host compromise
resistance or impossible escape. **Signature is not execution attestation.**
Actual Docker/runsc/WSL hostile/runtime enforcement remains BLOCKED/UNVERIFIED.

## Scope limits
All nine originals lack authoritative statements: templates reviewed, empty trusted
adapter registry/hard503 retained. No grader invented; foundation mission isn't a
substitute. Google/GitHub/OpenAI/external SMTP/targetPG+Redis/NginxTLS not verified
with real private accounts/target. No independent findings supplied; BUGS_AND_FIXES
separates intake from self-review fixes. Basic room moderation isn't automatic
classification, all-resource moderation, appeals/SLA or sybil/collusion assurance.

## Windows11 handoff
Rewrote both operator runbooks for WSL2 Ubuntu24.04/systemd/Engine INSIDE WSL/runsc,
Linux-filesystem checkout, Desktop integration off, scoped LAN/TLS and VM fallback.
No WSL install/runtime success is claimed. Stronger hostile host separation uses
disposable VM without Windows mounts/shared folders/secrets. Reports remain redacted
and ignored; real.env/OTP/tokens/backup archives must not be shared.
