# ROOT404 frontend — contributor guide

React18, Vite, Tailwind and Monaco; Node22.12+. Preserve ROOT404 branding and
feature boundaries. Local tests are not a production UI certificate.

```sh
cd frontend
npm ci
# Exported Node-config target, NOT an import.meta.env/browser URL.
VITE_API_TARGET=http://127.0.0.1:8000 npm run dev -- --host 0.0.0.0
npm run lint
npm test
npm run build
npm run test:e2e
```

Use Windows11 through WSL2 Ubuntu or a disposable Ubuntu VM, in Linux home.
Backend setup: ../INSTALLATION.md. Browser requests remain relative `/api`,
with Vite proxying server-side. `VITE_API_TARGET` must be **exported in the server
shell**; writing it only in `.env` does not set the current Node proxy config.
Default target is http://localhost:8000. Never put sandbox localhost into browser
API code. Nginx production runtime remains a separate unverified gate.

Real API is default. Mock data requires both development mode and explicit
`VITE_USE_MOCK=true`; never fallback to demo after an HTTP error. Development
OTP display requires backend `ENVIRONMENT=development` AND `ENABLE_DEV_OTP=true`.
SMTP/beta must keep it false. Tests opt in only against disposable databases.

## Current integration / boundaries
Auth/protected shell, dashboard, projects/editor, Mentor and Settings call real
API services with loading/empty/error states. Mentor requires a real configured
provider, does not fabricate answers and is not execution/scoring evidence.
Workspace is lazy-loaded; successful learner evaluation remains disabled pending
secure external executor acceptance and approved subject suites. Editor drafts
are not promised as durable offline autosave. Attachments/shared editing/WebRTC
are not completed features.

Rooms have basic persistent private text chat and API moderation/removal polling.
Peer-review slots/booking/final review, notifications and progress/badges have
API-backed selected workflows; human review does not replace judge results.
Settings supports privacy preferences, private owner export, session revocation
and confirmed deletion. Export/delete require recent sign-in; backup/provider
instant erasure is not promised. PrototypeFeature gates are not completion.

Unit/service tests include real-default/no-offline-fallback,401,429, filename
parity and settings wire-format coverage. Packaged Chromium E2E uses disposable
API/Vite at desktop/tablet/mobile viewports, including real auth, room/review,
settings and outage flows. No mock judge success is accepted as learner evidence.
For exact latest executed counts/gates see ../FINAL_ACCEPTANCE_REPORT.md and
../EXTERNAL_REVIEW_TRIAGE.md, not hardcoded historical README totals.
This is not complete accessibility/mobile/provider/TLS certification.
