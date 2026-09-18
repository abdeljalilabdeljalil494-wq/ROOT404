from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"s_{uuid.uuid4().hex[:10]}"

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Code
    files = Column(JSON, default=dict)  # {filename: content}
    language = Column(String, default="c")
    
    # Moulinette results
    status = Column(String, default="pending")  # pending, running, success, failed
    score = Column(Integer, nullable=True)
    tests = Column(JSON, default=list)  # [{name, status, detail}]
    logs = Column(Text, nullable=True)
    
    # AI review
    ai_review = Column(JSON, nullable=True)
    
    # Integrity
    similarity_score = Column(Float, default=0.0)
    integrity_flags = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    project = relationship("Project", back_populates="submissions")
    corrections = relationship("Correction", back_populates="submission", cascade="all, delete-orphan")
