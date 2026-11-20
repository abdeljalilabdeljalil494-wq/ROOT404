from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"r_{uuid.uuid4().hex[:8]}"

class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        Index('idx_room_type', 'type'),
        Index('idx_room_host', 'host_id'),
        Index('idx_room_created', 'created_at'),
        CheckConstraint('capacity > 0 AND capacity <= 1000', name='check_capacity'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="study", nullable=False, index=True)
    project = Column(String(100), nullable=True)
    host_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    capacity = Column(Integer, default=10, nullable=False)
    is_live = Column(Boolean, default=False, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    
    tags = Column(JSON, default=list, nullable=False)
    settings = Column(JSON, default=dict, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    members = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan", passive_deletes=True)
    messages = relationship("RoomMessage", back_populates="room", cascade="all, delete-orphan", passive_deletes=True)

class RoomMember(Base):
    __tablename__ = "room_members"
    __table_args__ = (
        Index('idx_room_member_room', 'room_id'),
        Index('idx_room_member_user', 'user_id'),
        Index('idx_room_member_unique', 'room_id', 'user_id', unique=True),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"rm_{uuid.uuid4().hex[:10]}")
    room_id = Column(String(32), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default="member", nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    room = relationship("Room", back_populates="members")

class RoomMessage(Base):
    __tablename__ = "room_messages"
    __table_args__ = (
        Index('idx_message_room', 'room_id'),
        Index('idx_message_user', 'user_id'),
        Index('idx_message_created', 'created_at'),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"msg_{uuid.uuid4().hex[:10]}")
    room_id = Column(String(32), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    removed_at = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)
    type = Column(String(20), default="text", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    room = relationship("Room", back_populates="messages")
