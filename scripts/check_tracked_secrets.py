"""Filename-only prevention guard. Never reads tracked values or historical blobs.
Not a substitute for an authorized secret-content/history scan or rotation.
"""
from pathlib import PurePosixPath
import subprocess
import sys


def main():
    names = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
    blocked = []
    for name in filter(None, names):
        leaf = PurePosixPath(name).name.lower()
        example = leaf.endswith(('.example', '.sample', '.template'))
        if not example and (leaf == '.env' or leaf.startswith('.env.') or
                            leaf in {'id_rsa', 'id_ed25519', 'credentials.json'} or
                            leaf.endswith(('.key', '.p12', '.pfx'))):
            blocked.append(name)
    if blocked:
        print('FAIL: sensitive filenames in Git index (values not inspected):')
        for name in blocked:
            print(name)
        return 1
    print('PASS: no prohibited secret filenames in Git index; contents/history NOT scanned')
    return 0


if __name__ == '__main__':
    sys.exit(main())
