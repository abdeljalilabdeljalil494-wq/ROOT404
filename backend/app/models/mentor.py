"""Persist successful provider interactions; raw submitted code is not stored here."""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Index
from app.core.database import Base


class MentorInteraction(Base):
    __tablename__ = 'mentor_interactions'
    __table_args__ = (Index('ix_mentor_user_created', 'user_id', 'created_at'),)
    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(String(32), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    kind = Column(String(16), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
