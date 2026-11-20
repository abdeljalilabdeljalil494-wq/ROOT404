#!/usr/bin/env bash
if [[ "${ROOT404_REPORT_ACTIVE:-}" != yes ]]; then
  _root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
  exec python3 "$_root/scripts/report_run.py" "install_gvisor_ci" bash "$0" "$@"
fi
# Disposable Linux CI worker ONLY. No sudo password, credential or socket mounts.
set -euo pipefail
[ "${CI:-}" = true ] || { echo "Disposable CI=true runner required" >&2; exit 2; }
version=20261116.0
arch=x86_64
[ "$(uname -m)" = "$arch" ]
command -v docker
sudo docker info >/dev/null
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
base="https://storage.googleapis.com/gvisor/releases/release/${version}/${arch}"
curl --fail --location --retry 3 "$base/runsc" -o runsc
curl --fail --location --retry 3 "$base/runsc.sha512" -o runsc.sha512
sha512sum -c runsc.sha512
sudo install -m 0755 runsc /usr/local/bin/runsc
# Add runsc without erasing Docker's existing CI daemon configuration.
sudo python3 - <<'PY'
import json
from pathlib import Path
p=Path('/etc/docker/daemon.json')
s=p.read_text() if p.exists() else '{}'
config=json.loads(s)
config.setdefault('runtimes',{})['runsc']={'path':'/usr/local/bin/runsc','runtimeArgs':['--platform=systrap']}
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(config))
PY
sudo systemctl restart docker
runsc --version
docker version
docker info --format '{{json .Runtimes}} {{.CgroupVersion}}'
