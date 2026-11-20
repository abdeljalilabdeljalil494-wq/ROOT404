from .beta import MissionClaim, ModerationReport
from .oauth import OAuthAttempt, OAuthIdentity
from .notification import Notification
from app.core.database import Base
from .user import User
from .project import Project, UserProjectProgress
from .submission import Submission
from .correction import Correction, CorrectionSlot
from .room import Room, RoomMember, RoomMessage
from .coalition import Coalition, CoalitionMember, CoalitionWar

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index, CheckConstraint
from datetime import datetime
import uuid

def gen_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:10]}"

class DailyMission(Base):
    __tablename__ = "daily_missions"
    __table_args__ = (
        Index('idx_daily_mission_user', 'user_id'),
        Index('idx_daily_mission_status', 'status'),
        CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='check_difficulty_range'),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("dm_"))
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, default=1, nullable=False)
    reward_xp = Column(Integer, default=100, nullable=False)
    skill = Column(String(50), nullable=True)
    status = Column(String(20), default="available", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

class Badge(Base):
    __tablename__ = "badges"
    id = Column(String(32), primary_key=True, default=lambda: gen_id("b_"))
    name = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(50), default="Trophy", nullable=False)
    tier = Column(String(20), default="bronze", nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(JSON, default=dict, nullable=False)

class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (
        Index('idx_user_badge_user', 'user_id'),
        Index('idx_user_badge_badge', 'badge_id'),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("ub_"))
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(String(32), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_created', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("audit_"))
    user_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 max 45
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class ArenaMatch(Base):
    __tablename__ = "arena_matches"
    __table_args__ = (
        Index('idx_arena_status', 'status'),
        Index('idx_arena_mode', 'mode'),
        Index('idx_arena_created', 'created_at'),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("am_"))
    mode = Column(String(20), default="1v1", nullable=False, index=True)
    status = Column(String(20), default="waiting", nullable=False, index=True)
    problem = Column(String(200), nullable=False)
    player_a_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    player_b_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    winner_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    viewers = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class PiscineDay(Base):
    __tablename__ = "piscine_days"
    __table_args__ = (
        Index('idx_piscine_day_number', 'day_number', unique=True),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("pd_"))
    day_number = Column(Integer, nullable=False, unique=True)
    title = Column(String(100), nullable=False)
    topic = Column(String(50), nullable=True)
    exercises = Column(JSON, default=list, nullable=False)
    is_rush = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class UserPiscineProgress(Base):
    __tablename__ = "user_piscine_progress"
    __table_args__ = (
        Index('idx_piscine_progress_user', 'user_id'),
        Index('idx_piscine_progress_day', 'day_id'),
    )
    id = Column(String(32), primary_key=True, default=lambda: gen_id("uppisc_"))
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    day_id = Column(String(32), ForeignKey("piscine_days.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="locked", nullable=False)
    score = Column(Integer, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

__all__ = [
    "User", "Project", "UserProjectProgress", "Submission", "Correction", "CorrectionSlot",
    "Room", "RoomMember", "RoomMessage", "Coalition", "CoalitionMember", "CoalitionWar",
    "DailyMission", "Badge", "UserBadge", "AuditLog", "ArenaMatch", "PiscineDay", "UserPiscineProgress",
    "Base"
]
