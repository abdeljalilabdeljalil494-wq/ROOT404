"""Durable daily reward claims and private moderation reports."""
from datetime import datetime
import uuid
from sqlalchemy import Column,String,DateTime,ForeignKey,UniqueConstraint,Integer
from app.core.database import Base


class MissionClaim(Base):
    __tablename__='mission_claims'
    __table_args__=(UniqueConstraint('user_id','day'),)
    id=Column(String(32),primary_key=True,default=lambda:uuid.uuid4().hex)
    user_id=Column(String(32),ForeignKey('users.id',ondelete='CASCADE'),nullable=False,index=True)
    day=Column(String(10),nullable=False)
    submission_id=Column(String(32),ForeignKey('submissions.id',ondelete='SET NULL'))
    xp=Column(Integer,nullable=False,default=25)
    created_at=Column(DateTime,nullable=False,default=datetime.utcnow)


class ModerationReport(Base):
    __tablename__='moderation_reports'
    __table_args__=(UniqueConstraint('user_id','message_id'),)
    id=Column(String(32),primary_key=True,default=lambda:uuid.uuid4().hex)
    user_id=Column(String(32),ForeignKey('users.id',ondelete='CASCADE'),nullable=False,index=True)
    message_id=Column(String(32),ForeignKey('room_messages.id',ondelete='CASCADE'),nullable=False)
    reason=Column(String(1000),nullable=False)
    status=Column(String(16),nullable=False,default='open',index=True)
    reviewer_id=Column(String(32),ForeignKey('users.id',ondelete='SET NULL'))
    created_at=Column(DateTime,nullable=False,default=datetime.utcnow)
    resolved_at=Column(DateTime)
