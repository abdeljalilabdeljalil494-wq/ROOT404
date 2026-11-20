# Trusted isolated execution dispatcher

**Implemented, contract-tested; Docker/gVisor runtime NOT verified in this sandbox.**
Do not enable public submissions until the hostile acceptance harness, host policy
review and independent security assessment pass. A container start is not an audit.

## Trust and placement
Run `executor_service.service:create_app --factory` on a **dedicated execution
worker host**, not inside the frontend/API/job container. The controller has
administrative Docker authority (a Docker-group user is effectively host root).
No daemon socket is mounted into any container. No user source enters shell
commands: only a server-generated name, fixed policy and operator-pinned image
are CLI arguments. Source arrives as bounded JSON on stdin, never as bind mounts.

The backend connects over TLS with a >=48-character private bearer secret; use
private ingress/firewall allowlisting (or operator-configured mTLS). TLS termination
is trusted and must not log Authorization/body. Do not expose port8090 publicly.
Example host service and TLS ingress are in `deploy/`; **not deployed/tested here**.

## Mandatory host dependencies
- Patched Linux host, cgroupv2, Docker with default seccomp enabled.
- Installed/configured gVisor `runsc` runtime, toolchain image built and audited.
- One controller process per worker; startup file lock rejects multiple workers.
- Dedicated host/daemon for ROOT404: startup removes jobs bearing its label.
- Trusted image registry and immutable `repository@sha256:...` image digest.
  Ubuntu24.04 is the current build base, so refresh/pin/scan base and toolchain in
  deployment; no build/runtime or image vulnerability audit was possible here.

```sh
# On the operator's isolated build/worker infrastructure, NOT run here:
docker build -f judge_sandbox/Dockerfile.runner -t YOUR_REGISTRY/root404-job:VERSION judge_sandbox
# Push to your trusted registry and record the resulting immutable RepoDigest.
# Supply that real digest via EXECUTOR_IMAGE; no placeholder digest is executable.
python3 -m venv .venv
.venv/bin/pip install -r executor_service/requirements.txt
```
Private `/etc/root404/executor.env` (mode0600) supplies EXECUTOR_IMAGE,
EXECUTOR_SHARED_SECRET, EXECUTOR_CONCURRENCY (default2,max16), and optionally
EXECUTOR_LOCK_FILE (default `/run/root404-executor/controller.lock`). The parent
lock directory must exist with worker-only permissions; systemd RuntimeDirectory
creates it. Set Docker config/daemon address only via trusted host configuration.
Never pass daemon credentials into a job image/environment.

## Enforced dispatch policy
Fresh job/container, trusted supervisor UID0 with ONLY CHOWN,DAC_OVERRIDE,KILL,
SETGID,SETUID after capdropALL; compiler and learner irreversibly drop to UID/GID1000
with no groups/capabilities. Supervisor is non-dumpable; learner cannot access its
protocol FDs or signal it. This is an intentional privileged-but-minimal trusted
supervisor, NOT a root learner. Networknone, immutable read-only root,
no-new-privileges, default seccomp + required runsc, IPCnone, no volumes/devices/
secrets, 1CPU, 256MiB RAM+swap cap,64PIDs,64FDs, corefiles disabled. Workspaces are
private64MiB tmpfs (exec needed for compiled binaries); tmp16MiB noexec. No image
pull during jobs. Source max20files,256KiB/file,512KiB total; stdin10KiB;
HTTP body1MiB with10s read deadline and bounded in-flight requests. Execution
budget1–30s per compilation/run, plus bounded controller overhead. Output is
bounded at primitive and controller pipe. Exact memory status depends on kernel
OOM evidence; language MemoryError may be runtime_error, never invented success.

Every result is schema-validated, not a score. Hidden expected outputs remain in
the backend. The wrapper/job result is untrusted data, not hardware attestation.
Finally removes container/anonymous volumes. Cleanup failure taints the worker,
blocks later execution and requires operator recovery. Startup and90s stale-job
reaper cover interrupted controllers/daemon races; recovery depends on a working
daemon. No guarantee is made for compromised/down hosts; monitor and drain them.

## Run verification
```sh
.venv/bin/python -m pytest executor_service/tests -q
# On a dedicated, approved hostile-test host with verified TLS:
# Privately configure ROOT404_EXECUTOR_TEST_URL and ROOT404_EXECUTOR_TEST_SECRET.
ROOT404_EXECUTOR_ALLOW_HOSTILE_TESTS=yes .venv/bin/python scripts/verify_executor.py
```
The harness sends real correct/incorrect/crashing/infinite/memory/output/fork jobs,
checks UID/root/network/socket/workspace separation and concurrent execution. It
**has not run here** (docker command absent). Also independently inspect cgroup
limits, daemon state/orphans after disconnect/restart, seccomp/AppArmor, cross-job
filesystem/process isolation, TLS credentials, worker egress and escape resistance.
This targeted suite is not a proof that container escape is impossible.

After acceptance only: configure backend JUDGE_ENABLED=true, JUDGE_URL=https://...
and the same private JUDGE_SHARED_SECRET. Never bypass TLS validation or substitute
host subprocess execution. Backend default remains disabled.

## Distinct identities and actual verification boundary
`judge_sandbox/runners/identity.py` checks the supervisor effective/permitted/bounding
capability set exactly (no ambient/inherited capabilities), then makes it
non-dumpable and no-new-privileges. Only the forked child drops all groups and
real/effective/saved IDs before compiler or learner exec. Linux clears capabilities
on root-to-user transition, verified again before exec. No keepcaps or setuid helper.
The root supervisor needs CHOWN for source ownership, DAC_OVERRIDE for safe cleanup
of learner-mode000 files, KILL for process-group reap, SETGID/SETUID for the drop.
Container root without SYS_ADMIN/NET_ADMIN/SYS_PTRACE or socket is not host-admin
isolation proof; real gVisor/cgroup/default-seccomp policy remains mandatory.

Native fixed probe actually passed under exactly these capabilities, verifying
UID/GID/groups, denied root regain/signaling/proc FD/private-file access. No learner
source or hostile executable was run on the host. It does not prove container
escape resistance. Docker CI verifies real identity/forgery/syscall behavior before
public judging can be enabled. Do not replace expected capabilities with defaults.
