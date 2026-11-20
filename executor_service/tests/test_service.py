"""Contract/control tests; not Docker, gVisor, cgroup or isolation evidence."""
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import uuid
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from executor_service.service import Job, DockerExecutor, create_app

SECRET = 's' * 64
HEADERS = {'Authorization': 'Bearer ' + SECRET}

def fresh():
    return {**HEADERS,'X-Root404-Request-ID':uuid.uuid4().hex,'X-Root404-Request-Time':str(int(time.time()))}

RESULT = {'status': 'success', 'output': '42\n', 'error': '', 'exit_code': 0, 'execution_time': .01}
PAYLOAD = {'files': {'main.py': 'print(42)'}, 'language': 'python'}


class FakeEngine:
    def ready(self): pass
    def execute(self, job):
        return {**RESULT,'evidence':{'image':'root404/jobs@sha256:'+'a'*64,'phases':[
            {'phase':'run','container':'root404-job-'+'b'*32+'-run','exit_code':0,
             'oom_killed':False,'timed_out':False,'output_limited':False}]}}


def test_auth_strict_validation_body_limit_and_result():
    with TestClient(create_app(FakeEngine(), SECRET)) as client:
        assert client.post('/v2/execute', json=PAYLOAD).status_code == 401
        assert client.post('/v2/execute', headers=fresh(), json=PAYLOAD).json()['result'] == RESULT
        for name in ['../x.py', '/x.py', 'x/../y.py', '-x.py', 'x//y.py', 'x;touch.py', '.root404-program']:
            assert client.post('/v2/execute', headers=fresh(), json={**PAYLOAD, 'files': {name: ''}}).status_code == 422
        assert client.post('/v2/execute', headers=fresh(), json={**PAYLOAD, 'timeout_seconds': 31}).status_code == 422
        assert client.post('/v2/execute', headers=fresh(), json={**PAYLOAD, 'command': 'sh'}).status_code == 422
        assert client.post('/v2/execute', headers=fresh(), content=b'x'*1048577).status_code == 413
        assert client.get('/openapi.json', headers=fresh()).status_code == 404


def test_concurrency_is_bounded_and_slot_released_on_failure():
    started, release = threading.Event(), threading.Event()
    class Engine(FakeEngine):
        def execute(self, job):
            started.set(); release.wait(3)
            raise RuntimeError('sensitive daemon error')
    with TestClient(create_app(Engine(), SECRET, 1)) as client, ThreadPoolExecutor(2) as pool:
        active = pool.submit(client.post, '/v2/execute', headers=fresh(), json=PAYLOAD)
        assert started.wait(2)
        assert client.post('/v2/execute', headers=fresh(), json=PAYLOAD).status_code == 429
        release.set()
        response = active.result()
        assert response.status_code == 503 and 'sensitive' not in response.text
        assert client.post('/v2/execute', headers=fresh(), json=PAYLOAD).status_code == 503


def test_engine_requires_digest_and_strong_secret():
    with pytest.raises(ValueError): DockerExecutor('ubuntu:latest')
    with pytest.raises(ValueError): create_app(FakeEngine(), 'short')
    with pytest.raises(ValidationError): Job(**{**PAYLOAD, 'stdin': 'x'*10241})


def test_runtime_policy_and_cleanup_on_start_failure(monkeypatch):
    calls=[]
    engine=DockerExecutor('root404/jobs@sha256:'+'a'*64)
    def command(*args):
        import json
        from types import SimpleNamespace
        from executor_service.host_supervisor import TMPFS_OPTIONS
        calls.append(args)
        return SimpleNamespace(stdout=json.dumps({'Name':args[-1],'Driver':'local',
            'Options':{'type':'tmpfs','device':'tmpfs','o':TMPFS_OPTIONS}}).encode())
    monkeypatch.setattr(engine,'command',command)
    monkeypatch.setattr('executor_service.host_supervisor.subprocess.Popen',lambda *args,**kwargs:(_ for _ in ()).throw(OSError('Cannot start')))
    with pytest.raises(OSError): engine.execute(Job(**PAYLOAD))
    command=next(call for call in calls if call[0]=='create')
    for flag in ['--runtime=runsc','--network=none','--read-only','--user=1000:1000','--cap-drop=ALL',
                 '--security-opt=no-new-privileges:true','--pids-limit=64','--memory=256m','--cpus=1']:
        assert flag in command
    assert not any('docker.sock' in arg or arg.startswith('--cap-add') or arg in ['--privileged','--volume','-v'] for arg in command)
    assert calls[0][:2]==('volume','create')
    assert '--opt=type=tmpfs' in calls[0] and '--opt=o=size=64m,uid=1000,gid=1000,mode=0700,nosuid,nodev' in calls[0]
    assert calls[-1][:3]==('volume','rm','-f')


def test_image_runtime_cgroup_seccomp_preflight_and_startup_cleanup(monkeypatch, tmp_path):
    import json
    from types import SimpleNamespace
    monkeypatch.setenv('EXECUTOR_LOCK_FILE',str(tmp_path/'worker.lock'))
    engine=DockerExecutor('root404/job@sha256:'+'b'*64)
    calls=[]
    def command(*args):
        calls.append(args)
        if args[0]=='info':
            return SimpleNamespace(stdout=json.dumps({'Runtimes':{'runsc':{}},'CgroupVersion':'2',
                'SecurityOptions':['name=seccomp,profile=builtin']}).encode())
        if args[0]=='ps': return SimpleNamespace(stdout=b'aabbccddeeff\n')
        return SimpleNamespace(stdout=b'{}')
    monkeypatch.setattr(engine,'command',command)
    engine.ready()
    assert ('rm','-f','-v','aabbccddeeff') in calls
    engine.lock_file.close()


def test_no_mutable_runtime_fallback_if_gvisor_missing(monkeypatch,tmp_path):
    import json
    from types import SimpleNamespace
    monkeypatch.setenv('EXECUTOR_LOCK_FILE',str(tmp_path/'worker.lock'))
    engine=DockerExecutor('root404/job@sha256:'+'c'*64)
    monkeypatch.setattr(engine,'command',lambda *args:SimpleNamespace(stdout=json.dumps({'Runtimes':{'runc':{}},'CgroupVersion':'2','SecurityOptions':['name=seccomp']}).encode()))
    with pytest.raises(RuntimeError):engine.ready()
    engine.lock_file.close()
