# Windows11 → WSL2 Ubuntu24.04 / disposable Ubuntu VM testing

Not production-ready. Keep public judge disabled; never read/modify/share real
`.env`. USER_ACTION_REQUIRED.md gives ordered tasks/expected artifacts. Repo and
node_modules/venv/Docker storage belong on Linux filesystem (`~/ROOT404`), NOT
/mnt/c, a Windows network share, or a Docker Desktop bind mount.

## WSL prerequisites (after systemd steps in user action file)
Run inside disposable Ubuntu24.04, not PowerShell. WSL2+systemd+cgroupv2 required.
Docker access is root-equivalent. Do not configure a valuable personal distro as a
hostile-code worker. VM option: Ubuntu24.04 x86_64, systemd, no shared folders or
credentials; same Linux commands apply, no WSL settings needed.

### Docker Engine inside Ubuntu (official apt repository)
On a NEW disposable distro; if existing Docker packages/daemon are installed,
review conflicts first, do not blindly uninstall/overwrite your working setup.
```sh
cd ~/ROOT404
mkdir -p reports
set -o pipefail
(
  set -e
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl git build-essential python3-venv python3-dev xz-utils
  sudo install -m0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
) 2>&1 | tee reports/wsl-docker-install.log
```
Close Ubuntu, save other WSL work, run PowerShell `wsl --shutdown`, reopen Ubuntu.
Docker Desktop WSL integration must be OFF for this distro. Confirm daemon is local:
```sh
cd ~/ROOT404
set -o pipefail
{ docker context show; docker version; docker compose version; systemctl is-active docker; docker info --format '{{.OperatingSystem}} {{.CgroupVersion}}'; } 2>&1 | tee reports/wsl-docker-status.log
```
Expect systemd Docker active, Ubuntu Linux Engine (not Docker Desktop), cgroup2.
Do not set DOCKER_HOST to a remote/Desktop daemon or mount its socket into jobs.
Ubuntu24.04 default Python3.12 is not the lab's tested Python3.11; actual WSL suite
must verify that interpreter/dependencies. Missing OS libraries must be fixed, not
used to skip tests. Native Windows Python/npm must not be mixed into Linux PATH.

### Node22.x Linux and declared dependencies
If `node --version` already shows supported22.12+ Linux Node, keep it. Otherwise
install Node22 using your approved package manager, or official current Linux x64
release with published checksum (commands fetch no credentials):
```sh
cd ~/ROOT404
set -o pipefail
(
  set -e
  test "$(uname -m)" = x86_64
  work=$(mktemp -d)
  trap 'rm -rf "$work"' EXIT
  cd "$work"
  curl -fsSLO https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt
  archive=$(awk '$2 ~ /^node-v22\..*-linux-x64.tar.xz$/ {print $2; exit}' SHASUMS256.txt)
  test -n "$archive"
  curl -fsSLO "https://nodejs.org/dist/latest-v22.x/$archive"
  grep "  $archive$" SHASUMS256.txt | sha256sum -c -
  mkdir -p "$HOME/.local/node22"
  tar -xJf "$archive" --strip-components=1 -C "$HOME/.local/node22"
) 2>&1 | tee reports/wsl-node-install.log
export PATH="$HOME/.local/node22/bin:$PATH"
node --version | tee reports/wsl-node-version.log
bash scripts/setup-testing.sh
bash scripts/validate.sh
```
Persist PATH in your Linux shell profile only if this install was needed. Checksum
checks transport corruption; use your organization's release-signature policy for
stronger package provenance. Node installation/runsc/WSL paths UNVERIFIED in this lab.

### runsc and actual isolation
`CI=true bash scripts/install_gvisor_ci.sh` installs pinned official runsc/configures
systrap and restarts Docker ONLY on disposable worker. Then:
`ROOT404_DISPOSABLE_HOST=yes bash scripts/test-judge-linux.sh`.
Reports include actual runtime/kernel/image/hostile assertions. Missing WSL kernel
capability means BLOCKED; move to disposable VM, never runc or privileged fallback.
Expected no labeled containers/volumes afterward. Real .env/Windows drives/socket
must not be mounted into learner containers. HMAC is not execution attestation.

## Automated regression evidence and reports
`bash scripts/validate.sh` runs actual disposable backend, frontend tests/lint/build,
Chromium at desktop/tablet/mobile widths, compilation/audit/whitespace. Reports in
reports/validate.log/json. Isolated development OTP is allowed ONLY test process;
not real external SMTP evidence. Browser no-sandbox is test tooling, not judge proof.
Background room5s/queue10s polling skips hidden tabs, doesn't overlap, stops on unmount.
Reports overwrite same name; archive redacted reports first. Never share raw traces
that contain tokens/private data, raw docker inspect/config or backup archives.

## Manual stack browser checklist (actual authorized SMTP)
1. Register unique account→actual email OTP→login. Wrong/expired code fails; no
   production dev_otp. Logout/revoke-all invalidates sessions, other account isolated.
