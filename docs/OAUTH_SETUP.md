# Google/GitHub OAuth — implemented, NOT externally verified

No app credentials have been used. Local tests use provider doubles and locally
signed RSA tokens; they do not prove provider console/callback/browser behavior.
Email OTP remains available; no existing email account is ever auto-linked.

## Google Cloud Console
1. Choose/create your staging project; open Google Auth Platform (OAuth consent
   screen). Configure app name/support contact, audience and authorized domain.
2. While in Testing, explicitly add each authorized test user's Google account.
   Request only `openid`, `email`, `profile`; review production verification rules
   before changing publishing status. No Google API key substitutes for OAuth.
3. Clients → Create client → Web application. Add the exact HTTPS frontend origin
   as authorized JavaScript origin. Add exact redirect URI:
   `https://YOUR_HOST/oauth/callback/google` (no wildcard/query/trailing slash).
4. Store client ID/secret privately as GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET;
   GOOGLE_REDIRECT_URI must exactly match the registered URI. Do not paste values
   into chat, git, screenshots, commands/history or frontend VITE_* variables.

## GitHub Developer Settings
1. Settings → Developer settings → OAuth Apps → New OAuth App (not a PAT/GitHub App).
2. Homepage URL is your exact HTTPS frontend origin. Authorization callback URL:
   `https://YOUR_HOST/oauth/callback/github`.
3. Generate client secret, save privately as GITHUB_CLIENT_SECRET and ID as
   GITHUB_CLIENT_ID; GITHUB_REDIRECT_URI must exactly match the callback above.
4. Use a test account with a primary verified email; ROOT404 refuses unverified or
   missing primary email. Requested scopes: read:user and user:email.

## Deployment and manual acceptance
Privately export environment variables or use a mode0600 file OUTSIDE checkout.
Compose passes secrets only to backend/migration, never frontend build. Callback
must stay same-origin with API so HttpOnly SameSite=Lax browser cookie is sent.
Use TLS; production cookies are Secure. Browser callback scrubs code/state from
history and POSTs to API; never log or share its query or tokens. At most one pending
flow per browser cookie (starting another invalidates the browser binding of the old one).

- New identity: Login → Google/GitHub → consent → dashboard, one account.
- Repeat login: same account, no duplicate identity/user.
- Existing email: error directing email login first; Settings → explicitly Link.
- Linking: sign in <10min ago, same active session throughout; cannot attach another
  user's identity or replace an already linked provider.
- Deny consent: visible failure, no account/token created.
- Alter/reuse callback state: rejected; expired >5min flow rejected.
- Revoke all sessions during linking: callback rejected.

No refresh/access/provider token is retained. Identity (provider, immutable subject)
is stored in schema0006; owned export includes it and deletion cascades it.
For local development only, exact localhost HTTP callback is allowed. Native LAN
and real private beta should use trusted HTTPS; do not disable certificate checks.

Record each provider separately with `scripts/record-manual-check.sh` (see user
guide). Outcome is operator-reported, not independent security certification.
