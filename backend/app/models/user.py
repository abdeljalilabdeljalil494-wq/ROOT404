from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"u_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=gen_id)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # Optional since OTP auth
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Academic
    level = Column(Float, default=0.0)
    xp = Column(Integer, default=0)
    xp_to_next = Column(Integer, default=1000)
    projects_done = Column(Integer, default=0)
    correction_points = Column(Integer, default=0)
    account_value = Column(Integer, default=0)
    jetons = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)
    reputation = Column(Integer, default=50)
    integrity_score = Column(Integer, default=100)
    
    # Campus & coalition
    campus = Column(String, default="Tunis")
    coalition_id = Column(String, nullable=True)
    
    # Black Hole
    blackhole_days_left = Column(Integer, default=120)
    blackhole_total = Column(Integer, default=120)
    blackhole_warning = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_mentor = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Piscine
    piscine_status = Column(String, default="not_started")  # not_started, in_progress, completed, failed
    piscine_score = Column(Integer, default=0)
    
    # JSON fields for flexibility
    skills = Column(JSON, default=dict)  # Skill graph
    badges = Column(JSON, default=list)
    socials = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    corrections_given = relationship("Correction", foreign_keys="Correction.corrector_id", back_populates="corrector")
    corrections_received = relationship("Correction", foreign_keys="Correction.author_id", back_populates="author")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "fullName": self.full_name,
            "email": self.email,
            "avatar": self.avatar_url or f"https://i.pravatar.cc/160?u={self.username}",
            "level": self.level,
            "xp": self.xp,
            "xpToNext": self.xp_to_next,
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
            "bio": self.bio,
            "socials": self.socials or {},
            "skills": self.skills or {},
            "badges": self.badges or []
        }
