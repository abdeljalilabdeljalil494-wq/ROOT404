#!/usr/bin/env python3
"""Opt-in trusted native UID boundary probe; NOT sandbox/hostile-code verification.

Runs only fixed audited operations, never learner source. Requires Linux root to
perform setresuid. Does not configure the host, create accounts or touch Docker.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'judge_sandbox'))
from runners.identity import protect_supervisor, drop_to_learner


def main():
    if os.environ.get('ROOT404_ALLOW_NATIVE_IDENTITY_PROBE') != 'yes' or os.getuid() != 0:
        raise SystemExit('Requires explicit opt-in and root; never run learner source here')
    with tempfile.TemporaryDirectory(prefix='root404-identity-') as directory:
        secret = Path(directory) / 'supervisor-private'
        secret.write_text('private test marker')
        secret.chmod(0o600)
        os.environ['ROOT404_ISOLATED_JOB'] = '1'
        protect_supervisor()
        incoming, outgoing = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(incoming)
            result = {}
            try:
                drop_to_learner()
                result['identities'] = os.getresuid() == (1000,)*3 and os.getresgid() == (1000,)*3
                result['groups'] = os.getgroups() == []
                for name, operation in [
                    ('root_regain', lambda: os.setuid(0)),
                    ('supervisor_signal', lambda: os.kill(os.getppid(), 0)),
                    ('supervisor_fd', lambda: os.open(f'/proc/{os.getppid()}/fd/1', os.O_WRONLY)),
                    ('private_file', lambda: os.open(str(secret), os.O_RDONLY)),
                ]:
                    try: operation()
                    except PermissionError: result[name] = True
                    else: result[name] = False
                os.write(outgoing, json.dumps(result).encode())
                os._exit(0)
            except BaseException:
                os.write(outgoing, b'{"probe_error":true}')
                os._exit(1)
        os.close(outgoing)
        result = json.loads(os.read(incoming, 4096))
        os.close(incoming)
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0 and len(result) == 6 and all(result.values()), result
        print(json.dumps({'status': 'VERIFIED', 'scope': 'native fixed UID/capability/proc boundary probe ONLY', 'checks': result}))


if __name__ == '__main__':
    main()
