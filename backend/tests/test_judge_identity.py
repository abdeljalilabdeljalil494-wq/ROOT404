"""Control-order tests, NOT proof of kernel/container enforcement."""
import sys
from pathlib import Path
from unittest.mock import mock_open
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'judge_sandbox'))
from runners import identity


def test_supervisor_refuses_same_uid_or_nonisolated_host(monkeypatch):
    monkeypatch.delenv('ROOT404_ISOLATED_JOB', raising=False)
    with pytest.raises(RuntimeError): identity.protect_supervisor()
    monkeypatch.setenv('ROOT404_ISOLATED_JOB', '1')
    monkeypatch.setattr(identity.os, 'getresuid', lambda: (1000,)*3)
    with pytest.raises(RuntimeError): identity.protect_supervisor()


def test_irreversible_learner_identity_order_and_zero_caps(monkeypatch):
    calls = []
    monkeypatch.setattr(identity.os, 'getresuid', lambda: (1000,)*3 if calls else (0,)*3)
    monkeypatch.setattr(identity.os, 'getresgid', lambda: (1000,)*3)
    monkeypatch.setattr(identity.os, 'getgroups', lambda: [])
    for name in ['setgroups','setresgid','setresuid']:
        monkeypatch.setattr(identity.os, name, lambda *args, name=name: calls.append((name, args)))
    monkeypatch.setattr(identity, 'prctl', lambda *args: calls.append(('prctl', args)))
    status = ''.join(key+':\t0000000000000000\n' for key in ['CapEff','CapPrm','CapInh','CapAmb'])
    monkeypatch.setattr('builtins.open', mock_open(read_data=status))
    identity.drop_to_learner()
    assert [row[0] for row in calls] == ['setgroups','setresgid','setresuid','prctl']
    assert calls[2][1] == (1000,1000,1000)
    monkeypatch.setattr('builtins.open', mock_open(read_data=status.replace('CapEff:\t0000000000000000','CapEff:\t0000000000000001')))
    calls.clear()
    with pytest.raises(RuntimeError, match='capabilities'): identity.drop_to_learner()


def test_supervisor_rejects_extra_caps_and_enforces_protection_order(monkeypatch):
    monkeypatch.setenv('ROOT404_ISOLATED_JOB', '1')
    monkeypatch.setattr(identity.os, 'getresuid', lambda: (0,)*3)
    allowed=sum(1 << bit for bit in (0,1,5,6,7))
    def status(mask):
        return ''.join(key+':\t'+format(mask,'016x')+'\n' for key in ['CapEff','CapPrm','CapBnd'])+'CapInh:\t0\nCapAmb:\t0\n'
    calls=[]
    monkeypatch.setattr(identity,'prctl',lambda *args:calls.append(args))
    monkeypatch.setattr('builtins.open',mock_open(read_data=status(allowed | (1 << 21))))
    with pytest.raises(RuntimeError,match='capability policy'): identity.protect_supervisor()
    assert not calls
    monkeypatch.setattr('builtins.open',mock_open(read_data=status(allowed)))
    identity.protect_supervisor()
    assert calls == [(identity.PR_SET_DUMPABLE,0),(identity.PR_SET_NO_NEW_PRIVS,1)]
