# Private staging deployment — NOT production-ready

Use native Linux Docker Engine + Compose plugin. Actual Docker/Nginx/TLS/restore
execution is UNVERIFIED here. Never expose public submissions; judge stays disabled.
See USER_ACTION_REQUIRED.md for exact staged commands and required reports.

## Private configuration, not real .env
Use a secret manager or mode0600 file OUTSIDE checkout. Required:
- ENVIRONMENT=production; stable random SECRET_KEY>=32characters.
- POSTGRES_USER/DB and strong unique POSTGRES_PASSWORD, REDIS_PASSWORD. Hex values
  avoid URI escaping issues; otherwise percent-encode DATABASE/Redis URI credentials.
- SMTP_HOST/FROM/TLS/port/auth and authorized test recipient. Never dev OTP in beta.
- CORS_ORIGINS exact HTTPS frontend origin. ENABLE_DEMO_FEATURES=false,
  SEED_DEMO_DATA=false, JUDGE_ENABLED=false, AI_PROVIDER=disabled unless approved.
- Optional Google/GitHub ID/secret/exact callback URI: docs/OAUTH_SETUP.md.
  Absent disables provider, partial/unsafe production configuration fails startup.
- Optional OpenAI explicit budget/consent, retention and privacy policy.

Compose API depends on healthy PostgreSQL/Redis AND successful explicit Alembic
migration service at head0007. `up` changes STAGING schema; operator authorization
and prior backup/restore rehearsal required. Never point initial tests at production
volumes. Existing fixed container names mean one stack per host; refuse collisions.
Docker image/database major upgrades and image digest approvals remain operator tasks.

Base Compose publishes HTTP only on127.0.0.1:8080. Trusted TLS override:
`-f docker-compose.yml -f deploy/compose.tls.yml`; privately configure ROOT404_TLS_DIR
with server.pem/server.key (readable by nginx UID, not world-readable). Certificate
must cover real frontend hostname. TLS1.2/1.3, HSTS, CSP and no callback access logs
are configured, but Nginx syntax/runtime/certificate behavior are UNVERIFIED here.
No secrets in frontend VITE_* build arguments. No database/Redis public ports.

## Operations/monitoring
- `/health`: liveness; `/ready`: database/Redis readiness,503 on failure. Same-origin
  frontend proxies `/ready`. Run scripts/test-stack.sh; configure external monitoring
  for readiness, TLS expiry, DB/storage/backup age and paid-provider budget alerts.
- Docker json-file logs bounded10MiB×3 per long-lived service. App request logs do
  not include bodies/query tokens; no raw inspect/compose-config output in reports.
  Persistent centralized alert delivery/monitoring is NOT deployed/verified.
- Backup `scripts/backup-stack.sh`; isolated fresh-DB restore rehearsal
  `scripts/restore-drill.sh`. Archives are SENSITIVE and unencrypted: encrypt/store
  outside checkout and reports; enforce operator retention. No production overwrite.
- Retention is explicit, never silent startup purge: docs/PRIVACY_RETENTION.md.
- No automatic downgrade for rollback. Restore a reviewed backup to new storage
  and test app/revision/data before operator traffic switch; never stamp schema.

## Dedicated judge worker
Separate host-only dispatcher with Docker root-equivalent authority, TLS/firewall
restricted to backend. Job image has only non-root launcher, no supervisor secret,
host IPC or socket mount. Protocol v2 signed host observations/replay checks are not
execution attestation. Immutable JUDGE_EXPECTED_IMAGE required before any approved
future enablement. Actual runsc+hostile+grading+independent gates must close first.
One command after prerequisites: scripts/test-judge-linux.sh (operator runbook).

## Release criteria
PRODUCTION_READINESS.md remains NOT READY. Successful Compose start/config check
is not isolation proof, grading certification, independent security review or
production acceptance. No deployment/production migration was performed by agent.

Windows11 operators must run these Linux Engine commands in WSL2 Ubuntu24.04 with
systemd or a disposable Ubuntu VM, not Docker Desktop. See corrected operator guides.
