#!/usr/bin/env bash
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
"$PYTHON" -m pytest backend/tests executor_service/tests -q
