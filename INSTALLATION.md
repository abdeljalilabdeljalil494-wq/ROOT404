# Native Linux installation — private beta

Python3.11 (tested), Node22.12+, npm, GCC/G++, Bash. Use declared dependencies;
never point tests at learner/production data. Real `.env` is not edited or copied.
```sh
bash scripts/setup-testing.sh
bash scripts/validate.sh
```
Reports:reports/setup-testing.*, reports/validate.*. Local Chromium uses locked
packaged binary; missing OS libraries must be installed per your distribution.
These are trusted tests, not permission to execute arbitrary code on the host.

## Development servers (separate disposable local database)
```sh
export ENVIRONMENT=development EMAIL_PROVIDER=development JUDGE_ENABLED=false
# Disposable trusted-local test only; otherwise configure SMTP and leave false.
export ENABLE_DEV_OTP=true
export DATABASE_URL="sqlite:////tmp/root404-local-dev.db"
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
.cache/verification-venv/bin/python -m alembic -c backend/alembic.ini upgrade head
PYTHONPATH=backend .cache/verification-venv/bin/python -m app.manage seed-catalog
PYTHONPATH=backend .cache/verification-venv/bin/python -m app.manage seed-execution-projects
PYTHONPATH=backend .cache/verification-venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Keep exported variables in that terminal; do not print/save secrets to reports.
Use another terminal for `cd frontend && npm run dev -- --host 0.0.0.0`.
Open5173; browser API is relative `/api`, Vite proxies to8000. Do not put backend
localhost into browser code. Binding0.0.0.0 with ENABLE_DEV_OTP=true exposes development OTP on reachable
interfaces; firewall to trusted local test clients only. Never use development OTP
or mock flags for a real private beta.

Current schema0007. No production create_all/stamp. Production/staging setup,
SMTP/TLS and migrations: DEPLOYMENT.md and USER_ACTION_REQUIRED.md.
Original catalog has descriptions, NOT executable grading specifications; templates
are in docs/subjects. Foundation suites are separate. Judge remains disabled.

Windows11: run the Linux steps inside WSL2 Ubuntu24.04 or disposable Ubuntu VM;
project in Linux home, not /mnt/c. USER_TESTING_GUIDE.md has exact prerequisites.

## Configuration sources
Canonical Compose/root template: `.env.example`; standalone backend template:
`backend/.env.example`; browser build template: `frontend/.env.example`. Never
fill templates with real secrets or track copied private files. Backend Settings
can load `.env` from its working directory; exported environment wins. Development
OTP disclosure is independently off by default, forbidden outside development,
and must never be used for beta/public auth. With development email and no
OTP opt-in, mail is not delivered: choose SMTP or explicit disposable-local opt-in.
Vite proxy target must be exported in the frontend server terminal, for example
`VITE_API_TARGET=http://127.0.0.1:8000 npm run dev -- --host 0.0.0.0`.
The current Node config intentionally uses exported `process.env`; merely putting
VITE_API_TARGET in a frontend env file does not configure the proxy. Browser calls
remain relative `/api`; localhost here refers only to the development server host.
