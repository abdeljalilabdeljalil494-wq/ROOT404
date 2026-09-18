from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"coal_{uuid.uuid4().hex[:6]}"

class Coalition(Base):
    __tablename__ = "coalitions"
    
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, default="#F8851F")
    motto = Column(String, nullable=True)
    points = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    members_count = Column(Integer, default=0)
    trend = Column(String, default="+0")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CoalitionMember(Base):
    __tablename__ = "coalition_members"
    
    id = Column(String, primary_key=True, default=lambda: f"cm_{uuid.uuid4().hex[:10]}")
    coalition_id = Column(String, ForeignKey("coalitions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

class CoalitionWar(Base):
    __tablename__ = "coalition_wars"
    
    id = Column(String, primary_key=True, default=lambda: f"war_{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="upcoming")  # upcoming, active, finished
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    points = Column(JSON, default=dict)  # {coalition_id: points}
    
    created_at = Column(DateTime, default=datetime.utcnow)
