"""Security primitives: bcrypt password hashing + signed JWT access tokens.

Hashing notes:
    * bcrypt with 12 rounds; the 72-byte input limit is enforced explicitly so
      long passphrases fail loudly instead of being silently truncated.
Token notes:
    * HS256 signed with ``Settings.SECRET_KEY``; short expiry enforced by the
      ``exp`` claim; production requires a strong secret (see config.py).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings

#: HMAC-SHA256 — the secret comes from Settings.SECRET_KEY.
ALGORITHM = "HS256"

#: bcrypt operates on at most 72 bytes; anything longer is rejected (never
#: silently truncated) at both registration and hashing time.
MAX_PASSWORD_BYTES = 72

#: Cost factor for bcrypt. 12 is the current mainstream balance (~250ms).
BCRYPT_ROUNDS = 12


# ── Password hashing ─────────────────────────────────────────────────────────

def validate_password_bytes(password: str) -> None:
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password must be at most {MAX_PASSWORD_BYTES} bytes (UTF-8)."
        )


def hash_password(password: str) -> str:
    validate_password_bytes(password)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time verification; returns False on any malformed hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ── JWT access tokens ────────────────────────────────────────────────────────

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
