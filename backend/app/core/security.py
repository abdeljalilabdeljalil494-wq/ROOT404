from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
import secrets
import string
import hashlib
import hmac
import time
import threading
from collections import defaultdict
from .config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Thread-safe OTP store
class ThreadSafeOTPStore:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._rate_limit: Dict[str, list] = defaultdict(list)  # email -> list of timestamps
        self._rate_lock = threading.RLock()
    
    def _clean_expired(self):
        now = datetime.utcnow()
        expired = [k for k, v in self._store.items() if now > v["expires"]]
        for k in expired:
            del self._store[k]
    
    def _check_rate_limit(self, email: str) -> bool:
        """Check if email is rate limited for OTP requests"""
        key = email.lower()
        now = time.time()
        hour_ago = now - 3600
        
        with self._rate_lock:
            # Clean old entries
            self._rate_limit[key] = [t for t in self._rate_limit[key] if t > hour_ago]
            
            if len(self._rate_limit[key]) >= settings.OTP_RATE_LIMIT_PER_HOUR:
                return False
            
            self._rate_limit[key].append(now)
            return True
    
    def store(self, email: str, otp: str):
        key = email.lower()
        with self._lock:
            self._clean_expired()
            self._store[key] = {
                "otp": hashlib.sha256(otp.encode()).hexdigest(),
                "expires": datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
                "attempts": 0,
                "created_at": datetime.utcnow()
            }
    
    def verify(self, email: str, code: str) -> bool:
        key = email.lower()
        with self._lock:
            self._clean_expired()
            
            if key not in self._store:
                # Constant time to prevent timing attacks
                hashlib.sha256(b"dummy").hexdigest()
                return False
            
            entry = self._store[key]
            
            if datetime.utcnow() > entry["expires"]:
                del self._store[key]
                return False
            
            if entry["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                del self._store[key]
                logger.warning(f"OTP max attempts exceeded for {email}")
                return False
            
            entry["attempts"] += 1
            
            # Constant-time comparison to prevent timing attacks
            hashed_input = hashlib.sha256(code.encode()).hexdigest()
            if hmac.compare_digest(hashed_input, entry["otp"]):
                del self._store[key]
                return True
            
            return False
    
    def can_request_otp(self, email: str) -> tuple[bool, str]:
        if not self._check_rate_limit(email):
            return False, f"Rate limit exceeded. Max {settings.OTP_RATE_LIMIT_PER_HOUR} OTP requests per hour."
        return True, ""
    
    def clear(self):
        with self._lock:
            self._store.clear()
        with self._rate_lock:
            self._rate_limit.clear()

# Global thread-safe store
_otp_store = ThreadSafeOTPStore()

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

def store_otp(email: str, otp: str):
    _otp_store.store(email, otp)

def verify_otp(email: str, code: str) -> bool:
    return _otp_store.verify(email, code)

def can_request_otp(email: str) -> tuple[bool, str]:
    return _otp_store.can_request_otp(email)

def generate_and_store_otp(email: str) -> str:
    can_request, msg = can_request_otp(email)
    if not can_request:
        raise ValueError(msg)
    
    otp = generate_otp(settings.OTP_LENGTH)
    store_otp(email, otp)
    # Only store last OTP in development
    if settings.ENVIRONMENT != "production":
        _last_otps.set(email, otp)
    return otp

def get_last_otp(email: str) -> Optional[str]:
    # Only available in non-production
    if settings.ENVIRONMENT == "production":
        return None
    return _last_otps.get(email)

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
    _otp_store.clear()
    _last_otps.clear()
