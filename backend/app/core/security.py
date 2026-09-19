"""JWT helpers for the authentication layer.

Kept intentionally small: token creation/validation only. Password hashing and
user management land with the Auth milestone (README Phase 1).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import get_settings

#: HMAC-SHA256 — the secret comes from Settings.SECRET_KEY.
ALGORITHM = "HS256"


def create_access_token(
    subject: Any,
    *,
    expires_minutes: int | None = None,
) -> str:
    """Create a signed, short-lived access token for ``subject``."""
    settings = get_settings()
    minutes = (
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
        if expires_minutes is None
        else expires_minutes
    )
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate signature and expiry; raises ``jwt.PyJWTError`` on failure."""
    settings = get_settings()
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
