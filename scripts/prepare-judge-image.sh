#!/usr/bin/env bash
if [[ "${ROOT404_REPORT_ACTIVE:-}" != yes ]]; then
  _root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
  exec python3 "$_root/scripts/report_run.py" "prepare-judge-image" bash "$0" "$@"
fi
# ONLY on an approved disposable Docker worker. Creates a loopback registry.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
[[ "${CI:-}" == true ]] || { echo 'Set CI=true only on the approved disposable runner.'; exit 2; }
docker version
mkdir -p .cache/judge-results
# Refuse to take over any existing named service/container.
docker run -d --name root404-rc-registry -p 127.0.0.1:5000:5000 registry:2
trap 'docker rm -f root404-rc-registry >/dev/null' EXIT
docker build --pull -f judge_sandbox/Dockerfile.runner -t localhost:5000/root404-job:rc judge_sandbox
docker push localhost:5000/root404-job:rc
image=$(docker image inspect localhost:5000/root404-job:rc --format '{{index .RepoDigests 0}}')
[[ "$image" =~ ^localhost:5000/root404-job@sha256:[a-f0-9]{64}$ ]] || { echo 'Immutable image digest missing'; exit 1; }
printf 'export EXECUTOR_IMAGE=%q\n' "$image" > .cache/judge-image.env
chmod 600 .cache/judge-image.env
docker image inspect localhost:5000/root404-job:rc --format '{{.Id}} {{json .RepoDigests}}' > .cache/judge-results/image.txt
printf '%s\n' 'Now run: source .cache/judge-image.env' 'Then: CI=true bash scripts/test-judge.sh --docker-ci'
