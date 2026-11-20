"""Authenticated, bounded HTTP dispatcher for fresh gVisor Docker jobs.

This process is a trusted host-side controller, not a submission container. Docker
access is administrative authority: never deploy it in the API/frontend or mount
its daemon socket into any container. No submitted value becomes a CLI option.
"""
import hmac
import sqlite3
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

MAX_BODY = 1048576
MAX_RESULT = 262144


class Job(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    files: dict[str, str] = Field(min_length=1, max_length=20)
    language: str
    stdin: str = ''
    timeout_seconds: int = Field(default=5, ge=1, le=30)
    output_limit_bytes: int = Field(default=65536, ge=1024, le=65536)

    @model_validator(mode='after')
    def valid_job(self):
        if self.language not in {'c', 'cpp', 'c++', 'python', 'py', 'javascript', 'js'}:
            raise ValueError('Unsupported language')
        total = 0
        for name, content in self.files.items():
            if (len(name) > 100 or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]*', name)
                    or any(part in {'', '.', '..'} or part.startswith('.') for part in name.split('/'))
                    or '\x00' in content):
                raise ValueError('Invalid source filename/content')
            size = len(content.encode())
            if size > 262144:
                raise ValueError('File too large')
            total += size
        if total > 524288 or len(self.stdin.encode()) > 10240:
            raise ValueError('Submission too large')
        return self


from backend.app.core.judge_protocol import Result, sign, verify
from executor_service.replay import ReplayStore


class DockerExecutor:
    def __init__(self, image, docker='/usr/bin/docker'):
        # Pin the toolchain, never auto-pull a mutable tag during a learner request.
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}', image):
            raise ValueError('EXECUTOR_IMAGE must be an immutable repository digest')
        if not Path(docker).is_absolute():
            raise ValueError('Absolute Docker executable required')
        self.image, self.docker = image, docker

    def command(self, *args, **kwargs):
        return subprocess.run([self.docker, *args], check=True, timeout=15,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, **kwargs)

    def ready(self):
        import fcntl
        lock = os.environ.get('EXECUTOR_LOCK_FILE', '/run/root404-executor/controller.lock')
        self.lock_file = open(lock, 'a')
        fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        info = json.loads(self.command('info', '--format', '{{json .}}').stdout)
        if 'runsc' not in info.get('Runtimes', {}) or not any('name=seccomp' in item for item in info.get('SecurityOptions', [])):
            raise RuntimeError('gVisor runtime/security configuration unavailable')
        if info.get('CgroupVersion') != '2':
            raise RuntimeError('cgroup v2 required')
        self.command('image', 'inspect', self.image)
        # Host boot recovery: only this dedicated worker's job namespace.
        jobs = self.command('ps', '-aq', '--filter', 'label=io.root404.executor=job').stdout.decode().split()
        for job in jobs:
            if re.fullmatch(r'[a-f0-9]{12,64}', job):
                self.command('rm', '-f', '-v', job)
        self.reap_volumes(startup=True)

    def reap_volumes(self, startup=False):
        volumes=self.command('volume','ls','-q','--filter','label=io.root404.executor=job').stdout.decode().split()
        for name in volumes:
            if re.fullmatch(r'root404-work-[a-f0-9]{32}',name):
                attached=self.command('ps','-aq','--filter','volume='+name).stdout.decode().strip()
                if not attached:
                    if not startup:
                        from datetime import datetime, timezone
                        created=self.command('volume','inspect','--format','{{.CreatedAt}}',name).stdout.decode().strip()
                        created=re.sub(r'(\.\d{6})\d+',r'\1',created).replace('Z','+00:00')
                        if (datetime.now(timezone.utc)-datetime.fromisoformat(created)).total_seconds()<120:
                            continue  # active request may be between volume/container create
                    self.command('volume','rm','-f',name)

    def reap_expired(self):
        from datetime import datetime, timezone
        jobs = self.command('ps', '-aq', '--filter', 'label=io.root404.executor=job').stdout.decode().split()
        for job in jobs:
            if not re.fullmatch(r'[a-f0-9]{12,64}', job):
                continue
            created = self.command('inspect', '--format', '{{.Created}}', job).stdout.decode().strip()
            # Docker RFC3339 nanoseconds -> datetime microseconds.
            created = re.sub(r'(\.\d{6})\d+', r'\1', created).replace('Z', '+00:00')
            if (datetime.now(timezone.utc) - datetime.fromisoformat(created)).total_seconds() > 90:
                self.command('rm', '-f', '-v', job)
        self.reap_volumes()

    def execute(self, job):
        from executor_service.host_supervisor import HostSupervisor
        return HostSupervisor(self).execute(job)


