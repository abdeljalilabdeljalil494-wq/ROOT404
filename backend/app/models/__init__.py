from app.core.database import Base
from .user import User
from .project import Project, UserProjectProgress
from .submission import Submission
from .correction import Correction, CorrectionSlot
from .room import Room, RoomMember, RoomMessage
from .coalition import Coalition, CoalitionMember, CoalitionWar

# Additional models defined inline for simplicity

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from datetime import datetime
import uuid

def gen_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:10]}"

class DailyMission(Base):
    __tablename__ = "daily_missions"
    id = Column(String, primary_key=True, default=lambda: gen_id("dm_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, default=1)
    reward_xp = Column(Integer, default=100)
    skill = Column(String, nullable=True)
    status = Column(String, default="available")  # available, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class Badge(Base):
    __tablename__ = "badges"
    id = Column(String, primary_key=True, default=lambda: gen_id("b_"))
    name = Column(String, unique=True, nullable=False)
    icon = Column(String, default="Trophy")
    tier = Column(String, default="bronze")  # bronze, silver, gold, legendary
    description = Column(Text, nullable=True)
    criteria = Column(JSON, default=dict)

class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(String, primary_key=True, default=lambda: gen_id("ub_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(String, ForeignKey("badges.id"), nullable=False, index=True)
    earned_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: gen_id("audit_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ArenaMatch(Base):
    __tablename__ = "arena_matches"
    id = Column(String, primary_key=True, default=lambda: gen_id("am_"))
    mode = Column(String, default="1v1")
    status = Column(String, default="waiting")  # waiting, live, finished
    problem = Column(String, nullable=False)
    player_a_id = Column(String, ForeignKey("users.id"), nullable=True)
    player_b_id = Column(String, ForeignKey("users.id"), nullable=True)
    winner_id = Column(String, ForeignKey("users.id"), nullable=True)
    viewers = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PiscineDay(Base):
    __tablename__ = "piscine_days"
    id = Column(String, primary_key=True, default=lambda: gen_id("pd_"))
    day_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    exercises = Column(JSON, default=list)
    is_rush = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPiscineProgress(Base):
    __tablename__ = "user_piscine_progress"
    id = Column(String, primary_key=True, default=lambda: gen_id("uppisc_"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    day_id = Column(String, ForeignKey("piscine_days.id"), nullable=False)
    status = Column(String, default="locked")  # locked, available, in_progress, done
    score = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

__all__ = [
    "User", "Project", "UserProjectProgress", "Submission", "Correction", "CorrectionSlot",
    "Room", "RoomMember", "RoomMessage", "Coalition", "CoalitionMember", "CoalitionWar",
    "DailyMission", "Badge", "UserBadge", "AuditLog", "ArenaMatch", "PiscineDay", "UserPiscineProgress",
    "Base"
]
