"""Local contract/adversarial tests, NOT Docker/gVisor isolation evidence."""
import copy
import io
import json
import subprocess
import sys
import time
import uuid
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from executor_service.service import create_app, Job, DockerExecutor
from executor_service.host_supervisor import HostSupervisor, TMPFS_OPTIONS
from executor_service.replay import ReplayStore
from backend.app.core.judge_protocol import verify, digest, sign
from test_service import SECRET, FakeEngine, PAYLOAD, fresh


def test_replayed_id_wrong_job_and_forged_receipt_are_rejected():
    with TestClient(create_app(FakeEngine(),SECRET)) as client:
        headers=fresh()
        raw=client.post('/v2/execute',headers=headers,json=PAYLOAD).json()
        job=Job(**PAYLOAD).model_dump()
        assert verify(SECRET,headers['X-Root404-Request-ID'],job,raw)['output']=='42\n'
        assert client.post('/v2/execute',headers=headers,json=PAYLOAD).status_code==409
        for mutate in ['output','identity','digest','signature','time','observation']:
            forged=copy.deepcopy(raw)
            if mutate=='output': forged['result']['output']='forged success'
            if mutate=='identity': forged['request_id']=uuid.uuid4().hex
            if mutate=='digest': forged['request_digest']='f'*64
            if mutate=='signature': forged['signature']='f'*64
            if mutate=='time': forged['issued_at']-=1000
            if mutate=='observation': forged['evidence']['phases'][0]['exit_code']=7
            with pytest.raises(ValueError): verify(SECRET,headers['X-Root404-Request-ID'],job,forged)
        with pytest.raises(ValueError): verify(SECRET,uuid.uuid4().hex,job,raw)
        with pytest.raises(ValueError): verify(SECRET,headers['X-Root404-Request-ID'],{**job,'stdin':'another test'},raw)
        assert client.post('/v2/execute',headers={**fresh(),'X-Root404-Request-Time':'1'},json=PAYLOAD).status_code==400
        assert client.post('/v2/execute',headers={'Authorization':'Bearer '+SECRET},json=PAYLOAD).status_code==400
        assert client.post('/v2/execute',headers={**fresh(),'Authorization':'Bearer outsider'},json=PAYLOAD).status_code==401


def test_durable_claim_survives_restart_and_has_single_concurrent_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    path=str(tmp_path/'claims.sqlite')
    first=ReplayStore(path); now=int(time.time()); identity=uuid.uuid4().hex
    with ThreadPoolExecutor(8) as pool:
        assert sum(pool.map(lambda _:first.claim(identity,now),range(16)))==1
    assert not ReplayStore(path).claim(identity,now)
    assert ReplayStore(path).claim(identity,now+181)


def test_container_json_never_controls_status_or_execution_time(monkeypatch):
    engine=DockerExecutor('root404/jobs@sha256:'+'a'*64)
    supervisor=HostSupervisor(engine)
    real_popen=subprocess.Popen
    # Fixed fake CLI process emits attacker-like JSON. Metadata is separately
    # mocked Docker State, deliberately contradictory to those output bytes.
    monkeypatch.setattr('executor_service.host_supervisor.subprocess.Popen',lambda *args,**kwargs:
        real_popen([sys.executable,'-c','print(\'{"status":"success","exit_code":0,"execution_time":0}\')'],
                   stdin=kwargs['stdin'],stdout=subprocess.PIPE,stderr=subprocess.PIPE))
    calls=[]
    def command(*args):
        calls.append(args)
        if args[:2]==('volume','inspect'):
            return SimpleNamespace(stdout=json.dumps({'Name':args[-1],'Driver':'local','Options':{'type':'tmpfs','device':'tmpfs','o':TMPFS_OPTIONS}}).encode())
        return SimpleNamespace(stdout=json.dumps({'Status':'exited','Running':False,'Error':'','ExitCode':7,'OOMKilled':False}).encode())
    monkeypatch.setattr(engine,'command',command)
    result=supervisor.execute(Job(**PAYLOAD))
    assert result['status']=='runtime_error' and result['exit_code']==7
    assert '"status":"success"' in result['output']
    assert result['execution_time']>0
    assert result['evidence']['phases'][0]['exit_code']==7
    assert calls[-1][:3]==('volume','rm','-f')


