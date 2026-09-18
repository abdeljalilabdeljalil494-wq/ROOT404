from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"s_{uuid.uuid4().hex[:10]}"

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index('idx_submission_user', 'user_id'),
        Index('idx_submission_project', 'project_id'),
        Index('idx_submission_user_project', 'user_id', 'project_id'),
        Index('idx_submission_status', 'status'),
        Index('idx_submission_created', 'created_at'),
        CheckConstraint('score IS NULL OR (score >= 0 AND score <= 100)', name='check_score_range'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    user_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(32), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    files = Column(JSON, default=dict, nullable=False)
    language = Column(String(20), default="c", nullable=False)
    
    status = Column(String(20), default="pending", nullable=False, index=True)
    score = Column(Integer, nullable=True)
    tests = Column(JSON, default=list, nullable=False)
    logs = Column(Text, nullable=True)
    
    ai_review = Column(JSON, nullable=True)
    
    similarity_score = Column(Float, default=0.0, nullable=False)
    integrity_flags = Column(JSON, default=list, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="submissions")
    project = relationship("Project", back_populates="submissions")
    corrections = relationship("Correction", back_populates="submission", cascade="all, delete-orphan", passive_deletes=True)
