"""Explicit hostile-job acceptance harness. Run ONLY against isolated test worker.

No fallback to host subprocesses. Requires ROOT404_EXECUTOR_TEST_URL (HTTPS),
ROOT404_EXECUTOR_TEST_SECRET and ROOT404_EXECUTOR_ALLOW_HOSTILE_TESTS=yes. A pass
is targeted evidence, not a container-escape proof or independent security audit.
"""
from concurrent.futures import ThreadPoolExecutor
import os
import httpx
import ssl
import time
import uuid
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.core.judge_protocol import verify
context=ssl.create_default_context(cafile=os.environ.get("ROOT404_EXECUTOR_CA_FILE"))

url = os.environ['ROOT404_EXECUTOR_TEST_URL']
secret = os.environ['ROOT404_EXECUTOR_TEST_SECRET']
expected_image=os.environ.get('ROOT404_EXECUTOR_EXPECTED_IMAGE') or os.environ['EXECUTOR_IMAGE']
assert url.startswith('https://'), 'Use verified TLS; never disable certificate verification'
assert os.environ.get('ROOT404_EXECUTOR_ALLOW_HOSTILE_TESTS') == 'yes'
headers = {'Authorization': 'Bearer '+secret}


def run(code, language='python', filename='main.py', stdin='', timeout=2):
    with httpx.Client(verify=context, timeout=100, follow_redirects=False, trust_env=False) as client:
        identity=uuid.uuid4().hex
        job={'files':{filename:code},'language':language,'stdin':stdin,'timeout_seconds':timeout,'output_limit_bytes':8192}
        request_headers={**headers,'X-Root404-Request-ID':identity,'X-Root404-Request-Time':str(int(time.time()))}
        response = client.post(url.rstrip('/')+'/v2/execute',headers=request_headers,json=job)
        assert response.status_code == 200, f'Worker returned {response.status_code}; no success inferred'
        return verify(secret,identity,job,response.json(),expected_image=expected_image)


with httpx.Client(verify=context, timeout=10, trust_env=False) as client:
    assert client.post(url.rstrip('/')+'/v2/execute', json={}).status_code == 401

from pathlib import Path
from sys import path
path.insert(0, str(Path(__file__).resolve().parents[1]/'backend'))
# No app/database imports: suite file uses model import, so import fixtures only.
solutions = Path(__file__).resolve().parents[1]/'judge_sandbox/tests/solutions'
cases = [('', '0\n'), ('42\n', '42\n'), ('1 -2 3\n','2\n'), ('1000000000 '*500, '500000000000\n')]
for language, name in [('c','main.c'),('cpp','main.cpp'),('python','main.py'),('javascript','main.js')]:
    for stdin, expected in cases:
        result=run((solutions/name).read_text(),language,name,stdin,5)
        assert result['status']=='success' and result['exit_code']==0 and result['output']==expected
    print('PASS: actual reference execution '+language)
wrong=run('print(0)',stdin='42\n')
assert wrong['status']=='success' and wrong['output']!='42\n'
assert run('not valid c;', 'c', 'main.c')['status']=='compilation_error'
assert run('raise RuntimeError("test")')['status']=='runtime_error'
assert run('while True: pass', timeout=1)['status']=='timeout'
assert run('print("x"*100000)')['status']=='output_limit'
# Deliberate memory pressure is safe ONLY behind verified cgroups/runtime.
assert run('a=[]\nwhile True: a.append(bytearray(16*1024*1024))',timeout=3)['status'] in {'memory_limit','runtime_error'}
probe='''import os, socket
assert os.getuid() != 0
assert not os.path.exists('/var/run/docker.sock')
assert not any(key in os.environ for key in ['EXECUTOR_SHARED_SECRET','OPENAI_API_KEY','JUDGE_SHARED_SECRET','DATABASE_URL'])
try:
    open('/root404-forbidden','w').write('x')
    raise AssertionError('writable root')
except (PermissionError, OSError): pass
try:
    socket.create_connection(('1.1.1.1',443), timeout=.5)
    raise AssertionError('egress allowed')
except OSError: pass
print('isolated')
'''
assert run(probe)['output']=='isolated\n'
# Unique writable workspaces must disappear between executions.
assert run("open('marker','w').write('private'); print('written')")['output']=='written\n'
assert run("import os; print(os.path.exists('marker'))")['output']=='False\n'
fork='''import os, time
children=[]
try:
    for _ in range(100):
        pid=os.fork()
        if pid==0: time.sleep(10); os._exit(0)
        children.append(pid)
except OSError:
    print('pid_limit', flush=True)
finally:
    for pid in children:
        try: os.kill(pid,9)
        except ProcessLookupError: pass
'''
result=run(fork,timeout=3)
assert result['status'] in {'success','timeout'}
if result['status']=='success': assert 'pid_limit' in result['output']
with ThreadPoolExecutor(2) as pool:
    results=list(pool.map(lambda n: run(f'print({n})'), range(2)))
