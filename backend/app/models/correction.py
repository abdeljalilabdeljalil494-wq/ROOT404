from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"c_{uuid.uuid4().hex[:10]}"

class Correction(Base):
    __tablename__ = "corrections"
    
    id = Column(String, primary_key=True, default=gen_id)
    submission_id = Column(String, ForeignKey("submissions.id"), nullable=False, index=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # student being corrected
    corrector_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # reviewer
    
    status = Column(String, default="pending")  # pending, scheduled, in_progress, completed, validated
    score = Column(Integer, nullable=True)
    checklist = Column(JSON, default=list)  # [{item, checked, comment}]
    comment = Column(Text, nullable=True)
    
    # Slot
    scheduled_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=30)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=True)
    
    # Reputation
    author_rating = Column(Integer, nullable=True)  # rating of correction quality by author
    corrector_rating = Column(Integer, nullable=True)  # rating of student seriousness
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    submission = relationship("Submission", back_populates="corrections")
    author = relationship("User", foreign_keys=[author_id], back_populates="corrections_received")
    corrector = relationship("User", foreign_keys=[corrector_id], back_populates="corrections_given")

class CorrectionSlot(Base):
    __tablename__ = "correction_slots"
    
    id = Column(String, primary_key=True, default=lambda: f"cs_{uuid.uuid4().hex[:10]}")
    corrector_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False)
    booked_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
