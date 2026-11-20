# Security audit — 2026-11-18

## Release decision: DO NOT DEPLOY TO UNTRUSTED PUBLIC USERS
Zero known dependency advisories does not mean zero application vulnerabilities.
This was a source review plus targeted tests, not a comprehensive penetration test.

## Remediated
- OTP plaintext not persisted: HMAC using deployment secret; atomic attempt limit,
  TTL check and one-time deletion; no verification fallback to development cache.
- Production requires a strong signing key, PostgreSQL and configured SMTP; demo
  seeds/features forbidden. JWT required claims, fixed configured algorithm,
  expiry checks, verified active user and shared persistent revocation.
- OTP email throttles shared through SQL. Login has auth limiter; raw forwarded
  headers cannot change its key. HTTP auth/rate-limit headers preserved.
- Seed endpoints admin-only, room content member-only, private joins fail closed.
- Peer score bounds and repeat-review conflict; project rewards only first pass.
- Judge does not execute code inside API, fabricate scores or mount Docker socket.
  HTTP executor result is size/schema checked, redirects disabled; hidden test
  inputs/expected/actual outputs are not included in public evaluation results.
- Removed unconfined container profiles/default production passwords; one-shot
  CLI network_mode:none, non-root, read-only image, caps dropped, resource limits.
- SQL bound values hidden in SQLAlchemy error messages. Config secrets not copied
  into docs. Filled env files ignored; root .env inspected was whitespace only.
- Audited dependencies upgraded; `npm audit` and declared-requirements `pip-audit`
  both zero known vulnerabilities on this run. Retest continuously.

## Boundary review
| Risk | Findings and residuals |
|---|---|
| SQL injection | ORM bound parameters; tested search/invalid inputs. Not every query fuzzed. |
| XSS | React text rendering; token remains in localStorage (residual impact if XSS); no rich-HTML security guarantee. Marketing/legacy UI not exhaustively tested. |
| CSRF | Authorization bearer is explicitly attached; no cookie auth. X-Requested-With is not treated as a CSRF defense. |
| Auth/IDOR | Targeted route/member/revocation tests. All subsystem permissions and multi-tenant cases not exhaustively verified. |
| SSRF | Executor URL operator-configured, AI URL fixed; no user-controlled target. Admin must restrict executor egress/URL. |
| Traversal/injection | Filename/size checks, argv execution without shell in new primitive. Regex source-code bans are defense-in-depth only, never sandbox isolation. |
| Untrusted code | CRITICAL RELEASE BLOCKER: dedicated Docker/runsc controller implemented but no runtime/hostile/independent isolation verification. Resource-limit subprocesses must not accept public submissions on a shared host. |
| Rate limits | OTP/email and configured IP/auth/Judge controls now use shared SQL; atomic fixed windows verified across SQLite threads/processes. Per-account AI hourly cap shared across ask/review. No process-memory fallback. Target deployment PostgreSQL load, scheduled cleanup and trusted edge/DDoS controls still needed. |
| Abuse | Repeat project/review awards closed; full concurrent PostgreSQL validation, collusion, Arena integrity, coalition permissions and exam integrity unfinished. |
| Secrets | No live root-env credential identified; historical Git/external secrets not scanned. Rotate any credentials previously committed/exposed. Never paste keys in chat. |
| Upload/deserialization | No new binary upload or pickle path added; JSON source inputs bounded. Full streaming/chunked HTTP body enforcement still needs work. |
| Privacy | Public portfolio exposure/consent and account deletion policies need review. Logs/retention/backups need operational validation. |

## Verification limits
Actual native PostgreSQL16.2, Redis8.10.3 and local SMTP STARTTLS/API delivery are
now verified locally. External SMTP/OpenAI, Docker/runsc/seccomp/AppArmor, hostile
network/fork/memory/escape and full browser XSS/accessibility remain unverified. Do not interpret compose settings or the trusted runner tests as an
isolation assessment. Production must keep JUDGE_ENABLED=false until that work is complete.

## Reconciliation follow-up
Provider advice no longer contains fabricated random review grades. Owner-only
successful interaction history and SQL account budgets are tested using HTTP
test doubles. Account deletion/export and retention CLI now exist; backup/provider erasure,
operator scheduling and consent/legal review remain outstanding; review code
is not separately persisted, but user questions/provider output may include it.
Mentor UI shows provider failures and uncertainty rather than scripted responses.
Migration0004 verified on SQLite and actual local PostgreSQL16.2; no new production-security claim is made.

## Production-engineering checkpoint
113backend+6controller tests and30frontend tests pass; refreshed npm and backend/
controller requirements audits report0known findings. Controller uses fixed policy,
required gVisor/cgroupv2/seccomp, no host bind/socket/secrets and cleanup failure
quarantine, but NONE of this is runtime isolation evidence without Docker tests.
Privacy defaults/recent-auth/export/deletion/session epoch/log filtering are tested;
selected real PostgreSQL integration passes. See docs/PRIVACY_RETENTION.md and
docs/LIVE_SERVICE_VERIFICATION.md. No independent production security audit exists.
