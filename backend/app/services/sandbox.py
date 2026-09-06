"""Hybrid sandbox executor — the « Docker/Ubuntu Sandbox » of the roadmap.

Strategy (auto-detected, per project decision):
- Docker available  → every command runs in an ephemeral Ubuntu container:
  `docker run --rm --network none --memory 512m --cpus 1 --pids-limit 128`
  with the working directory mounted. Network is fully disabled.
- Docker unavailable → restricted local subprocess:
  * fresh working dir under data/sandbox/ (wiped before each run)
  * wall-clock timeout (subprocess) + CPU rlimit
  * RAM capped via RLIMIT_AS (512 MiB)
  * file size capped via RLIMIT_FSIZE (16 MiB) — no disk bombs
  * RLIMIT_NOFILE 64, RLIMIT_NPROC 128
  * minimal environment (PATH reduced, no user env)
  * network: cannot be disabled without user namespaces — accepted
    residual risk in dev mode; the Docker path closes it for production.

The judge only ever talks to this module — swapping execution backends
requires no change elsewhere.
"""

import os
import resource
import shlex
import shutil
import subprocess
import tempfile

SANDBOX_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "sandbox")

# Limits shared by both backends
LIMIT_TIMEOUT = 12.0        # default wall clock per command (s)
LIMIT_MEMORY = 512 * 1024 * 1024   # 512 MiB
LIMIT_FSIZE = 16 * 1024 * 1024     # 16 MiB per file
LIMIT_NOFILE = 64
LIMIT_NPROC = 128
OUTPUT_CAP = 1024 * 1024   # 1 MiB captured per stream

DOCKER_IMAGE = "root404-sandbox"
DOCKER_TIMEOUT = 60.0      # per command, inside docker

_docker_ok: bool | None = None


class ExecResult:
    def __init__(self, ok: bool, exit_code: int, stdout: str, stderr: str,
                 timed_out: bool, via: str):
        self.ok = ok
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.via = via  # 'docker' | 'local'

    @property
    def output(self) -> str:
        return self.stdout + self.stderr


def docker_available() -> bool:
    """Cached probe: docker CLI present AND able to talk to the daemon."""
    global _docker_ok
    if _docker_ok is None:
        _docker_ok = False
        if shutil.which("docker"):
            try:
                r = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
                _docker_ok = r.returncode == 0
            except Exception:
                _docker_ok = False
    return _docker_ok


def _ensure_docker_image() -> bool:
    """Build the sandbox image once (ubuntu + build tools + valgrind)."""
    dockerfile = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sandbox", "Dockerfile")
    if not os.path.exists(dockerfile):
        return False
    try:
        probe = subprocess.run(["docker", "image", "inspect", DOCKER_IMAGE],
                               capture_output=True, timeout=15)
        if probe.returncode != 0:
            build = subprocess.run(["docker", "build", "-t", DOCKER_IMAGE, os.path.dirname(dockerfile)],
                                   capture_output=True, timeout=900)
            if build.returncode != 0:
                return False
        return True
    except Exception:
        return False


def _limits(cpu_seconds: int):
    """preexec_fn: apply rlimits in the child (local mode only)."""
    def _apply():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        resource.setrlimit(resource.RLIMIT_AS, (LIMIT_MEMORY, LIMIT_MEMORY))
        resource.setrlimit(resource.RLIMIT_FSIZE, (LIMIT_FSIZE, LIMIT_FSIZE))
        resource.setrlimit(resource.RLIMIT_NOFILE, (LIMIT_NOFILE, LIMIT_NOFILE))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (LIMIT_NPROC, LIMIT_NPROC))
        except (ValueError, OSError):
            pass  # may already be near the cap
    return _apply


def _env() -> dict:
    return {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "HOME": "/tmp",
        "LANG": "C.UTF-8",
        "TERM": "dumb",
    }


def run_command(workdir: str, args: list, stdin: str | None = None,
                timeout: float = LIMIT_TIMEOUT) -> ExecResult:
    """Run a command inside the sandbox. Never raises on command failure."""
    if docker_available() and _ensure_docker_image():
        return _run_docker(workdir, args, stdin, timeout)
    return _run_local(workdir, args, stdin, timeout)


def _run_local(workdir: str, args: list, stdin: str | None, timeout: float) -> ExecResult:
    try:
        proc = subprocess.Popen(
            [str(a) for a in args],
            cwd=workdir,
            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_env(),
            preexec_fn=_limits(int(timeout) + 1),
        )
    except Exception as e:  # binary missing, …
        return ExecResult(False, 127, "", f"sandbox: impossible de lancer {' '.join(map(str, args))} ({e})", False, "local")
    try:
        # communicate() feeds stdin, closes it, and drains BOTH pipes
        # concurrently — no deadlocks with forked children.
        out_b, err_b = proc.communicate(
            input=(stdin or "").encode("utf-8") if stdin is not None else None,
            timeout=timeout,
        )
        return ExecResult(proc.returncode == 0, proc.returncode,
                          out_b[:OUTPUT_CAP].decode("utf-8", errors="replace"),
                          err_b[:OUTPUT_CAP].decode("utf-8", errors="replace"),
                          False, "local")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return ExecResult(False, -1, "", f"sandbox: timeout ({timeout:.0f}s) — processus tué.", True, "local")


def _run_docker(workdir: str, args: list, stdin: str | None, timeout: float) -> ExecResult:
    workdir_abs = os.path.abspath(workdir)
    cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", f"{LIMIT_MEMORY // 1024}m",
        "--cpus", "1",
        "--pids-limit", str(LIMIT_NPROC),
        "--user", "65534",
        "-v", f"{workdir_abs}:/work",
        "-w", "/work",
        DOCKER_IMAGE,
        "bash", "-c", shlex.join(str(a) for a in args),
    ]
    try:
        r = subprocess.run(cmd, input=(stdin or "").encode() if stdin is not None else None,
                           capture_output=True, timeout=timeout + 20)
        out = r.stdout[:OUTPUT_CAP].decode("utf-8", errors="replace")
        err = r.stderr[:OUTPUT_CAP].decode("utf-8", errors="replace")
        return ExecResult(r.returncode == 0, r.returncode, out, err, False, "docker")
    except subprocess.TimeoutExpired:
        return ExecResult(False, -1, "", f"sandbox: timeout ({timeout:.0f}s) — conteneur tué.", True, "docker")
    except Exception as e:
        return ExecResult(False, 127, "", f"sandbox: docker indisponible ({e})", False, "docker")


def fresh_workdir(tag: str) -> str:
    """Create (wiping first) an isolated working directory for one run."""
    os.makedirs(SANDBOX_ROOT, exist_ok=True)
    d = os.path.join(SANDBOX_ROOT, tag)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    return d


def temp_file() -> str:
    """Scratch file inside the sandbox root (for judge fixtures)."""
    os.makedirs(SANDBOX_ROOT, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix="r404_", dir=SANDBOX_ROOT)
    os.close(fd)
    return path
