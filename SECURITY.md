# ROOT404 security and verification policy — 2026-11-18

**Do not deploy to untrusted public users yet.** No production security verification,
pentest or sandbox isolation certification has been completed. A passing dependency
audit or a hardened Compose setting is not a security guarantee.

## Implemented controls (targeted local tests)
- SQL-backed HMAC OTP storage, TTL, attempt limits and atomic one-time consumption;
  SMTP SSL/STARTTLS with failure invalidation, never a production development bypass.
- Required/expiring JWT claims, active verified accounts, SQL logout revocations;
  production strong-key/config validation and no demo seeds/features.
- Shared atomic SQL fixed-window request budgets for configured IP/auth/judge
  controls; separate OTP email and per-account AI hourly budgets. SQL storage
  failures do not enable a memory fallback. Forwarded-IP trust is explicit.
- Targeted ownership/admin/room-member enforcement and repeat-reward protection.
- Bounded authenticated HTTP judge/provider clients, no redirect following/proxy
  environment, no API-host execution of submitted code, no fabricated test success.
- Ask/review provider advice is not executed validation. Cheating/similarity and
  complexity checks are lexical heuristics, not proof; no paste-based automatic penalty.
- Production demo fixtures disabled. Hiring/exam/mentorship prototypes gated at router.

## Critical residuals
1. **Untrusted code:** dedicated dispatcher implemented but Docker/runsc unverified. CLI subprocess limits
   are insufficient isolation. Keep JUDGE_ENABLED=false. Never mount Docker socket
   into API/jobs, enable unconfined seccomp/AppArmor, share host secrets or grant
   network access. Test non-root, network/filesystem denial, CPU/memory/PIDs/wall/
   output limits, cleanup and escape resistance on real infrastructure first.
2. Native PostgreSQL16.2 migration/concurrency/restore, Redis and local STARTTLS
   delivery are verified locally, not production. Target deployment/proxy/TLS and
   Internet recipient delivery remain unverified. Route limits are not a global body-size/edge/DDoS shield.
   SQL budgets require cleanup and high-volume testing; fixed windows allow bursts.
3. localStorage bearer tokens remain vulnerable to XSS impact. Full authorization,
   content moderation, anti-collusion, rate/body-size and browser security review
   remain open. React text escaping is not complete XSS assurance.
4. User questions and provider responses persist. Raw review code is not separately
   retained, but advice/questions may include it. Provider receives supplied context.
   Account deletion/export and retention CLI exist; operator backup/provider
   erasure, consent and spending/quality controls remain incomplete.
   Do not submit credentials or private code without an approved processing policy.
5. Demo-gated screens and stub external-service tests are not production workflows.

## Secrets and operations
Use ignored private env files or a managed secret store; examples contain no real
credentials. Never send keys in issues/chat. Rotate any credential previously
committed or exposed; historical Git/external secret scanning is not complete.
Restrict trusted proxy CIDRs and executor targets; back up/rehearse restore before
schema changes. Schedule expired auth-state cleanup and define logging/retention,
alerts, TLS termination and incident response before release.

## Reporting and evidence
Report vulnerabilities privately through the repository's private security advisory
channel if enabled, otherwise contact maintainers privately; do not publish exploit
credentials or user data. See SECURITY_AUDIT.md for reviewed risks,
docs/VERIFICATION_RESULTS.md for executed tests and PRODUCTION_READINESS.md for
release gates. Actual local PostgreSQL/Redis/STARTTLS tests ran; Docker hostile-code and deployed
production security tests did not. See docs/LIVE_SERVICE_VERIFICATION.md.

Account/private-directory defaults, session epoch revocation and recent-auth bounded
export/deletion are now tested. SecretFilter suppresses arbitrary error detail and
redacts known credentials/email/bearer/URLs. These are defense-in-depth, not complete
DLP/privacy/security assurance; see docs/PRIVACY_RETENTION.md.
