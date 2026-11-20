from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Index, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def gen_id():
    return f"c_{uuid.uuid4().hex[:10]}"

class Correction(Base):
    __tablename__ = "corrections"
    __table_args__ = (
        Index('idx_correction_submission', 'submission_id'),
        Index('idx_correction_author', 'author_id'),
        Index('idx_correction_corrector', 'corrector_id'),
        Index('idx_correction_status', 'status'),
        CheckConstraint('score IS NULL OR (score >= 0 AND score <= 100)', name='check_correction_score'),
    )
    
    id = Column(String(32), primary_key=True, default=gen_id)
    submission_id = Column(String(32), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    corrector_id = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    status = Column(String(20), default="pending", nullable=False, index=True)
    score = Column(Integer, nullable=True)
    checklist = Column(JSON, default=list, nullable=False)
    comment = Column(Text, nullable=True)
    
    scheduled_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=30, nullable=False)
    room_id = Column(String(32), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    
    author_rating = Column(Integer, nullable=True)
    corrector_rating = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    submission = relationship("Submission", back_populates="corrections")
    author = relationship("User", foreign_keys=[author_id], back_populates="corrections_received")
    corrector = relationship("User", foreign_keys=[corrector_id], back_populates="corrections_given")

class CorrectionSlot(Base):
    __tablename__ = "correction_slots"
    __table_args__ = (
        Index('idx_slot_corrector', 'corrector_id'),
        Index('idx_slot_project', 'project_id'),
        Index('idx_slot_start', 'start_time'),
        Index('idx_slot_booked', 'is_booked'),
    )
    
    id = Column(String(32), primary_key=True, default=lambda: f"cs_{uuid.uuid4().hex[:10]}")
    corrector_id = Column(String(32), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(32), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False, index=True)
    booked_by = Column(String(32), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
