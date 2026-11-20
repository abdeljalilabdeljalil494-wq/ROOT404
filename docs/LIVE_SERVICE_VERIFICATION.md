# Live-service verification evidence — 2026-11-18

These are **actual local services**, not production deployments or independent
verification. No SQLite result is counted as PostgreSQL evidence. No SMTP stub
is counted as delivered mail. No Docker result is inferred from source settings.

## Executed successfully
Command, from root with explicit local disposable-DB provisioning access:
```sh
.venv/bin/pip install -r backend/requirements-dev.txt -r requirements-integration.txt
ROOT404_PG_ADMIN_DSN='host=/tmp port=55432 user=root404 dbname=postgres' \
  .venv/bin/python scripts/verify_infrastructure.py
```
Provision a disposable local PostgreSQL admin on55432, authenticated Redis on56379
and the loopback STARTTLS sink on5587 first. Redis credentials live in ignored
`.cache/infrastructure/verify.json` under `redis_url`; do not commit them. SMTP CA
is `.cache/infrastructure/smtp.pem`, private key `.cache/infrastructure/smtp.key`.
Run `scripts/local_smtp_sink.py` only for local integration. The verifier creates
and drops ONLY randomized `root404_verify_*` databases/roles, never an existing
application DB. Ports/paths intentionally target a local lab, not arbitrary prod.

| Boundary | Actual evidence |
|---|---|
| PostgreSQL16.2 | Native process supplied by pgserver0.1.4, TCP/password-authenticated app role, UTF8 database |
| Alembic | Fresh0001; inserted row;0001->0004; exact head/row assertion; downgrade/re-upgrade |
| PostgreSQL backup/restore | Real pg_dump/pg_restore into a second disposable DB; row/head retained |
| Shared throttle |32 concurrent requests across8threads; exactly5 accepted by atomic PostgreSQL upsert |
| OTP |16 concurrent PostgreSQL attempts; exactly1 successful consumption |
| Production configuration | App startup verifies migration head (no create_all); ready200 against actual SQL/Redis |
| Authentication flow | API login -> real SMTP STARTTLS -> private local mailbox -> code verification -> replay400 |
| Privacy/data | Actual PostgreSQL export/history; private portfolio404; deletion401 afterwards; FK cascade deletes owned history, preserves second user |
| Redis8.10.3 | Built from official tagged GitHub source; requirepass, separate clients read/write and app readiness |
| Redis persistence | Actual process stop/start; AOF restored the test key; verified then removed |
| SMTP | Real aiosmtpd1.4.6 server; certificate-verified STARTTLS; delivered message headers/body verified in private local mailbox |

Redis emitted a host memory-overcommit warning. No host sysctl was silently changed.
Native PostgreSQL16.2 is a lab dependency, **not an approved production patch**;
Compose targets PostgreSQL15, whose exact deployment image/version is not tested
by this lab. Test supported current patches in staging. No HA/failover, scale,
crash recovery, production secret store or operator restore drill was verified.

## Not executed / blocked
- `docker version` exits127: Docker absent. No gVisor runtime, built job image,
  real job HTTP service, container concurrency or hostile isolation tests ran.
- GitHub binary download redirected to a disallowed release-assets host; alternative
  PostgreSQL binary came through the declared PyPI verification dependency.
- OpenAI egress is outside this sandbox's host allowlist; no configured provider
  key was used. Provider integration remains MockTransport-only, not live evidence.
- SMTP delivers to a local sink, NOT an external recipient. No MX/DNS/reputation,
  external account, bounce or Internet mailbox receipt claim is made.
- API calls use TestClient against real services; no browser or deployed Nginx/TLS
  end-to-end journey. Certificates in the lab are locally trusted test certs only.

Ephemeral logs: `/tmp/root404-real-infrastructure-final.log`. The tracked evidence
is this bounded description and executable verifier, not credentials or raw mail.
Generated service data/builds/certs stay under ignored `.cache/`.


## Autonomous continuation rerun
Current head0005 (private notifications) migrated/preserved/downgraded/reupgraded and
restored successfully on the actual PG16.2lab. Harness now passes9checks, including
simultaneous same-owner overlapping slot publications (200/409), competing authors
booking one slot (one200), concurrent final human review (200/409), exactly one70
point award and3transactional private alerts. This is actual PostgreSQL behavior,
not SQLite or mocks. Fixtures are failed submissions, not claimed judge execution.
No target production version/TLS/deployment/operator restore drill is implied.
