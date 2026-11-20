from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"p_{uuid.uuid4().hex[:8]}"

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index('idx_project_slug', 'slug', unique=True),
        Index('idx_project_level_value', 'level_value'),
        Index('idx_project_lang', 'lang'),
        Index('idx_project_requires', 'requires'),
        CheckConstraint('difficulty >= 1 AND difficulty <= 5', name='check_difficulty'),
        CheckConstraint('xp > 0', name='check_xp_positive'),
        CheckConstraint('level_value >= 0 AND level_value <= 21', name='check_level_value'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    level = Column(String(20), default="Niveau 1", nullable=False)
    level_value = Column(Float, default=1.0, nullable=False, index=True)
    lang = Column(String(20), default="C", nullable=False, index=True)
    lang_color = Column(String(20), default="#3B9EFF", nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    difficulty = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=1000, nullable=False)
    duration = Column(String(20), default="1 sem.", nullable=False)
    status_default = Column(String(20), default="available", nullable=False)
    
    requires = Column(String(100), nullable=True, index=True)
    is_bonus = Column(Boolean, default=False, nullable=False)
    is_group = Column(Boolean, default=False, nullable=False)
    max_team = Column(Integer, default=1, nullable=False)
    
    test_cases = Column(JSON, default=list, nullable=False)
    norm_rules = Column(JSON, default=dict, nullable=False)
    
    objectives = Column(JSON, default=list, nullable=False)
    constraints = Column(JSON, default=list, nullable=False)
    resources = Column(JSON, default=list, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    submissions = relationship("Submission", back_populates="project", cascade="all, delete-orphan", passive_deletes=True)

class UserProjectProgress(Base):
    __tablename__ = "user_project_progress"
    __table_args__ = (
        Index('idx_upp_user', 'user_id'),
        Index('idx_upp_project', 'project_id'),
        Index('idx_upp_user_project', 'user_id', 'project_id', unique=True),
        Index('idx_upp_status', 'status'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"upp_{uuid.uuid4().hex[:10]}")
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(32), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String(20), default="locked", nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)
    score = Column(Integer, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, default=0, nullable=False)
    
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
