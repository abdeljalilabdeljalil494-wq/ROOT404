"""Security primitives: OTP generation/hashing + JWT issue/verify.

The platform authenticates with e-mail OTP + short-lived JWT — no passwords
are ever stored (see README « Auth (OTP), Tokens »).
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import models
from .config import settings
from .db import get_db

bearer_scheme = HTTPBearer(auto_error=False)

TOKEN_INVALID = {"detail": "Token invalide ou expiré"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ----------------------------- OTP ----------------------------------------

def generate_otp() -> str:
    """6-digit numeric code."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(code: str) -> str:
    """OTP codes are stored hashed — a DB leak alone is useless."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


# ----------------------------- JWT ----------------------------------------

def create_token(user_id: str) -> str:
    now = _now()
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": now + timedelta(days=settings.jwt_expires_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


# ----------------------------- FastAPI dependency --------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(get_db),
) -> models.User:
    """Resolve the Bearer token to a User, or answer 401."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentification requise")
    payload = decode_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, **TOKEN_INVALID)
    user = db.get(models.User, payload["sub"])
    if user is None:
        raise HTTPException(status_code=401, **TOKEN_INVALID)
    return user
