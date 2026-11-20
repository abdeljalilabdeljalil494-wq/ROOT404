"""Run real TLS dispatcher/hostile acceptance on a Docker+runsc CI host.

No execution-engine doubles, credential printing, host-source execution or bypass
when the runtime is missing. Artifacts contain whitelisted policy/results only.
"""
import json
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
import ssl
import platform
import shutil
import httpx

root=Path(__file__).resolve().parents[1]
os.chdir(root)
assert os.environ.get('CI') == 'true', 'Use disposable CI worker only'
assert os.environ.get('EXECUTOR_IMAGE'), 'Real immutable built image required'
artifacts=root/'.cache/judge-results'; artifacts.mkdir(parents=True,exist_ok=True)
# A failed rerun must not leave an old green result or mix old policy records.
(artifacts/'result.json').unlink(missing_ok=True)
(artifacts/'acceptance.txt').write_text('NOT RUN: current acceptance has not started\n')
(artifacts/'runtime.json').write_text(json.dumps({'host_kernel':platform.release(),'host_os':platform.system(),
    'docker':json.loads(subprocess.run(['/usr/bin/docker','version','--format','{{json .}}'],check=True,capture_output=True,timeout=15).stdout),
    'runsc':subprocess.run([shutil.which('runsc') or '/usr/local/bin/runsc','--version'],check=True,capture_output=True,timeout=15).stdout.decode()},indent=2))
policy_before=set((artifacts/'policy').glob('*.json'))
volume_before=set((artifacts/'volumes').glob('*.json'))
source_paths=[*Path('executor_service').rglob('*.py'), *Path('judge_sandbox').rglob('*.py'),
              Path('judge_sandbox/Dockerfile.runner'), Path('backend/app/core/judge_protocol.py'), Path('scripts/verify_executor.py'),
              Path('scripts/run_executor_ci.py')]
