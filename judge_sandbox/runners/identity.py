"""Linux identity boundary for the trusted per-container supervisor.

Not host isolation: requires the actual approved gVisor/cgroup/network policy.
All failures are fatal; there is no same-UID or root-learner fallback.
"""
import ctypes
import os

LEARNER_UID = 1000
LEARNER_GID = 1000
PR_SET_DUMPABLE = 4
PR_SET_NO_NEW_PRIVS = 38


def prctl(option, value):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(option, value, 0, 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def protect_supervisor():
    if os.environ.get('ROOT404_ISOLATED_JOB') != '1' or os.getresuid() != (0, 0, 0):
        raise RuntimeError('Trusted supervisor identity required')
    # Reject accidental privileged/default-capability launches as well as an
    # underprivileged supervisor that would fail to drop/reap its children.
    allowed = sum(1 << bit for bit in (0, 1, 5, 6, 7))  # CHOWN,DAC_OVERRIDE,KILL,SETGID,SETUID
    with open('/proc/self/status') as status:
        fields = dict(line.split(':', 1) for line in status if ':' in line)
    if any(int(fields[key].strip(), 16) != allowed for key in ('CapEff', 'CapPrm', 'CapBnd')):
        raise RuntimeError('Supervisor capability policy mismatch')
    if any(int(fields[key].strip(), 16) for key in ('CapInh', 'CapAmb')):
        raise RuntimeError('Supervisor inherited/ambient capabilities forbidden')
    prctl(PR_SET_DUMPABLE, 0)
    prctl(PR_SET_NO_NEW_PRIVS, 1)


def drop_to_learner():
    if os.getresuid() != (0, 0, 0):
        raise RuntimeError('Refusing shared supervisor/learner identity')
    os.setgroups([])
    os.setresgid(LEARNER_GID, LEARNER_GID, LEARNER_GID)
    os.setresuid(LEARNER_UID, LEARNER_UID, LEARNER_UID)
    prctl(PR_SET_NO_NEW_PRIVS, 1)
    if os.getresuid() != (LEARNER_UID,) * 3 or os.getresgid() != (LEARNER_GID,) * 3 or os.getgroups():
        raise RuntimeError('Learner privilege drop failed')
    # Linux setresuid clears effective/permitted capabilities; no keepcaps used.
    with open('/proc/self/status') as status:
        fields = dict(line.split(':', 1) for line in status if ':' in line)
    if any(int(fields[key].strip(), 16) for key in ('CapEff', 'CapPrm', 'CapInh', 'CapAmb')):
        raise RuntimeError('Learner retained capabilities')
