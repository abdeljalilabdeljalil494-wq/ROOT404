# Windows 11 operator actions — ordered

Your host is **Windows11**, not native Linux. Use WSL2 Ubuntu24.04 or a disposable
Ubuntu24.04 VM. Docker Engine must run INSIDE Linux with systemd, NOT Docker Desktop's
backend. Keep exact current checkout at `~/ROOT404`, NEVER `/mnt/c/...`.
Do not commit/push, touch the real `.env`, enable public judge, or send secrets.
All repository check scripts write redacted `./reports/` logs/JSON; archive before
rerunning (same check overwrites). PASS means actual command exit0, not certification.

## 1. Prepare WSL2/systemd/Engine/runsc, then hostile isolation
**Needs you:** Windows virtualization/admin rights and a disposable Linux environment.
WSL shares the Windows host: prefer a disposable Ubuntu VM with NO shared folders,
credentials or production workloads for hostile tests/stronger host separation.
WSL results are targeted WSL evidence only. Runtime failure means BLOCKED, not runc fallback.

### A. PowerShell (administrator)
Enable hardware virtualization if Windows requests it; reboot if prompted:
```powershell
wsl --update
wsl --install -d Ubuntu-24.04
wsl --set-version Ubuntu-24.04 2
wsl --list --verbose
```
If distro already exists do not reinstall/unregister it. Create a Linux account.
Use a dedicated disposable distro/VM for hostile execution, not one holding secrets.

