#!/usr/bin/env bash
# Comprehensive local checks. Collects failures without masking the final status.
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
failed=0
run_gate() {
  printf '\n=== %s ===\n' "$1"
  shift
  if "$@"; then printf '%s\n' 'PASS'; else failed=1; printf '%s\n' 'FAIL (continuing other independent gates)' >&2; fi
}
run_gate tracked-secret-filenames "$PYTHON" scripts/check_tracked_secrets.py
run_gate backend bash scripts/test-backend.sh
run_gate frontend bash scripts/test-frontend.sh
# Live paid/mail probes require consent; configured authorized environments run
# them automatically. Missing/failed authorized checks retain nonzero status.
if [[ "${ROOT404_ALLOW_EXTERNAL_PROBES:-}" == yes ]]; then
  run_gate external bash scripts/test-infrastructure.sh --external
fi
run_gate python-compile "$PYTHON" -m compileall -q backend/app executor_service judge_sandbox scripts
run_gate whitespace git diff --check
printf '\nLocal quality result: '
if (( failed )); then echo FAIL; else echo PASS; fi
printf '%s\n' 'Local PASS does not imply production readiness. External/Docker gates are separate; run bash scripts/check-production-readiness.sh.'
exit "$failed"
