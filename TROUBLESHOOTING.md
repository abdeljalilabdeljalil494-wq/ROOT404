# Troubleshooting

- **Page says integration in progress:** preserved legacy demo screen. It is not
  yet wired to real APIs. Enable explicit development demo only for UI review.
- **No OTP email in development:** the default development provider deliberately
  sends nothing; local API response has dev_otp. Configure SMTP for actual delivery.
- **SMTP 503:** configure provider/host/from/TLS/auth and check outbound connectivity.
  Failed delivery invalidates the challenge. Registration can create an account
  before delivery fails; request a fresh code, do not repeatedly register it.
- **Expired/invalid code:** request a new one. Codes are consumed once, expire after
  ten minutes and lock after five attempts; do not bypass these safeguards.
- **429:** honor Retry-After; SQL email quota is five/hour. Multiple workers still
  have separate general/IP throttles; use a trusted distributed edge limiter.
- **Unexpected session invalidation on restart:** configure a persistent SECRET_KEY.
  Development without one generates a fresh key each process. Logout revokes token.
- **Judge 503:** expected without the missing isolated executor or executable suite.
  Do not turn on a flag to fabricate results or run code in the backend process.
- **AI 503:** provider disabled/missing key/unreachable. No canned fallback. This
  environment restricts outbound provider access.
- **Production startup rejects schema:** run/rehearse Alembic migrations; do not
  call create_all or stamp an uninspected database.
- **CORS config error:** comma-separated origins or JSON list accepted, never `*`
  in production. Configure actual frontend origin, not the backend hostname.
- **Remote preview cannot call API:** browser calls must be relative `/api`; Vite
  proxies internally, both servers bind 0.0.0.0. Do not expose localhost to browser.
- **Build needs newer Node:** use Node 22.12+ and npm ci from frontend/.
- **Container failures:** not runtime-verified in this environment. Inspect Compose
  logs, permissions/tmpfs, schema version, DB/Redis health and Nginx config before
  assuming the static Compose checks prove startup.

## Private-beta additions
- **Compose API not starting:** inspect migration service status locally (never
  share raw env/config). It must exit0 at0006; restore backup and resolve migration
  errors, never stamp/create_all production. Docker path not executed in this lab.
- **OAuth503/startup rejects config:** absent provider credentials disable it;
  partial production ID/secret/URI fails startup. Exact HTTPS callback path required;
  docs/OAUTH_SETUP.md has console steps. Backend vars, never VITE_* secrets.
- **OAuth409 email exists:** login by email OTP, then Settings→Link with recent
  session. This is intentional takeover protection, not a duplicate-account bug.
- **OAuth400 state:** same browser, start fresh flow;5min expiry, single-use, cookie
  binding. Other tab/hostname or absent Secure cookie may invalidate flow. Never
  relax state checks or share callback queries.
- **OAuth502:** provider/signature/claims/verified-email check failed. Report only
  status/type/provider, not provider bodies/tokens. Real apps remain UNVERIFIED.
- **No mission XP:** Daily Missions are suggestions/coming soon, not executable
  graders. Submit503 must not award XP. Coalition totals derive active accounts,
  not persisted historical demo scores. Wars are not available to ordinary users.
- **Where reports are:** ignored reports/*.log/json. PASS means command exit0;
  inspect gate scope. Manual checks explicitly operator-reported. Files may include
  disposable test identifiers; review before sharing. Never upload backups/traces
  containing private accounts, OTPs, OAuth callback params or access tokens.
