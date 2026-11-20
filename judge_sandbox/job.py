"""Fixed stdin JSON protocol for one ephemeral execution container; no secrets."""
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runners.common import execute


def main():
    from runners.identity import protect_supervisor
    protect_supervisor()
    # Host validates too. Defense against a controller/configuration mistake.
    data = sys.stdin.buffer.read(1048577)
    if len(data) > 1048576:
        raise ValueError('Oversized job')
    job = json.loads(data)
    files = job['files']
    if not isinstance(files, dict) or not 1 <= len(files) <= 20:
        raise ValueError('Invalid files')
    import re
    total = 0
    for name, source in files.items():
        if (not isinstance(source, str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]{0,99}', name)
                or any(part in {'', '.', '..'} or part.startswith('.') for part in name.split('/'))
                or '\x00' in source or len(source.encode()) > 262144):
            raise ValueError('Invalid source')
        total += len(source.encode())
    if total > 524288:
        raise ValueError('Oversized sources')
    with tempfile.TemporaryDirectory(prefix='job-', dir='/workspace') as directory:
        root = Path(directory)
        for name, source in files.items():
            path = root/name
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            path.write_text(source)
            path.chmod(0o600)
        # Only the learner workspace belongs to UID1000; /opt/judge and
        # supervisor protocol pipes remain trusted, root-owned and inaccessible.
        for path in [root, *root.rglob('*')]:
            os.chown(path, 1000, 1000)
        result = execute(directory, job['language'], job.get('stdin', ''),
                         job.get('timeout_seconds', 5), job.get('output_limit_bytes', 65536))
        # Result is untrusted data at the controller, not a grading decision.
        sys.stdout.write(json.dumps(result))


if __name__ == '__main__':
    main()
