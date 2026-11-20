from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import InvalidTokenError as JWTError, ExpiredSignatureError
from passlib.context import CryptContext
import secrets
import string
import hashlib
import hmac
import threading
from .config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# For development: last OTPs with thread safety
class ThreadSafeLastOTP:
    def __init__(self):
        self._store: Dict[str, str] = {}
        self._lock = threading.RLock()
    
    def set(self, email: str, otp: str):
        with self._lock:
            self._store[email.lower()] = otp
    
    def get(self, email: str) -> Optional[str]:
        with self._lock:
            return self._store.get(email.lower())
    
    def clear(self):
        with self._lock:
            self._store.clear()

_last_otps = ThreadSafeLastOTP()

def hash_password(password: str) -> str:
    # Validate password strength
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Add standard claims
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,  # Not before
        "iss": settings.PROJECT_NAME,  # Issuer
        "jti": secrets.token_urlsafe(16),  # JWT ID for revocation tracking
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer=settings.PROJECT_NAME,
            options={
                "require": ["sub", "exp", "iat", "nbf", "iss", "jti"],
                "verify_aud": False,
                "verify_iss": True,
                "verify_exp": True,
                "verify_nbf": True,
            }
        )
        return payload
    except ExpiredSignatureError:
        logger.info("JWT token expired")
        return None
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected JWT error: {e}")
        return None

def generate_otp(length: int = 6) -> str:
    # Use secrets for cryptographically secure random
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def _otp_digest(email: str, code: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), f"{email.lower()}:{code}".encode(), hashlib.sha256).hexdigest()


def store_otp(email: str, otp: str):
    from .database import SessionLocal
    from app.models.auth_state import OTPChallenge
    with SessionLocal() as db:
        db.merge(OTPChallenge(email=email.lower(), digest=_otp_digest(email, otp),
                              expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES), attempts=0))
        db.commit()


def verify_otp(email: str, code: str) -> bool:
    from sqlalchemy import update, delete
    from .database import SessionLocal
    from app.models.auth_state import OTPChallenge
    email = email.lower()
    with SessionLocal() as db:
        # Atomic increment serializes concurrent attempts on PostgreSQL and SQLite.
        claimed = db.execute(update(OTPChallenge).where(
            OTPChallenge.email == email, OTPChallenge.expires_at > datetime.utcnow(),
            OTPChallenge.attempts < settings.OTP_MAX_ATTEMPTS
        ).values(attempts=OTPChallenge.attempts + 1))
        if claimed.rowcount != 1:
            db.rollback()
            return False
        entry = db.get(OTPChallenge, email)
        valid = hmac.compare_digest(entry.digest, _otp_digest(email, code))
        if valid:
            db.execute(delete(OTPChallenge).where(OTPChallenge.email == email))
        db.commit()
        return valid


def can_request_otp(email: str) -> tuple[bool, str]:
    from sqlalchemy import update, delete
    from sqlalchemy.exc import IntegrityError
    from .database import SessionLocal
    from app.models.auth_state import AuthThrottle
    key = hashlib.sha256(email.lower().encode()).hexdigest()
    with SessionLocal() as db:
        db.execute(delete(AuthThrottle).where(AuthThrottle.key == key, AuthThrottle.expires_at <= datetime.utcnow()))
        db.commit()
        try:
            db.add(AuthThrottle(key=key, count=0, expires_at=datetime.utcnow() + timedelta(hours=1)))
            db.commit()
        except IntegrityError:
            db.rollback()
        result = db.execute(update(AuthThrottle).where(AuthThrottle.key == key,
            AuthThrottle.count < settings.OTP_RATE_LIMIT_PER_HOUR).values(count=AuthThrottle.count + 1))
        db.commit()
        return result.rowcount == 1, "Rate limit exceeded for OTP requests"


def generate_and_store_otp(email: str) -> str:
    from app.services.email import send_otp
    can_request, msg = can_request_otp(email)
    if not can_request:
        raise ValueError(msg)
    otp = generate_otp(settings.OTP_LENGTH)
    store_otp(email, otp)
    try:
        send_otp(email, otp)
    except Exception:
        # A code whose delivery failed must not remain usable.
        from .database import SessionLocal
        from app.models.auth_state import OTPChallenge
        with SessionLocal() as db:
            db.query(OTPChallenge).filter_by(email=email.lower(), digest=_otp_digest(email, otp)).delete()
            db.commit()
        raise
    if settings.ENVIRONMENT == "development" and settings.ENABLE_DEV_OTP:
        _last_otps.set(email, otp)
    return otp


def get_last_otp(email: str) -> Optional[str]:
    return _last_otps.get(email) if settings.ENVIRONMENT == "development" and settings.ENABLE_DEV_OTP else None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS"""
    if not isinstance(text, str):
        return ""
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Basic XSS prevention - escape HTML special chars for storage
    # Note: actual escaping should happen at render time, but we do basic sanitization
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        "<script", "</script>", "javascript:", "onerror=", "onload=",
        "eval(", "document.cookie", "document.write"
    ]
    
    lower_text = text.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_text:
            logger.warning(f"Potentially dangerous pattern detected: {pattern}")
            # Don't block, but log - actual prevention via output encoding
    
    return text.strip()

def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format"""
    if not username:
        return False, "Username is required"
    
    if len(username) < settings.MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {settings.MIN_USERNAME_LENGTH} characters"
    
    if len(username) > settings.MAX_USERNAME_LENGTH:
        return False, f"Username must be at most {settings.MAX_USERNAME_LENGTH} characters"
    
    # Alphanumeric + underscore + hyphen, must start with letter
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, underscore, hyphen"
    
    # Reserved usernames
    reserved = ["admin", "root", "system", "api", "www", "mail", "support", "help"]
    if username.lower() in reserved:
        return False, "Username is reserved"
    
    return True, ""

def validate_email_format(email: str) -> tuple[bool, str]:
    """Additional email validation beyond Pydantic"""
    if len(email) > settings.MAX_EMAIL_LENGTH:
        return False, "Email too long"
    
    # Check for common disposable domains in production
    if settings.ENVIRONMENT == "production":
        disposable = ["tempmail.com", "10minutemail.com", "guerrillamail.com"]
        domain = email.split("@")[-1].lower() if "@" in email else ""
        if domain in disposable:
            return False, "Disposable email domains not allowed"
    
    return True, ""

# Cleanup for testing
def _clear_stores():
    if settings.ENVIRONMENT != "development":
        raise RuntimeError("Test reset is only available in development")
    from .database import SessionLocal
    from app.models.auth_state import OTPChallenge, AuthThrottle, RevokedToken
    with SessionLocal() as db:
        for model in (OTPChallenge, AuthThrottle, RevokedToken):
            db.query(model).delete()
        db.commit()
    _last_otps.clear()
