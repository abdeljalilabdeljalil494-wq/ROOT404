from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"coal_{uuid.uuid4().hex[:6]}"

class Coalition(Base):
    __tablename__ = "coalitions"
    __table_args__ = (
        Index('idx_coalition_name', 'name', unique=True),
        Index('idx_coalition_points', 'points'),
        CheckConstraint('points >= 0', name='check_points_positive'),
        CheckConstraint('members_count >= 0', name='check_members_positive'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(20), default="#F8851F", nullable=False)
    motto = Column(String(200), nullable=True)
    points = Column(Integer, default=0, nullable=False, index=True)
    wins = Column(Integer, default=0, nullable=False)
    members_count = Column(Integer, default=0, nullable=False)
    trend = Column(String(20), default="+0", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CoalitionMember(Base):
    __tablename__ = "coalition_members"
    __table_args__ = (
        Index('idx_coalition_member_coalition', 'coalition_id'),
        Index('idx_coalition_member_user', 'user_id'),
        Index('idx_coalition_member_unique', 'coalition_id', 'user_id', unique=True),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"cm_{uuid.uuid4().hex[:10]}")
    coalition_id = Column(String(32), ForeignKey("coalitions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default="member", nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CoalitionWar(Base):
    __tablename__ = "coalition_wars"
    __table_args__ = (
        Index('idx_war_status', 'status'),
        Index('idx_war_dates', 'start_at', 'end_at'),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"war_{uuid.uuid4().hex[:8]}")
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="upcoming", nullable=False, index=True)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    points = Column(JSON, default=dict, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
