#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
case "${1:---unit}" in
  --unit) "$PYTHON" -m pytest executor_service/tests backend/tests/test_judge_protocol.py backend/tests/test_original_grading_gate.py backend/tests/test_project_suites.py -q ;;
  --docker-ci)
    [[ "${CI:-}" == true ]] || { echo 'Disposable CI runner required; see USER_TESTING_GUIDE.md'; exit 2; }
    mkdir -p .cache/judge-results
    printf '%s\n' '{"status":"BLOCKED","reason":"Current Docker/gVisor acceptance has not completed"}' > .cache/judge-results/result.json
    docker version
    "$PYTHON" scripts/run_executor_ci.py ;;
  --remote) "$PYTHON" scripts/verify_executor.py ;;
  *) echo 'Choose --unit, --docker-ci, or --remote (explicit private opt-in approved isolated worker).'; exit 2 ;;
esac
