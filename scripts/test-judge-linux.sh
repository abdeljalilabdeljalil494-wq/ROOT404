#!/usr/bin/env bash
# One command AFTER Docker/runsc/dependencies on an approved disposable Linux host.
source "$(dirname -- "${BASH_SOURCE[0]}")/test-common.sh"
[[ "${ROOT404_DISPOSABLE_HOST:-}" == yes ]] || { echo 'BLOCKED: explicit ROOT404_DISPOSABLE_HOST=yes required'; exit 2; }
export CI=true
# Invalidate stale acceptance artifacts before build/runtime failure.
mkdir -p .cache/judge-results
printf '%s\n' '{"status":"BLOCKED","reason":"Current Linux acceptance not completed"}' > .cache/judge-results/result.json
command -v docker
command -v runsc
runsc --version
docker version
[[ "$(docker info --format '{{.CgroupVersion}}')" == 2 ]] || { echo 'cgroup v2 required'; exit 1; }
bash scripts/prepare-judge-image.sh
source .cache/judge-image.env
bash scripts/test-judge.sh --docker-ci
