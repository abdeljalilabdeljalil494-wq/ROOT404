"""One-shot execution primitive, NOT a sandbox.

Call only inside a fresh, externally isolated job container. Resource limits do
not provide network/filesystem isolation. Never import this in the backend.
"""
import math
import os
from pathlib import Path
import resource
import signal
import selectors
import subprocess
import sys
import tempfile
import time

LANGUAGES = {"c": (".c",), "cpp": (".cpp", ".cc"), "python": (".py",), "javascript": (".js",)}
ALIASES = {"c++": "cpp", "py": "python", "js": "javascript"}


def execute(workdir, language, stdin="", timeout=5, output_limit=65536):
    language = ALIASES.get(language, language)
    root = Path(workdir).resolve()
    if language not in LANGUAGES or not 0 < timeout <= 30 or len(stdin.encode()) > 10240:
        raise ValueError("Invalid execution request")
    started = time.monotonic()
    sources = sorted(p for p in root.rglob('*') if p.suffix in LANGUAGES[language] and p.is_file())
    if not sources or any(p.is_symlink() or not p.resolve().is_relative_to(root) for p in sources):
        return {"status": "compilation_error", "output": "", "error": "No valid source files", "exit_code": None, "execution_time": 0}
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(root), "TMPDIR": str(root), "LANG": "C.UTF-8"}

    def limits():
        # RLIMIT_NPROC is UID-wide on a shared host. Enforce it only inside
        # the isolated job namespace; the Docker cgroup PID cap remains required.
        if os.environ.get("ROOT404_ISOLATED_JOB") == "1":
            resource.setrlimit(resource.RLIMIT_NPROC, (48, 48))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(timeout), math.ceil(timeout) + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024, 32 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        # V8 reserves more address space than its actual resident memory.
        memory = (1024 if language == "javascript" else 512) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        if os.environ.get("ROOT404_ISOLATED_JOB") == "1":
            # This function runs in the forked child ONLY. All identities and
            # supplementary groups are dropped irreversibly before any learner
            # code (including the compiler's input) executes.
            from runners.identity import drop_to_learner
            drop_to_learner()

    def invoke(command, input_text=""):
        # Keep pipe-output bounds independent of compiler artifact file limits.
        # The old RLIMIT_FSIZE=output_limit also truncated valid executables.
        with tempfile.TemporaryFile(dir=root) as incoming:
            incoming.write(input_text.encode()); incoming.seek(0)
            process = subprocess.Popen(command, cwd=root, env=env, stdin=incoming,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       start_new_session=True, preexec_fn=limits)
            streams = {'out': bytearray(), 'err': bytearray()}
            timed_out, limited = False, False
            deadline = time.monotonic() + timeout
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ, 'out')
                    selector.register(process.stderr, selectors.EVENT_READ, 'err')
                    while selector.get_map():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            timed_out = True
                            break
                        for key, _ in selector.select(min(remaining, .1)):
                            target = streams[key.data]
                            chunk = os.read(key.fd, min(8192, output_limit + 1 - len(target)))
                            if not chunk:
                                selector.unregister(key.fileobj)
                            else:
                                target.extend(chunk)
                        if any(len(data) > output_limit for data in streams.values()):
                            limited = True
                            break
                    if not timed_out and not limited:
                        try:
                            process.wait(timeout=max(.001, deadline-time.monotonic()))
                        except subprocess.TimeoutExpired:
                            timed_out = True
            finally:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait()
                process.stdout.close(); process.stderr.close()
            return (process.returncode, streams['out'][:output_limit].decode(errors='replace'),
                    streams['err'][:output_limit].decode(errors='replace'), timed_out, limited)

    def result(status, output, error, code):
        return {"status": status, "output": output, "error": error, "exit_code": code, "execution_time": time.monotonic() - started}

    if language in ("c", "cpp"):
        binary = root / ".root404-program"
        command = ["gcc" if language == "c" else "g++", "-Wall", "-Wextra", "-Werror", "-I", str(root), *map(str, sources), "-o", str(binary)]
        code, out, err, timeout_hit, limited = invoke(command)
        if timeout_hit: return result("timeout", out, err, code)
        if limited: return result("output_limit", out, err, code)
        if code != 0: return result("compilation_error", out, err, code)
        command = [str(binary)]
    else:
        main = root / ("main.py" if language == "python" else "main.js")
        if main not in sources:
            if len(sources) != 1: return result("compilation_error", "", "A main entry point is required", None)
            main = sources[0]
        command = [sys.executable, "-I", str(main)] if language == "python" else ["node", "--jitless", "--max-old-space-size=64", str(main)]
    code, out, err, timeout_hit, limited = invoke(command, stdin)
    status = "timeout" if timeout_hit or code == -signal.SIGXCPU else "output_limit" if limited else "success" if code == 0 else "runtime_error"
    return result(status, out, err, code)
