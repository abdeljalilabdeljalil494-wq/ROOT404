from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .database import get_db
from .security import decode_token
from app.models.user import User
import logging
from typing import Optional

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

from .rate_limit import RateLimiter

# State is shared in SQL across worker instances, not process-local.
_rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Get client IP with proxy support"""
    # Uvicorn handles forwarded headers only from configured trusted proxy IPs.
    return request.client.host if request.client else "unknown"

def rate_limit(
    request: Request,
    max_requests: int = 100,
    window: int = 60,
    key_prefix: str = "global"
):
    """Rate limiting dependency"""
    client_ip = get_client_ip(request)
    key = f"{key_prefix}:{client_ip}"
    
    try:
        allowed, retry_after = _rate_limiter.is_allowed(key, max_requests, window)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Rate limit storage unavailable")
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "retry_after": retry_after,
                "message": f"Rate limit exceeded. Try again in {retry_after} seconds."
            },
            headers={"Retry-After": str(retry_after)}
        )

def auth_rate_limit(request: Request):
    """Stricter rate limit for auth endpoints"""
    from app.core.config import settings
    return rate_limit(
        request,
        max_requests=settings.RATE_LIMIT_AUTH_REQUESTS,
        window=settings.RATE_LIMIT_AUTH_WINDOW,
        key_prefix="auth"
    )

def judge_rate_limit(request: Request):
    """Rate limit for judge endpoints"""
    from app.core.config import settings
    return rate_limit(
        request,
        max_requests=settings.RATE_LIMIT_JUDGE_REQUESTS,
        window=settings.RATE_LIMIT_JUDGE_WINDOW,
        key_prefix="judge"
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - Bearer token required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate token format
    if not credentials.credentials or not 20 <= len(credentials.credentials) <= 8192:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    from app.models.auth_state import RevokedToken
    if not payload.get("jti") or db.get(RevokedToken, payload["jti"]):
        raise HTTPException(status_code=401, detail="Session revoked")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload - missing sub",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate user_id format to prevent injection
    if not isinstance(user_id, str) or len(user_id) > 100:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if payload.get("sv", 0) != user.session_version:
        raise HTTPException(status_code=401, detail="Session revoked")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email verification required")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account frozen (Black Hole) or deactivated"
        )
    
    return user

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    # An explicitly supplied invalid/revoked token is not anonymous authentication.
    return get_current_user(credentials, db)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        logger.warning(f"Admin access denied for user {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_mentor(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_mentor and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor privileges required"
        )
    return current_user

# For testing - clear rate limiter
def _clear_rate_limiter():
    _rate_limiter.clear()


def require_demo_mode():
    from .config import settings
    if settings.ENVIRONMENT != "development" or not settings.ENABLE_DEMO_FEATURES:
        raise HTTPException(status_code=503, detail="This prototype workflow is not implemented for real use")


def ai_rate_limit(current_user: User = Depends(get_current_user)):
    """Per-account persisted hourly budget shared by ask/review aliases."""
    from .config import settings
    try:
        allowed, retry = _rate_limiter.is_allowed(f"ai-user:{current_user.id}", settings.AI_REQUESTS_PER_HOUR, 3600)
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Rate limit storage unavailable")
    if not allowed:
        raise HTTPException(status_code=429, detail="AI request budget exhausted", headers={"Retry-After": str(retry)})
