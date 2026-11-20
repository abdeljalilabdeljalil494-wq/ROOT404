"""Actual javascript execution. External per-job isolation is mandatory."""
import json
import sys
try:
    from .common import execute
except ImportError:
    from common import execute


def run_js_project(workdir, stdin="", timeout=5):
    return execute(workdir, "javascript", stdin, timeout)


if __name__ == "__main__":
    print(json.dumps(run_js_project(sys.argv[1], sys.stdin.read(10241))))