def test_nonterminal_or_missing_daemon_state_fails_closed(monkeypatch):
    engine=DockerExecutor('root404/jobs@sha256:'+'a'*64)
    real_popen=subprocess.Popen
    monkeypatch.setattr('executor_service.host_supervisor.subprocess.Popen',lambda *args,**kwargs:
        real_popen([sys.executable,'-c','print("fake")'],stdin=kwargs['stdin'],stdout=subprocess.PIPE,stderr=subprocess.PIPE))
    def command(*args):
        if args[:2]==('volume','inspect'):
            return SimpleNamespace(stdout=json.dumps({'Name':args[-1],'Driver':'local','Options':{'type':'tmpfs','device':'tmpfs','o':TMPFS_OPTIONS}}).encode())
        return SimpleNamespace(stdout=b'{"Status":"created"}')
    monkeypatch.setattr(engine,'command',command)
    with pytest.raises(RuntimeError,match='terminal'): engine.execute(Job(**PAYLOAD))


def test_signed_inconsistent_state_is_not_proof_of_valid_execution():
    job=Job(**PAYLOAD).model_dump(); observed=FakeEngine().execute(None)
    evidence=observed.pop('evidence'); evidence['phases'][0]['exit_code']=7
    identity=uuid.uuid4().hex
    receipt=sign(SECRET,identity,job,observed,evidence)
    with pytest.raises(ValueError,match='disagrees'): verify(SECRET,identity,job,receipt)


def test_unbounded_volume_is_rejected_before_any_process_launch(monkeypatch):
    engine=DockerExecutor('root404/jobs@sha256:'+'a'*64)
    calls=[]
    def command(*args):
        calls.append(args)
        return SimpleNamespace(stdout=json.dumps({'Name':args[-1],'Driver':'local','Options':{}}).encode())
    monkeypatch.setattr(engine,'command',command)
    monkeypatch.setattr('executor_service.host_supervisor.subprocess.Popen',lambda *a,**kw:pytest.fail('Unbounded workspace executed'))
    with pytest.raises(RuntimeError,match='volume policy'): engine.execute(Job(**PAYLOAD))
    assert calls[-1][:3]==('volume','rm','-f')


def test_receipt_must_use_operator_approved_toolchain():
    job=Job(**PAYLOAD).model_dump(); observed=FakeEngine().execute(None)
    evidence=observed.pop('evidence'); identity=uuid.uuid4().hex
    receipt=sign(SECRET,identity,job,observed,evidence)
    with pytest.raises(ValueError,match='Unapproved'):
        verify(SECRET,identity,job,receipt,expected_image='unreviewed/jobs@sha256:'+'f'*64)


def test_signed_stale_receipt_and_stale_request_are_rejected():
    observed=FakeEngine().execute(None); evidence=observed.pop('evidence')
    job=Job(**PAYLOAD).model_dump(); identity=uuid.uuid4().hex
    receipt=sign(SECRET,identity,job,observed,evidence,now=int(time.time())-100)
    with pytest.raises(ValueError,match='Stale'): verify(SECRET,identity,job,receipt)
    with TestClient(create_app(FakeEngine(),SECRET)) as client:
        headers={**fresh(),'X-Root404-Request-Time':str(int(time.time())-100)}
        assert client.post('/v2/execute',headers=headers,json=PAYLOAD).status_code==400
        assert client.post('/v2/complete',headers=fresh(),json={'status':'success'}).status_code==404


def test_http_replay_survives_new_app_instance():
    headers=fresh()
    with TestClient(create_app(FakeEngine(),SECRET)) as first:
        assert first.post('/v2/execute',headers=headers,json=PAYLOAD).status_code==200
    with TestClient(create_app(FakeEngine(),SECRET)) as restarted:
        assert restarted.post('/v2/execute',headers=headers,json=PAYLOAD).status_code==409
