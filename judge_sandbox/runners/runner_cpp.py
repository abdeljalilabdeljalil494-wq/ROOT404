"""Actual cpp execution. External per-job isolation is mandatory."""
import json
import sys
try:
    from .common import execute
except ImportError:
    from common import execute


def run_cpp_project(workdir, stdin="", timeout=5):
    return execute(workdir, "cpp", stdin, timeout)


if __name__ == "__main__":
    print(json.dumps(run_cpp_project(sys.argv[1], sys.stdin.read(10241))))
