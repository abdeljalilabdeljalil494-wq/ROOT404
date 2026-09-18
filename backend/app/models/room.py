from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"r_{uuid.uuid4().hex[:8]}"

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    type = Column(String, default="study")  # study, correction, pair, competition, mentor, live
    project = Column(String, nullable=True)
    host_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    capacity = Column(Integer, default=10)
    is_live = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    
    tags = Column(JSON, default=list)
    settings = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    members = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("RoomMessage", back_populates="room", cascade="all, delete-orphan")

class RoomMember(Base):
    __tablename__ = "room_members"
    
    id = Column(String, primary_key=True, default=lambda: f"rm_{uuid.uuid4().hex[:10]}")
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, default="member")  # host, member, observer
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="members")

class RoomMessage(Base):
    __tablename__ = "room_messages"
    
    id = Column(String, primary_key=True, default=lambda: f"msg_{uuid.uuid4().hex[:10]}")
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    type = Column(String, default="text")  # text, code, system, file
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    room = relationship("Room", back_populates="messages")
