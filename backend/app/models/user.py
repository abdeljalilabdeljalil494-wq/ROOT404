from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"u_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        Index('idx_user_campus', 'campus'),
        Index('idx_user_level', 'level'),
        Index('idx_user_is_active', 'is_active'),
        Index('idx_user_coalition', 'coalition_id'),
        CheckConstraint('level >= 0 AND level <= 21', name='check_level_range'),
        CheckConstraint('xp >= 0', name='check_xp_positive'),
        CheckConstraint('reputation >= 0 AND reputation <= 100', name='check_reputation_range'),
        CheckConstraint('integrity_score >= 0 AND integrity_score <= 100', name='check_integrity_range'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    username = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    display_name = Column(String(50), nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Academic with constraints
    level = Column(Float, default=0.0, nullable=False, index=True)
    xp = Column(Integer, default=0, nullable=False)
    xp_to_next = Column(Integer, default=1000, nullable=False)
    projects_done = Column(Integer, default=0, nullable=False)
    correction_points = Column(Integer, default=0, nullable=False)
    account_value = Column(Integer, default=0, nullable=False)
    jetons = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    accuracy = Column(Integer, default=0, nullable=False)
    reputation = Column(Integer, default=50, nullable=False)
    integrity_score = Column(Integer, default=100, nullable=False)
    
    # Campus & coalition
    campus = Column(String(20), default="Tunis", nullable=False, index=True)
    coalition_id = Column(String(32), nullable=True, index=True)
    
    # Black Hole
    blackhole_days_left = Column(Integer, default=120, nullable=False)
    blackhole_total = Column(Integer, default=120, nullable=False)
    blackhole_warning = Column(Boolean, default=False, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Private by default; public directories require explicit opt-in.
    public_profile = Column(Boolean, default=False, nullable=False, server_default="0")
    directory_visible = Column(Boolean, default=False, nullable=False, server_default="0")
    session_version = Column(Integer, default=0, nullable=False, server_default="0")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_mentor = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Piscine
    piscine_status = Column(String(20), default="not_started", nullable=False)
    piscine_score = Column(Integer, default=0, nullable=False)
    
    # JSON fields
    skills = Column(JSON, default=dict, nullable=False)
    badges = Column(JSON, default=list, nullable=False)
    socials = Column(JSON, default=dict, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships with proper cascading
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    corrections_given = relationship("Correction", foreign_keys="Correction.corrector_id", back_populates="corrector", cascade="all, delete-orphan", passive_deletes=True)
    corrections_received = relationship("Correction", foreign_keys="Correction.author_id", back_populates="author", cascade="all, delete-orphan", passive_deletes=True)

    def to_dict(self):
        from app.services.gamification import calculate_level_progress, xp_to_level, LEVEL_THRESHOLDS
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "fullName": self.full_name,
            "email": self.email,
            "avatar": self.avatar_url,
            "level": self.level,
            "levelProgress": calculate_level_progress(self.xp),
            "xp": self.xp,
            "xpToNext": max(0, LEVEL_THRESHOLDS[min(21, int(xp_to_level(self.xp)) + 1)] - self.xp),
            "projectsDone": self.projects_done,
            "correctionPoints": self.correction_points,
            "accountValue": self.account_value,
            "jetons": self.jetons,
            "streak": self.streak,
            "accuracy": self.accuracy,
            "reputation": self.reputation,
            "integrity": self.integrity_score,
            "campus": self.campus,
            "coalition": self.coalition_id,
            "blackHole": {"daysLeft": self.blackhole_days_left, "total": self.blackhole_total},
            "isMentor": self.is_mentor,
            "isAdmin": self.is_admin,
            "joined": self.created_at.strftime("%b. %Y") if self.created_at else "",
            "bio": self.bio[:1000] if self.bio else None,  # Truncate for safety
            "socials": self.socials or {},
            "skills": self.skills or {},
            "badges": self.badges or []
        }
