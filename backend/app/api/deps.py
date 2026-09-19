"""Shared FastAPI dependencies: DB session + current-user resolution."""
from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User

#: Optional bearer: missing header is handled by us (401 with clean message).
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user; 401 for missing/invalid/expired tokens."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise unauthorized from None
    subject = payload.get("sub")
    if subject is None or not str(subject).isdigit():
        raise unauthorized

    user = db.get(User, int(subject))
    if user is None or not user.is_active:
        raise unauthorized
    return user
