"""Trusted HOST-ONLY lifecycle/result authority. Never imported by job images.

Learner bytes are only stdout/stderr, never a JSON result or exit-code authority.
Docker daemon State is independently queried after each disposable phase. A unique,
size-limited tmpfs Docker volume transfers compiler artifacts, without host binds,
archive extraction, code execution on host, or shared PID namespaces.
"""
import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time
import uuid


TMPFS_OPTIONS='size=64m,uid=1000,gid=1000,mode=0700,nosuid,nodev'


class HostSupervisor:
    def __init__(self, engine):
        self.engine = engine

    def phase(self, job, phase, name, volume, observations):
        engine = self.engine
        args = ['create', '--name', name, '--pull=never', '--interactive',
                '--runtime=runsc', '--network=none', '--read-only', '--user=1000:1000',
                '--cap-drop=ALL', '--security-opt=no-new-privileges:true',
                '--pids-limit=64', '--memory=256m', '--memory-swap=256m', '--cpus=1',
                '--ulimit=nofile=64:64', '--ulimit=core=0:0', '--ipc=none',
                '--log-driver=none', '--restart=no', '--label=io.root404.executor=job',
                '--mount=type=volume,src='+volume+',dst=/workspace,volume-nocopy',
                '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=16m,uid=1000,gid=1000,mode=0700',
                '--entrypoint=/usr/bin/python3', engine.image, '-I', '/opt/judge/launch.py', phase]
        engine.command(*args)
        output = {'output': bytearray(), 'error': bytearray()}
        timed_out = limited = False
        with tempfile.TemporaryFile() as incoming:
            incoming.write(job.model_dump_json().encode()); incoming.seek(0)
            process = subprocess.Popen([engine.docker, 'start', '--attach', '--interactive', name],
                stdin=incoming, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + job.timeout_seconds + 15
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ, 'output')
                    selector.register(process.stderr, selectors.EVENT_READ, 'error')
                    while selector.get_map():
                        remaining = deadline-time.monotonic()
                        if remaining <= 0:
                            timed_out = True; break
                        for key, _ in selector.select(min(.1, remaining)):
                            target = output[key.data]
                            data = os.read(key.fd, min(8192, job.output_limit_bytes+1-len(target)))
                            if not data: selector.unregister(key.fileobj)
                            else: target.extend(data)
                        if any(len(data)>job.output_limit_bytes for data in output.values()):
                            limited = True; break
                if timed_out or limited:
                    engine.command('kill', name)
                try: process.wait(timeout=5 if timed_out or limited else max(.01, deadline-time.monotonic()))
                except subprocess.TimeoutExpired:
                    timed_out = True
                    engine.command('kill', name)
                    process.wait(timeout=5)
            finally:
                if process.poll() is None:
                    process.kill(); process.wait(timeout=5)
                process.stdout.close(); process.stderr.close()
        state = json.loads(engine.command('inspect', '--format', '{{json .State}}', name).stdout)
        # CLI text/return code and anything printed by the learner are NOT metadata.
        if state.get('Status') != 'exited' or state.get('Running') or state.get('Error') or type(state.get('ExitCode')) is not int:
            raise RuntimeError('No independently observed terminal container state')
        if not timed_out and not limited and process.returncode not in {0,state['ExitCode']}:
            raise RuntimeError('Attach failed; output completeness unverified')
        if type(state.get('OOMKilled')) is not bool:
            raise RuntimeError('Missing OOM observation')
        observations.append({'phase': phase, 'container': name, 'exit_code': state['ExitCode'],
                             'oom_killed': state['OOMKilled'], 'timed_out': timed_out, 'output_limited': limited})
        audit_dir = os.environ.get('EXECUTOR_AUDIT_DIR')
        if audit_dir:
            info = json.loads(engine.command('inspect', '--format', '{{json .}}', name).stdout)
            path = Path(audit_dir); path.mkdir(parents=True, exist_ok=True, mode=0o700)
            (path/(name+'.json')).write_text(json.dumps({'user': info['Config']['User'],
                'host_config': {key: info['HostConfig'].get(key) for key in ['Runtime','NetworkMode','ReadonlyRootfs',
                    'Memory','MemorySwap','NanoCpus','PidsLimit','Privileged','Binds','CapDrop','CapAdd','Mounts','SecurityOpt']},
                'observation': observations[-1]}))
        status = ('memory_limit' if state['OOMKilled'] else 'timeout' if timed_out or state['ExitCode']==152 else 'output_limit' if limited
                  else 'success' if state['ExitCode']==0 else 'compilation_error' if phase=='compile' else 'runtime_error')
        return {'status': status, 'exit_code': state['ExitCode'],
                **{key: bytes(value[:job.output_limit_bytes]).decode(errors='replace') for key,value in output.items()}}

    def execute(self, job):
        engine = self.engine
        if getattr(engine, 'tainted', False):
            raise RuntimeError('Worker requires recovery')
        started = time.monotonic()
        identity = uuid.uuid4().hex
        volume = 'root404-work-'+identity
        names, observations = [], []
        try:
            # Docker-managed tmpfs volume, NOT an unbounded disk volume or host bind.
            engine.command('volume','create','--driver=local','--label=io.root404.executor=job',
                '--opt=type=tmpfs','--opt=device=tmpfs',
                '--opt=o='+TMPFS_OPTIONS,volume)
            actual=json.loads(engine.command('volume','inspect','--format','{{json .}}',volume).stdout)
            if actual.get('Name')!=volume or actual.get('Driver')!='local' or actual.get('Options')!={'type':'tmpfs','device':'tmpfs','o':TMPFS_OPTIONS}:
                raise RuntimeError('Workspace volume policy mismatch')
            audit=os.environ.get('EXECUTOR_AUDIT_DIR')
            if audit:
                destination=Path(audit).parent/'volumes'
                destination.mkdir(parents=True,exist_ok=True,mode=0o700)
                (destination/(volume+'.json')).write_text(json.dumps({key:actual[key] for key in ['Name','Driver','Options']}))
            phases = ['compile','run'] if job.language in {'c','cpp','c++'} else ['run']
            for phase in phases:
                name = 'root404-job-'+identity+'-'+phase
                names.append(name)
                result = self.phase(job,phase,name,volume,observations)
                if result['status']!='success': break
            result['execution_time'] = time.monotonic()-started
            return {**result, 'evidence': {'image': engine.image, 'phases': observations}}
        finally:
            failures = []
            # Try every cleanup even if an earlier one fails. No silent success.
            for name in names:
                try: engine.command('rm','-f','-v',name)
                except (OSError,subprocess.SubprocessError): failures.append(name)
            try: engine.command('volume','rm','-f',volume)
            except (OSError,subprocess.SubprocessError): failures.append(volume)
            if failures:
                engine.tainted = True
                raise RuntimeError('Cleanup failed; worker drained')
