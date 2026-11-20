"""Shared, atomic SQL fixed-window request budgets (SQLite/PostgreSQL).

No in-memory fallback: a storage outage must not silently disable abuse controls.
The existing auth_throttles table also stores OTP email budgets under separate keys.
"""
from datetime import datetime, timedelta
import hashlib
import math
from sqlalchemy import case, delete
from .database import SessionLocal
from .config import settings
from app.models.auth_state import AuthThrottle


class RateLimiter:
    def __init__(self, session_factory=None):
        self.session_factory = session_factory or SessionLocal

    def is_allowed(self, key: str, max_requests: int, window: int) -> tuple[bool, int]:
        if max_requests < 1 or window < 1:
            raise ValueError("Invalid rate limit budget")
        digest = 'req:' + hashlib.sha256(key.encode()).hexdigest()[:60]
        now = datetime.utcnow()
        expires = now + timedelta(seconds=window)
        with self.session_factory() as db:
            dialect = db.get_bind().dialect.name
            if dialect == 'postgresql':
                from sqlalchemy.dialects.postgresql import insert
            elif dialect == 'sqlite':
                from sqlalchemy.dialects.sqlite import insert
            else:
                raise RuntimeError('Rate limiter requires PostgreSQL or SQLite')
            expired = AuthThrottle.expires_at <= now
            statement = insert(AuthThrottle).values(key=digest, count=1, expires_at=expires)
            statement = statement.on_conflict_do_update(index_elements=[AuthThrottle.key], set_={
                'count': case((expired, 1), else_=AuthThrottle.count + 1),
                'expires_at': case((expired, expires), else_=AuthThrottle.expires_at),
            }).returning(AuthThrottle.count, AuthThrottle.expires_at)
            count, expires_at = db.execute(statement).one()
            db.commit()
        return count <= max_requests, max(1, math.ceil((expires_at - now).total_seconds())) if count > max_requests else 0

    def clear(self):
        """Test-only reset; production cleanup uses expiration, never a public reset."""
        if settings.ENVIRONMENT != 'development':
            raise RuntimeError('Rate limit reset is development-only')
        with self.session_factory() as db:
            db.execute(delete(AuthThrottle).where(AuthThrottle.key.like('req:%')))
            db.commit()