source_hashes={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(source_paths)}
(artifacts/'source-manifest.json').write_text(json.dumps(source_hashes,indent=2))
with tempfile.TemporaryDirectory(prefix='root404-ci-tls-') as temporary:
    directory=Path(temporary)
    key,cert=directory/'server.key',directory/'server.pem'
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),
                    '-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    secret=secrets.token_hex(48)
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print('::add-mask::'+secret,flush=True)
    env=dict(os.environ,EXECUTOR_SHARED_SECRET=secret,EXECUTOR_CONCURRENCY='2',
             EXECUTOR_LOCK_FILE=str(directory/'worker.lock'),EXECUTOR_REPLAY_DB=str(directory/'claims.sqlite'),EXECUTOR_AUDIT_DIR=str(artifacts/'policy'))
    with (directory/'worker.log').open('wb') as log:
        worker=subprocess.Popen([sys.executable,'-m','uvicorn','executor_service.service:create_app','--factory',
                                 '--host','127.0.0.1','--port','8091','--no-access-log',
                                 '--ssl-keyfile',str(key),'--ssl-certfile',str(cert)],env=env,stdout=log,stderr=log)
        try:
            context=ssl.create_default_context(cafile=str(cert))
            deadline=time.monotonic()+45
            with httpx.Client(verify=context,trust_env=False,timeout=2) as client:
                while True:
                    if worker.poll() is not None: raise RuntimeError('Real worker startup failed; no runtime fallback')
                    try:
                        if client.get('https://127.0.0.1:8091/health',headers={'Authorization':'Bearer '+secret}).status_code==200: break
                    except httpx.HTTPError: pass
                    if time.monotonic()>deadline: raise RuntimeError('Real worker readiness timeout')
                    time.sleep(.2)
            test_env=dict(env,ROOT404_EXECUTOR_TEST_URL='https://127.0.0.1:8091',ROOT404_EXECUTOR_TEST_SECRET=secret,
                          ROOT404_EXECUTOR_CA_FILE=str(cert),ROOT404_EXECUTOR_ALLOW_HOSTILE_TESTS='yes',ROOT404_EXECUTOR_HOST_AUDIT='yes')
            with (artifacts/'acceptance.txt').open('w') as output:
                subprocess.run([sys.executable,'scripts/verify_executor.py'],env=test_env,check=True,stdout=output,stderr=subprocess.STDOUT,timeout=600)
            # Verify durable replay claims through an ACTUAL controller restart,
            # keeping the private replay DB/certificate/secret unchanged.
            restart_id=secrets.token_hex(16)
            restart_job={'files':{'main.py':'print(42)'},'language':'python','stdin':'','timeout_seconds':2,'output_limit_bytes':8192}
            restart_headers={'Authorization':'Bearer '+secret,'X-Root404-Request-ID':restart_id,'X-Root404-Request-Time':str(int(time.time()))}
            with httpx.Client(verify=context,trust_env=False,timeout=100) as client:
                response=client.post('https://127.0.0.1:8091/v2/execute',headers=restart_headers,json=restart_job)
                assert response.status_code==200
            worker.terminate(); worker.wait(timeout=20)
            worker=subprocess.Popen([sys.executable,'-m','uvicorn','executor_service.service:create_app','--factory',
                '--host','127.0.0.1','--port','8091','--no-access-log','--ssl-keyfile',str(key),'--ssl-certfile',str(cert)],env=env,stdout=log,stderr=log)
            deadline=time.monotonic()+45
            with httpx.Client(verify=context,trust_env=False,timeout=2) as client:
                while True:
                    if worker.poll() is not None: raise RuntimeError('Worker restart failed')
                    try:
                        if client.get('https://127.0.0.1:8091/health',headers={'Authorization':'Bearer '+secret}).status_code==200: break
                    except httpx.HTTPError: pass
                    if time.monotonic()>deadline: raise RuntimeError('Restart readiness timeout')
                    time.sleep(.2)
                restart_headers['X-Root404-Request-Time']=str(int(time.time()))
                assert client.post('https://127.0.0.1:8091/v2/execute',headers=restart_headers,json=restart_job).status_code==409
            with (artifacts/'acceptance.txt').open('a') as output:
                output.write('PASS: persistent request identity rejected after actual controller restart\n')
            policies=[json.loads(p.read_text()) for p in set((artifacts/'policy').glob('*.json'))-policy_before]
            assert policies, 'No independent Docker inspect policy evidence'
            volumes=[json.loads(p.read_text()) for p in set((artifacts/'volumes').glob('*.json'))-volume_before]
            assert volumes, 'No independently inspected bounded tmpfs volumes'
            from executor_service.host_supervisor import TMPFS_OPTIONS
            for volume in volumes:
                assert volume['Driver']=='local'
                assert volume['Options']=={'type':'tmpfs','device':'tmpfs','o':TMPFS_OPTIONS}
            allowed_volumes={volume['Name'] for volume in volumes}
            for policy in policies:
                host=policy['host_config']
                assert policy['user']=='1000:1000' and host['Runtime']=='runsc'
                assert host['NetworkMode']=='none' and host['ReadonlyRootfs']
                assert host['Memory']==268435456 and host['MemorySwap']==268435456 and host['NanoCpus']==1000000000
                assert host['PidsLimit']==64 and not host['Privileged'] and not host.get('Binds')
                assert not host['CapAdd']
                mounts=host['Mounts']
                assert len(mounts)==1 and mounts[0]['Type']=='volume' and mounts[0]['Target']=='/workspace'
                assert mounts[0]['Source'] in allowed_volumes
                assert host['CapDrop']==['ALL'] and 'no-new-privileges:true' in host['SecurityOpt']
            (artifacts/'result.json').write_text(json.dumps({'status':'VERIFIED','scope':'targeted real CI acceptance, not independent escape certification',
                      'commit':os.environ.get('GITHUB_SHA'),'image':env['EXECUTOR_IMAGE'],'inspected_jobs':len(policies)}))
        except BaseException as failure:
            (artifacts/'result.json').write_text(json.dumps({'status':'FAILED','exception_type':type(failure).__name__,
                'commit':os.environ.get('GITHUB_SHA'),'image':env['EXECUTOR_IMAGE']}))
            raise
        finally:
            worker.terminate()
            try: worker.wait(timeout=20)
            except subprocess.TimeoutExpired: worker.kill();worker.wait(timeout=5)
            log.flush()
            (artifacts/'worker.log').write_text((directory/'worker.log').read_text(errors='replace')[-262144:].replace(secret,'[REDACTED]'))
