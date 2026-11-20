"""Local shared-state evidence, not a PostgreSQL production/concurrency certification."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import os
import subprocess
import sys
import uuid
from sqlalchemy import update
import pytest
from app.core.rate_limit import RateLimiter
from app.core.database import SessionLocal
from app.models.auth_state import AuthThrottle


def test_independent_limiter_instances_share_one_atomic_budget():
    key = 'concurrent:' + uuid.uuid4().hex
    def attempt(_):
        return RateLimiter().is_allowed(key, 5, 60)[0]
    with ThreadPoolExecutor(max_workers=8) as workers:
        results = list(workers.map(attempt, range(16)))
    assert sum(results) == 5


def test_budget_survives_a_separate_process():
    key = 'process:' + uuid.uuid4().hex
    assert RateLimiter().is_allowed(key, 1, 60) == (True, 0)
    source = 'from app.core.rate_limit import RateLimiter; import sys; allowed, retry = RateLimiter().is_allowed(sys.argv[1],1,60); assert not allowed and retry > 0'
    env = dict(os.environ, PYTHONPATH='backend')
    subprocess.run([sys.executable, '-c', source, key], env=env, check=True, capture_output=True)


def test_expired_request_window_restarts():
    key = 'expired:' + uuid.uuid4().hex
    limiter = RateLimiter()
    assert limiter.is_allowed(key, 1, 60)[0]
    assert not limiter.is_allowed(key, 1, 60)[0]
    with SessionLocal() as db:
        db.execute(update(AuthThrottle).where(AuthThrottle.key.like('req:%')).values(expires_at=datetime.utcnow() - timedelta(seconds=1)))
        db.commit()
    assert limiter.is_allowed(key, 1, 60) == (True, 0)


def test_invalid_budget_is_not_silently_accepted():
    with pytest.raises(ValueError):
        RateLimiter().is_allowed('bad', 0, 60)
