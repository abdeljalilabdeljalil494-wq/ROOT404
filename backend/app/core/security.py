from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import random
import string
import hashlib
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory OTP store for dev (in prod use Redis)
_otp_store: Dict[str, Dict[str, Any]] = {}

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def store_otp(email: str, otp: str):
    _otp_store[email.lower()] = {
        "otp": hashlib.sha256(otp.encode()).hexdigest(),
        "expires": datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        "attempts": 0
    }

def verify_otp(email: str, code: str) -> bool:
    key = email.lower()
    if key not in _otp_store:
        return False
    entry = _otp_store[key]
    if datetime.utcnow() > entry["expires"]:
        del _otp_store[key]
        return False
    if entry["attempts"] >= 5:
        del _otp_store[key]
        return False
    entry["attempts"] += 1
    hashed = hashlib.sha256(code.encode()).hexdigest()
    if hashed == entry["otp"]:
        del _otp_store[key]
        return True
    return False

def get_otp_for_debug(email: str) -> Optional[str]:
    """
    Only for development: retrieve OTP hash info.
    In real prod, OTP would be sent via email.
    For mock/dev we allow returning the code via API.
    """
    # This is a dev helper - in production remove
    return None

# For development: we keep last generated OTPs in memory to return via API
_last_otps: Dict[str, str] = {}

def generate_and_store_otp(email: str) -> str:
    otp = generate_otp(settings.OTP_LENGTH)
    store_otp(email, otp)
    _last_otps[email.lower()] = otp
    return otp

def get_last_otp(email: str) -> Optional[str]:
    return _last_otps.get(email.lower())
