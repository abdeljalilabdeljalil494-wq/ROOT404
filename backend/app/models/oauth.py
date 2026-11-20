from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Integer
from app.core.database import Base
from datetime import datetime
import uuid


class OAuthIdentity(Base):
    __tablename__='oauth_identities'
    __table_args__=(UniqueConstraint('provider','subject'),UniqueConstraint('user_id','provider'))
    id=Column(String(32),primary_key=True,default=lambda:uuid.uuid4().hex)
    user_id=Column(String(32),ForeignKey('users.id',ondelete='CASCADE'),nullable=False,index=True)
    provider=Column(String(16),nullable=False)
    subject=Column(String(255),nullable=False)
    created_at=Column(DateTime,nullable=False,default=datetime.utcnow)


class OAuthAttempt(Base):
    __tablename__='oauth_attempts'
    state_hash=Column(String(64),primary_key=True)
    browser_hash=Column(String(64),nullable=False)
    provider=Column(String(16),nullable=False)
    verifier=Column(String(128),nullable=False)
    nonce=Column(String(128),nullable=False)
    user_id=Column(String(32),ForeignKey('users.id',ondelete='CASCADE'),nullable=True)
    session_version=Column(Integer,nullable=True)
    expires_at=Column(DateTime,nullable=False,index=True)