### B. Ubuntu shell: systemd and filesystem
Merge these settings into `/etc/wsl.conf` using `sudoedit /etc/wsl.conf` (preserve
other settings; don't duplicate existing sections):
```ini
[boot]
systemd=true
[automount]
enabled=false
[interop]
enabled=false
appendWindowsPath=false
```
Automount/interop restrictions are for the disposable judge distro. Transfer source
BEFORE disabling Windows mounts if using Explorer; never transfer `.env`/keys/dumps.
From PowerShell, save work then `wsl --shutdown` (stops ALL WSL sessions), reopen Ubuntu.
Transfer the EXACT Arena working tree including uncommitted/new files via approved
export/copy, keeping Git metadata needed by validate; do not test a stale remote
base commit. Location `~/ROOT404`. In Ubuntu:
```sh
cd ~/ROOT404
mkdir -p reports
set -o pipefail
{ pwd; ps -p 1 -o comm=; stat -fc %T /sys/fs/cgroup; uname -r; } 2>&1 | tee reports/wsl-environment.log
```
**Expect:** Linux home path, `systemd`, `cgroup2fs`, WSL2 kernel (or VM kernel).
If missing, fix setup/restart; no unsupported-kernel bypass. Full prerequisites,
Docker Engine and Node setup: USER_TESTING_GUIDE.md §WSL prerequisites.

### C. In prepared Linux checkout
Turn OFF Docker Desktop WSL integration for this distro to avoid wrong daemon.
After installing Engine and runsc as documented:
```sh
bash scripts/setup-testing.sh
# Only if runsc not configured, on DISPOSABLE Linux (restarts Docker):
CI=true bash scripts/install_gvisor_ci.sh
ROOT404_DISPOSABLE_HOST=yes bash scripts/test-judge-linux.sh
```
**Expect/check:** exit0, actual hostile tests+runtime report VERIFIED, both empty:
```sh
docker ps -aq --filter label=io.root404.executor=job
docker volume ls -q --filter label=io.root404.executor=job
```
No runtime here has been verified. If WSL kernel/runsc/cgroups fail, repeat on a
clean Ubuntu24.04 VM; do not remove security flags or use Docker Desktop as evidence.
**Send:** reports/wsl-environment.log, reports/test-judge-linux.*, and
reports/judge-isolation/ (versions/kernel/image/source manifest/policy/volumes/result/
acceptance/redacted worker log). WSL version list must show VERSION2; copy nonsecret
PowerShell output into reports/wsl-windows-version.txt before returning bundle.

## 2. Reproduce local suite + full staging stack/browser
**Needs you:** WSL/VM machine; stack needs staging SMTP/TLS/private config and write approval.
```sh
cd ~/ROOT404
bash scripts/validate.sh
```
**Expect:** all gates PASS, reports/validate.*. This uses disposable SQLite/dev OTP;
not real mail or isolation. Windows browsers use http://localhost:5173 for manually
started Vite (see INSTALLATION); test-suite servers start/stop automatically.

For production-mode staging create private file OUTSIDE repo from EXAMPLE ONLY:
```sh
install -d -m700 "$HOME/.config/root404"
test -e "$HOME/.config/root404/staging.env" || install -m600 .env.example "$HOME/.config/root404/staging.env"
# Privately edit staging.env; NEVER the real .env. Set production SMTP/DB/Redis/key,
# exact CORS origin, JUDGE_ENABLED=false, ENABLE_DEMO_FEATURES=false.
export ROOT404_STACK_ENV="$HOME/.config/root404/staging.env"
export ROOT404_TLS_DIR="$HOME/.config/root404/tls"
export ROOT404_STACK_URL='https://YOUR_STAGING_HOST'
.cache/verification-venv/bin/python scripts/report_run.py stack-start docker compose --env-file "$ROOT404_STACK_ENV" -f docker-compose.yml -f deploy/compose.tls.yml up -d --build
bash scripts/test-stack.sh
```
Replace hostname first, provision trusted server.pem/server.key privately (nginx UID
readable) and DNS/firewall; approve migrations/backup first for existing volumes.
**Expect:** migration0007 exits0, services healthy, readiness200. Follow browser
checklist in USER_TESTING_GUIDE, then record ONLY actual outcome:
```sh
bash scripts/record-manual-check.sh stack-browser pass
```
Use fail/blocked instead if needed. Submit remains503/no XP until judge gates close.
**Send:** reports/validate.*, stack-start.*, test-stack.*,
record-manual-check-stack-browser.* + redacted checklist. Never dumps/raw config.

## 3. External services / real OAuth apps
**Needs you:** account/recipient/spend approval. Privately export config from your
secret manager or private staging file, never paste values into shell commands/chat.
Exact probe variables: docs/RC_VERIFICATION.md. Exact Google/GitHub console steps:
docs/OAUTH_SETUP.md. Credentials only backend/env, never VITE_*.
```sh
bash scripts/check-integration-config.sh
export ROOT404_ALLOW_EXTERNAL_PROBES=yes
# ONLY with approval for the bounded paid call:
export ROOT404_ALLOW_PAID_AI_PROBE=yes
bash scripts/test-infrastructure.sh --external
```
**Expect:** authorized live checks VERIFIED; missing values return BLOCKED/exit1.
SMTP acceptance is not delivery without matching actual mailbox receipt. Config
success isn't live verification. Real OAuth requires login/deny/replay/email collision/
explicit-link checks from docs/OAUTH_SETUP.md; then record providers separately:
```sh
bash scripts/record-manual-check.sh google-oauth pass
bash scripts/record-manual-check.sh github-oauth pass
```
**Send:** reports/check-integration-config.*, test-infrastructure-external.*,
record-manual-check-{google-oauth,github-oauth}.* and redacted checklist, never callback queries.

## 4. Phone/tablet over LAN (Windows/WSL networking)
**Needs you:** physical devices, Windows network/firewall admin and trusted HTTPS.
Prefer Windows11 supported WSL mirrored networking for same-LAN reachability, or a
VM bridged onto a trusted LAN. Do not expose WSL ports publicly. Exact setup/options
and rollback are in USER_TESTING_GUIDE §LAN. Do not change firewall automatically.
Open trusted staging HTTPS hostname on phone; execute keyboard/layout/room/report/
mission-disabled-submit checks. Record actual outcome in Ubuntu:
```sh
bash scripts/record-manual-check.sh mobile-lan pass
```
**Expect/check:** valid certificate without warning bypass, readable/responsive UI,
no false save/score/XP; audio/video still coming soon. **Send:**
reports/record-manual-check-mobile-lan.* + OS/browser versions/redacted screenshots.

## 5. Approved subjects and independent reviewer
Nine `docs/subjects/<project>.md` templates exist; supply approved version/statement,
allowed functions/toolchain/ABI/output/edges/scoring. Do not publish hidden answers.
```sh
.cache/verification-venv/bin/python scripts/report_run.py project-grading .cache/verification-venv/bin/python scripts/check_project_grading.py
```
**Expect now:** INCOMPLETE/exit1, all nine disabled. Templates aren't executable
approval; agent retains grader coding/testing. **Send:** approved subjects and
reports/project-grading.*. Neither SECURITY_REVIEW_INDEPENDENT.md nor
SECURITY_REVIEW_JUDGE.md was present; provide approved reviewer findings if available.
Independent sign-off is not replaced by our engineering self-review.
