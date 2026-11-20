"""Shared authentication state; no OTP plaintext is persisted."""
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class OTPChallenge(Base):
    __tablename__ = "otp_challenges"
    email = Column(String(254), primary_key=True)
    digest = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)


class AuthThrottle(Base):
    __tablename__ = "auth_throttles"
    key = Column(String(64), primary_key=True)
    count = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    jti = Column(String(64), primary_key=True)
    expires_at = Column(DateTime, nullable=False, index=True)