def create_app(engine=None, secret=None, concurrency=None):
    secret = secret if secret is not None else os.environ.get('EXECUTOR_SHARED_SECRET', '')
    if len(secret) < 48:
        raise ValueError('A private high-entropy executor secret of >=48 characters is required')
    engine = engine or DockerExecutor(os.environ.get('EXECUTOR_IMAGE', ''))
    concurrency = concurrency if concurrency is not None else int(os.environ.get('EXECUTOR_CONCURRENCY', '2'))
    if not 1 <= concurrency <= 16:
        raise ValueError('Invalid concurrency')
    slots = threading.BoundedSemaphore(concurrency)
    replay = ReplayStore(os.environ.get('EXECUTOR_REPLAY_DB','/var/lib/root404-executor/replays.sqlite'))

    @asynccontextmanager
    async def lifespan(app):
        engine.ready()
        stop = threading.Event()
        def reap():
            # Recover jobs after client/daemon races or controller interruption.
            # No active request can live90 seconds under the policy above.
            while not stop.wait(15):
                try:
                    if hasattr(engine, 'reap_expired'):
                        engine.reap_expired()
                except (OSError, subprocess.SubprocessError, ValueError, RuntimeError):
                    engine.tainted = True  # recovery failures drain worker, not silent health
        reaper = threading.Thread(target=reap, daemon=True)
        reaper.start()
        try:
            yield
        finally:
            stop.set()
            reaper.join(timeout=16)
            if getattr(engine, 'lock_file', None):
                engine.lock_file.close()

    app = FastAPI(title='ROOT404 execution worker', docs_url=None, redoc_url=None,
                  openapi_url=None, lifespan=lifespan)

    request_slots = threading.BoundedSemaphore(concurrency + 4)

    @app.middleware('http')
    async def boundary(request: Request, call_next):
        if not hmac.compare_digest(request.headers.get('authorization', '').encode(), ('Bearer ' + secret).encode()):
            return JSONResponse(status_code=401, content={'detail': 'Unauthorized'})
        if not request_slots.acquire(blocking=False):
            return JSONResponse(status_code=429, content={'detail': 'Worker at capacity'})
        try:
            if request.url.path == '/v2/execute' and request.method == 'POST':
                length = request.headers.get('content-length')
                if length and (not length.isdecimal() or int(length) > MAX_BODY):
                    return JSONResponse(status_code=413, content={'detail': 'Job too large'})
                size, chunks = 0, []
                import asyncio
                try:
                    async with asyncio.timeout(10):
                        async for chunk in request.stream():
                            size += len(chunk)
                            if size > MAX_BODY:
                                return JSONResponse(status_code=413, content={'detail': 'Job too large'})
                            chunks.append(chunk)
                except TimeoutError:
                    return JSONResponse(status_code=408, content={'detail': 'Job body timed out'})
                request._body = b''.join(chunks)
            return await call_next(request)
        finally:
            request_slots.release()

    @app.get('/health')
    def health():
        if getattr(engine, 'tainted', False):
            raise HTTPException(503, 'Worker requires recovery')
        return {'status': 'ok'}

    @app.post('/v2/execute')
    def execute(job: Job, request: Request):
        import time
        now=int(time.time())
        identity=request.headers.get('x-root404-request-id','')
        stamp=request.headers.get('x-root404-request-time','')
        if not re.fullmatch('[a-f0-9]{32}',identity) or not re.fullmatch('[0-9]{10}',stamp) or abs(now-int(stamp))>30:
            raise HTTPException(400,'Fresh request identity required')
        if not slots.acquire(blocking=False):
            raise HTTPException(429, 'Worker at capacity', headers={'Retry-After': '2'})
        try:
            if not replay.claim(identity,now):
                raise HTTPException(409,'Request identity already consumed')
            observed=engine.execute(job)
            result={key:value for key,value in observed.items() if key!='evidence'}
            envelope=sign(secret,identity,job.model_dump(),result,observed['evidence'])
            # Apply the same strict consistency checks before releasing a receipt.
            verify(secret,identity,job.model_dump(),envelope)
            return envelope
        except (OSError, subprocess.SubprocessError, ValueError, RuntimeError, KeyError, sqlite3.Error, ValidationError):
            # Never log code, stdin, credentials, daemon error text or provider output.
            raise HTTPException(503, 'Execution infrastructure unavailable')
        finally:
            slots.release()

    return app
