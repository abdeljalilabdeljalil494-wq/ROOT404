"""Authentication endpoints: register, login, and session introspection.

* Passwords are bcrypt-hashed; never logged, never returned.
* Login failures are generic ("Incorrect email or password") to prevent
  account enumeration.
* Rate limiting for these endpoints is applied by RateLimitMiddleware.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import LoginRequest, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    email = payload.email.lower()
    existing = db.scalar(
        select(User).where((User.email == email) | (User.username == payload.username))
    )
    if existing is not None:
        field = "email" if existing.email == email else "username"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with this {field} already exists.",
        )

    user = User(
        email=email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # race with a concurrent registration
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email or username already exists.",
        ) from None
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    email = payload.email.lower()
    user = db.scalar(select(User).where(User.email == email))
    #: Same generic error + similar work factor whether or not the user exists
    #: (verify against a dummy hash when missing) to prevent enumeration.
    if user is None:
        verify_password(payload.password, hash_password("timing-equalizer"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This account is disabled."
        )
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user (requires a valid Bearer token)."""
    return current_user


@router.get("/check-email")
def check_email(
    email: str = Query(..., max_length=255),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    """Lightweight availability probe used by the registration form."""
    exists = db.scalar(select(User).where(User.email == email.lower())) is not None
    return {"available": not exists}
