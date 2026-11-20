#!/usr/bin/env bash
if [[ "${ROOT404_REPORT_ACTIVE:-}" != yes ]]; then
  _root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
  exec python3 "$_root/scripts/report_run.py" "check-production-readiness" bash "$0" "$@"
fi
# Never turns passing unit tests into a release authorization.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
printf '%s\n' \
 'NOT PRODUCTION READY' \
 'BLOCKED: real Docker/gVisor evidence for the outside-container host supervisor/protocol v2' \
 'INCOMPLETE: nine original project-specific grading suites' \
 'INCOMPLETE: remaining advanced product workflows and abuse controls' \
 'BLOCKED: production service verification and independent security sign-off' \
 'See PRODUCTION_READINESS.md and FINAL_ACCEPTANCE_REPORT.md.'
exit 1
