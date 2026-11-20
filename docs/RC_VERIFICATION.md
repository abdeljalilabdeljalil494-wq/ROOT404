# Release-candidate verification procedures

## Real Docker/gVisor CI
`.github/workflows/judge-isolation.yml` is a real hosted-runner job, not a fake
engine test. It runs on ubuntu24.04 with Docker, installs official gVisor
release20261116.0 with published SHA512 verification, configures systrap (no nested
KVM needed), and requires cgroupv2+seccomp. Missing runtime means failure, no runc
fallback. Modifies only the disposable runner daemon configuration.

The job builds the toolchain image, pushes to a loopback-only disposable registry,
records immutable RepoDigest, creates short-lived local TLS credentials outside
artifacts, and runs the real HTTP hostile harness. Credentials are masked, no
production secrets needed. Audit artifacts whitelist UID/runtime/network/fs/cgroup/
capability settings, not env/source/stdin/Authorization. Final orphan assertion runs
on failure too; cleanup required by CI is itself a failed test, not a pass.

Run on the current branch after publication:
```sh
gh workflow run judge-isolation.yml --ref arena/bf97d7c1-root404
gh run list --workflow judge-isolation.yml --branch arena/bf97d7c1-root404
gh run view RUN_NUMBER --log-failed
```
`RUN_NUMBER` must come from the actual list. Workflow_dispatch may require the
workflow to exist on the default branch; the branch-specific push trigger avoids
silently relying on that. Do not merge to main just to run a test. If GitHub denies
workflow updates/dispatch, retain BLOCKED status and have an authorized maintainer
run the exact branch commit on an approved ephemeral runner. Never request tokens
in chat or create a privileged untrusted-PR/self-hosted workflow.

A green run is targeted CI verification, not independent host escape certification.
Public Judge defaults false regardless of CI. See SECURITY_REVIEW.md for residuals.

## Browser integration
```sh
cd frontend
npm ci
npm run test:e2e
```
Override ROOT404_TEST_PYTHON with your installed Python executable if the default
verification venv path is absent. Requires declared backend dev requirements and
GCC/G++ for other quality gates. Playwright launches its own disposable backend on
8011 and Vite on5181; refuses reuse of unrelated servers/databases. Three Chromium
viewports:1440x1000,820x1180,390x844. Core auth/data are actual API calls; the separate
outage test intentionally aborts one request to verify failure behavior.

Artifacts `.cache/browser-results/` are ignored. Test-only traces may contain
short-lived disposable account tokens/export data; CI retention3days. No production
secret is loaded. Browser OS sandbox disabled for this constrained trusted test
runner, NOT for any judge workload; same-origin web security stays enabled.
Axe scans selected selected login/dashboard/catalog/review/learning/portfolio/Settings states, not every page or manual screen-reader behavior.
Actual mobile devices/Safari/Firefox remain unverified. Unit tests do not replace it.

## Private external staging probes
`scripts/verify_external_integrations.py` requires explicit
ROOT404_ALLOW_EXTERNAL_PROBES=yes. Never prints credential/exception body text.
Configure privately in an ignored file/secret store, not a commit or chat:

| Boundary | Exact required configuration | Check / constraints |
|---|---|---|
| PostgreSQL | ROOT404_VERIFY_DATABASE_URL, sslmode=verify-full and valid sslrootcert in DSN where needed | Read-only TLS and Alembichead0007 check, NO migrations/DDL; staging backup/migration rehearsal separately |
| Redis | ROOT404_VERIFY_REDIS_URL=rediss://... | Certificate-verified TLS/auth, scoped UUID key expires30s and is deleted |
| SMTP | ROOT404_VERIFY_SMTP_HOST, ROOT404_VERIFY_SMTP_FROM, ROOT404_VERIFY_RECIPIENT; optional PORT(default587), SMTP_SSL=true(for465), SMTP_USERNAME, SMTP_PASSWORD | One opt-in message, certificate-verified STARTTLS/SSL; accepted alone remains IMPLEMENTED BUT UNVERIFIED |
| Mailbox receipt | ROOT404_VERIFY_IMAP_HOST, ROOT404_VERIFY_IMAP_USERNAME, ROOT404_VERIFY_IMAP_PASSWORD | Verified-TLS read-only inbox search for unique probe subject; no deletion |
| OpenAI | OPENAI_API_KEY, optional AI_MODEL; ROOT404_ALLOW_PAID_AI_PROBE=yes | One bounded16token non-sensitive call; connectivity/sample response, NOT quality/privacy certification |
| Nginx/TLS | ROOT404_VERIFY_PUBLIC_URL=https://..., optional ROOT404_VERIFY_CA_FILE | Real trusted certificate, HTML root and /api/health+security headers; no disabled verification |
| Executor | ROOT404_EXECUTOR_TEST_URL, ROOT404_EXECUTOR_TEST_SECRET, ROOT404_EXECUTOR_EXPECTED_IMAGE (approved immutable RepoDigest), optional ROOT404_EXECUTOR_CA_FILE; ROOT404_EXECUTOR_ALLOW_HOSTILE_TESTS=yes | scripts/verify_executor.py ONLY on approved isolated staging worker, not public production |

SMTP variable prefix in the table applies to each field: ROOT404_VERIFY_SMTP_PORT,
ROOT404_VERIFY_SMTP_SSL, ROOT404_VERIFY_SMTP_USERNAME, ROOT404_VERIFY_SMTP_PASSWORD.
No placeholders are real credentials. With absent values, external script returns
BLOCKED per integration and exit1; that is not integration-test success. No automatic
production writes/migrations, paid inference or recipient email without opt-in.
Current external probes: BLOCKED (no private configuration), never simulated.

Native local actual PG/Redis/STARTTLS checks remain separately reproducible in
LIVE_SERVICE_VERIFICATION.md; they do not validate production deployment versions.

Current host/protocol details and non-attestation caveat: ENGINEERING_REPORT.md.
Runtime CI additionally inspects bounded tmpfs volumes and performs actual controller
restart/replay rejection. This prepared CI is UNEXECUTED here; no Docker runtime.
