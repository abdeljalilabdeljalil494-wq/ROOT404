#!/usr/bin/env bash
if [[ "${ROOT404_REPORT_ACTIVE:-}" != yes ]]; then
  _root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
  exec python3 "$_root/scripts/report_run.py" "setup-testing" bash "$0" "$@"
fi
# Installs only declared/locked test dependencies; no services or system changes.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
python3 -m venv .cache/verification-venv
.cache/verification-venv/bin/python -m pip install -r backend/requirements-dev.txt -r executor_service/requirements.txt -r requirements-integration.txt
(cd frontend && npm ci)
# Linux uses the locked packaged Chromium; other desktops use Playwright's build.
if [[ "$(uname -s)" != Linux ]] && [[ -z "${ROOT404_CHROMIUM_EXECUTABLE:-}" ]]; then
  (cd frontend && npx playwright install chromium)
fi
printf '%s\n' 'Dependencies ready. Run bash scripts/validate.sh'
