#!/usr/bin/env bash
# Source from a test entrypoint. No env files are printed or implicitly loaded.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
PYTHON=${ROOT404_TEST_PYTHON:-$ROOT/.cache/verification-venv/bin/python}
if [[ ! -x "$PYTHON" ]] && ! command -v "$PYTHON" >/dev/null 2>&1; then
  printf '%s\n' 'Python environment missing. Run bash scripts/setup-testing.sh or set ROOT404_TEST_PYTHON.' >&2
  exit 2
fi
export ROOT404_TEST_PYTHON="$PYTHON"

# Every operator test entrypoint preserves its actual exit code and redacted log.
if [[ "${ROOT404_REPORT_ACTIVE:-}" != yes ]]; then
  _report_name=$(basename "$0" .sh)
  if [[ "$_report_name" == record-manual-check && -n "${1:-}" ]]; then _report_name="$_report_name-$1"; fi
  case "${1:-}" in --native|--external|--unit|--docker-ci|--remote) _report_name="${_report_name}-${1#--}" ;; esac
  exec "$PYTHON" scripts/report_run.py "$_report_name" bash "$0" "$@"
fi
