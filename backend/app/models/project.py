from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"p_{uuid.uuid4().hex[:8]}"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=gen_id)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    level = Column(String, default="Niveau 1")
    level_value = Column(Float, default=1.0)
    lang = Column(String, default="C")
    lang_color = Column(String, default="#3B9EFF")
    tags = Column(JSON, default=list)
    difficulty = Column(Integer, default=1)  # 1-5
    xp = Column(Integer, default=1000)
    duration = Column(String, default="1 sem.")
    status_default = Column(String, default="available")  # for template
    
    # Lifecycle
    requires = Column(String, nullable=True)  # slug of required project
    is_bonus = Column(Boolean, default=False)
    is_group = Column(Boolean, default=False)
    max_team = Column(Integer, default=1)
    
    # Moulinette config
    test_cases = Column(JSON, default=list)
    norm_rules = Column(JSON, default=dict)
    
    # Content
    objectives = Column(JSON, default=list)
    constraints = Column(JSON, default=list)
    resources = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    submissions = relationship("Submission", back_populates="project")

class UserProjectProgress(Base):
    __tablename__ = "user_project_progress"
    
    id = Column(String, primary_key=True, default=lambda: f"upp_{uuid.uuid4().hex[:10]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    status = Column(String, default="locked")  # locked, available, progress, submitted, moulinette, peer_review, passed, failed
    progress = Column(Integer, default=0)
    score = Column(Integer, nullable=True)
    attempts = Column(Integer, default=0)
    best_score = Column(Integer, default=0)
    
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