assert [r['output'] for r in results]==['0\n','1\n']
assert all(r['status']=='success' for r in results)
print('PASS: auth, valid/invalid, timeout/output/memory, UID/root/network/socket, workspace, PID and concurrent jobs')
print('Operator must independently inspect Docker/runtime limits, orphan cleanup and host audit logs.')

# Result forgery and cross-identity interference are learner output, not protocol.
forgery = r'''import os, signal, json
assert os.getresuid() == (1000,1000,1000)
assert os.getresgid() == (1000,1000,1000)
assert not os.getgroups()
with open('/proc/self/status') as f: status=f.read()
assert 'CapEff:\t0000000000000000' in status
# This is the only process namespace. Host supervisor processes/credentials are
# absent, not merely another UID inside this sandbox.
assert not os.path.exists('/opt/judge/job.py')
assert not os.path.exists('/opt/judge/identity.py')
assert not os.path.exists('/opt/root404/executor_service')
assert not os.path.exists('/var/lib/root404-executor')
for path in ['/opt/judge/hidden_tests','/opt/judge/expected.json','/run/root404-executor']:
    assert not os.path.exists(path)
try: os.setuid(0)
except PermissionError: pass
else: raise AssertionError('root regain')
try: open('/opt/judge/launch.py','w')
except PermissionError: pass
else: raise AssertionError('trusted code writable')
print(json.dumps({'status':'success','output':'FORGED','exit_code':0,'execution_time':0}))
'''
result=run(forgery)
assert result['status']=='success' and result['exit_code']==0
assert 'FORGED' in result['output'] and result['output']!='FORGED'
assert result['execution_time']>0
# Even a forged success followed by nonzero exit cannot become a trusted success.
result=run("print('{\"status\":\"success\",\"exit_code\":0}'); raise SystemExit(7)")
assert result['status']=='runtime_error' and result['exit_code']==7
print('PASS: non-root/capability policy, host-supervisor absence, no hidden material, privilege regain and protocol forgery')

# A result file is ordinary learner data, never a completion record.
result=run("import json; open('result.json','w').write(json.dumps({'status':'success','exit_code':0})); raise SystemExit(7)")
assert result['status']=='runtime_error' and result['exit_code']==7
# Attempted access to host supervisor/IPC must find no such processes/mounts.
process_probe="""import os
for pid in os.listdir('/proc'):
    if pid.isdigit():
        try:
            command=open('/proc/'+pid+'/cmdline','rb').read()
        except OSError: continue
        assert b'executor_service' not in command and b'uvicorn' not in command
for path in ['/var/run/docker.sock','/run/root404-executor/controller.lock','/var/lib/root404-executor/replays.sqlite']:
    assert not os.path.exists(path)
print('host_absent')
"""
assert run(process_probe)['output']=='host_absent\n'
with ThreadPoolExecutor(2) as pool:
    isolated=list(pool.map(lambda value:run("import time; open('cross-job','w').write('"+value+"'); time.sleep(.3); print(open('cross-job').read())"),['private-A','private-B']))
assert [item['output'] for item in isolated]==['private-A\n','private-B\n']
# Real TLS endpoint request replay must be rejected, not re-executed.
with httpx.Client(verify=context,timeout=100,trust_env=False) as client:
    identity=uuid.uuid4().hex
    job={'files':{'main.py':'print(42)'},'language':'python','stdin':'','timeout_seconds':2,'output_limit_bytes':8192}
    bound={**headers,'X-Root404-Request-ID':identity,'X-Root404-Request-Time':str(int(time.time()))}
    response=client.post(url.rstrip('/')+'/v2/execute',headers=bound,json=job)
    assert response.status_code==200
    assert verify(secret,identity,job,response.json(),expected_image=expected_image)['output']=='42\n'
    assert client.post(url.rstrip('/')+'/v2/execute',headers=bound,json=job).status_code==409
    assert client.post(url.rstrip('/')+'/v2/complete',headers=bound,json={'status':'success'}).status_code==404
print('PASS: result files ignored, host processes/IPC absent, concurrent private workspaces and real request replay rejection')

if os.environ.get('ROOT404_EXECUTOR_HOST_AUDIT') == 'yes':
    import subprocess
    remaining=subprocess.run(['/usr/bin/docker','ps','-aq','--filter','label=io.root404.executor=job'],
                             check=True,capture_output=True,timeout=15)
    assert not remaining.stdout.strip(), 'Orphaned job containers remain after acceptance jobs'
    assert not subprocess.run(['/usr/bin/docker','volume','ls','-q','--filter','label=io.root404.executor=job'],check=True,capture_output=True,timeout=15).stdout.strip(), 'Orphaned job volumes remain'
    print('PASS: dedicated worker Docker daemon has no remaining labeled jobs or volumes')