2. Dashboard→project→editor; public judge disabled→submit503, no score/progress/XP.
3. `/progress`: executable mission links to supplied Stream Sum Python spec. Claim
   stays disabled without today's owned trusted success. No mock execution to unlock.
   Once judge gates eventually close, actual success allows one25XP claim/day; repeat
   must409. This positive runtime journey is BLOCKED here. Badges/reputation show
   documented measured policy, no arbitrary update button or repeated-read rewards.
4. Rooms: create/join/send; second browser receives via polling, edit draft survives
   refresh. Nonmember cannot read history. Report another member's message; own
   `/moderation` shows status, outsiders see none. Separate non-conflicted admin can
   remove/dismiss; removed message disappears in both clients after polling. No staff
   role self-assignment UI. Existing admin must be provisioned via approved operator
   process, not public registration. No audio/video/presence claim.
5. Peer review uses eligible owned submission, reviewer/author authorization, one
   finalization/award. Without real result, empty state is correct; never fabricate.
6. Notifications remain private/read state persists; rankings privacy opt-in only.
   Profile/portfolio stores real values; export owned data, delete disposable test
   account only after confirming email; old token rejected. Migration head0007.
7. Google/GitHub login/deny/replay/explicit linking: docs/OAUTH_SETUP.md. Real app
   verification remains UNVERIFIED until operator runs it.

Record actual manual outcomes, not predictions:
`bash scripts/record-manual-check.sh stack-browser pass` (or fail/blocked).

## LAN from Windows11/WSL to physical phone/tablet
Never expose development OTP over an untrusted network. Prefer production-mode
staging HTTPS+trusted certificate and exact hostname on the same trusted LAN.
Windows localhost forwarding usually works for Windows browser, NOT other devices.
A bridged disposable VM is the simpler alternative to complex WSL NAT forwarding.

On supported updated Windows11, WSL mirrored networking is optional. Preserve
existing `%UserProfile%\.wslconfig`, merge via Notepad (PowerShell):
```powershell
notepad "$env:USERPROFILE\.wslconfig"
# Add/merge: [wsl2] section with networkingMode=mirrored and firewall=true
# Save work first (all WSL sessions stop):
wsl --shutdown
Get-NetIPConfiguration
```
Configure Windows/Hyper-V firewall in Windows Security/approved admin tooling to
allow ONLY inbound TCP443 for the private LAN/test devices, never broad public
access. Names/IDs vary; do not paste an indiscriminate allow-all rule. NAT mode
requires explicit scoped Windows forwarding/firewall or use a bridged VM instead;
these paths are NOT executed/verified here. No automatic firewall changes in scripts.
Ensure Linux service binds0.0.0.0 and trusted staging hostname resolves on phone
to reachable Windows/VM LAN address; TLS cert must match. Install approved private
CA on test phone if necessary; NEVER bypass a certificate warning.

On phone: registration/mail/login, navigation/editor/disabled submit, rooms/report,
settings at portrait/landscape; keyboard focus/Tab/Enter/Escape, no horizontal
scroll/focus trap/hidden button, readable error/loading/empty states. Compare iOS
Safari and Android browser. Desktop emulation/axe is not physical/assistive proof.
Ubuntu command after check:
`bash scripts/record-manual-check.sh mobile-lan pass` (or fail/blocked).
Send reports/record-manual-check-mobile-lan.* plus OS/browser versions/redacted
screenshots. Remove temporary LAN rules and restore optional mirrored settings
when finished. Do not enable WAN forwarding.

## Backup/restore staging drill
Private paths stay in WSL Linux home, NOT Windows mounts/repo/reports. Dump contains
personal data, encrypt per operator policy; never upload it.
```sh
export ROOT404_STACK_ENV="$HOME/.config/root404/staging.env"
export ROOT404_BACKUP_DIR="$HOME/.local/share/root404/private-backups"
bash scripts/backup-stack.sh
export ROOT404_BACKUP_FILE='/ABSOLUTE/APPROVED/BACKUP.dump'
ROOT404_ALLOW_RESTORE_DRILL=yes bash scripts/restore-drill.sh
```
Expect a new unique root404_restore_* DB at0007, never original overwrite/drop.
Check representative records/constraints/app before restore acceptance. Send only
reports/backup-stack.* / restore-drill.* and redacted integrity result. Docker restore
runtime remains UNVERIFIED here. Manual PASS is operator-reported, not independent audit.

### Provision a test moderator (trusted host operator only)
Register/verify a disposable moderator email first. No public role-assignment API.
Set ROOT404_ADMIN_EMAIL privately in your shell/secret manager, then on approved
staging ONLY (role change revokes target sessions; moderator signs in again):
```sh
export ROOT404_ADMIN_ROLE=grant
ROOT404_ALLOW_ADMIN_CHANGE=yes bash scripts/set-admin.sh
# Revoke after testing:
export ROOT404_ADMIN_ROLE=revoke
ROOT404_ALLOW_ADMIN_CHANGE=yes bash scripts/set-admin.sh
```
Needs ROOT404_STACK_ENV from setup. Expected existing active verified account role
change only; no account created, report reports/set-admin.* (archive grant before
revoke). Docker CLI wrapper UNVERIFIED here; role helper tested locally. Do not send
email/private credentials; public registration still cannot assign is_admin.
