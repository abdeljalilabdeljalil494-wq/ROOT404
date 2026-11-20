"""One-shot job CLI. Requires externally enforced container isolation.

This is not a persistent HTTP executor and must not be exposed as one. No scores
are assigned here: the backend compares actual output with server-owned tests.
"""
import argparse
import json
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runners.common import execute, LANGUAGES, ALIASES


def run_in_sandbox(language, files, test_cases=None, timeout=5):
    language = ALIASES.get(language, language)
    if language not in LANGUAGES or not isinstance(files, dict) or not 1 <= len(files) <= 20:
        raise ValueError("Invalid language or file count")
    total = 0
    for name, content in files.items():
        if not isinstance(name, str) or not isinstance(content, str):
            raise ValueError("Invalid file")
        if not name or len(name) > 100 or name.startswith(('/', '.')) or '\\' in name or '..' in name or '\x00' in name or '\x00' in content:
            raise ValueError("Invalid filename or content")
        size = len(content.encode())
        if size > 1024 * 1024: raise ValueError("File too large")
        total += size
    if total > 5 * 1024 * 1024: raise ValueError("Submission too large")
    parent = '/workspace' if Path('/workspace').exists() else None
    with tempfile.TemporaryDirectory(prefix='root404_', dir=parent) as directory:
        for name, content in files.items():
            path = Path(directory) / name
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_text(content)
            path.chmod(0o600)
        if test_cases:
            return {"executions": [execute(directory, language, case.get('stdin', ''), timeout) for case in test_cases]}
        return execute(directory, language, '', timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang', required=True)
    parser.add_argument('--files', required=True, help='JSON filename-to-source map')
    parser.add_argument('--tests', help='Server-supplied JSON test list')
    parser.add_argument('--timeout', type=int, default=5)
    args = parser.parse_args()
    try:
        files = json.loads(Path(args.files).read_text())
        tests = json.loads(Path(args.tests).read_text()) if args.tests else None
        print(json.dumps(run_in_sandbox(args.lang, files, tests, args.timeout)))
    except (ValueError, OSError):
        print(json.dumps({"status": "error", "error": "Invalid job or unavailable toolchain"}))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
