from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.correction import Correction, CorrectionSlot
from app.models.submission import Submission
from app.models.project import Project
from app.services.correction import CorrectionService
from datetime import datetime, timedelta

router = APIRouter(prefix="/peer-review", tags=["Peer Review"])

class ScheduleRequest(BaseModel):
    submission_id: str
    preferred_time: Optional[datetime] = None

class ReviewRequest(BaseModel):
    score: int
    comment: Optional[str] = None
    checklist: Optional[List[dict]] = None
    author_rating: Optional[int] = None

class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    project_id: Optional[str] = None

@router.get("/")
def list_corrections(
    role: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if role == "corrector" or role == "all":
        as_corrector = db.query(Correction).filter(Correction.corrector_id == current_user.id).all()
    else:
        as_corrector = []
    
    if role == "author" or role == "all":
        as_author = db.query(Correction).filter(Correction.author_id == current_user.id).all()
    else:
        as_author = []
    
    def format_correction(c):
        submission = db.query(Submission).filter(Submission.id == c.submission_id).first()
        project = db.query(Project).filter(Project.id == submission.project_id).first() if submission else None
        author = db.query(User).filter(User.id == c.author_id).first()
        corrector = db.query(User).filter(User.id == c.corrector_id).first() if c.corrector_id else None
        
        return {
            "id": c.id,
            "project": project.slug if project else "unknown",
            "project_name": project.name if project else "unknown",
            "author": author.username if author else "unknown",
            "corrector": corrector.username if corrector else "searching...",
            "status": c.status,
            "score": c.score,
            "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "checklist": c.checklist,
            "role": "corrector" if c.corrector_id == current_user.id else "author"
        }
    
    return {
        "as_corrector": [format_correction(c) for c in as_corrector],
        "as_author": [format_correction(c) for c in as_author],
        "pending": len([c for c in as_corrector if c.status in ["pending", "scheduled"]]),
        "total": len(as_corrector) + len(as_author)
    }

@router.post("/request")
def request_correction(payload: ScheduleRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == payload.submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    correction = CorrectionService.create_correction_request(payload.submission_id, current_user.id, db)
    return {
        "id": correction.id,
        "status": correction.status,
        "corrector": correction.corrector_id,
        "checklist": correction.checklist,
        "message": "Demande de correction créée, recherche d'un correcteur..."
    }

@router.get("/{correction_id}")
def get_correction(correction_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    correction = db.query(Correction).filter(Correction.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="Correction non trouvée")
    if correction.author_id != current_user.id and correction.corrector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    submission = db.query(Submission).filter(Submission.id == correction.submission_id).first()
    project = db.query(Project).filter(Project.id == submission.project_id).first() if submission else None
    
    return {
        "id": correction.id,
        "submission_id": correction.submission_id,
        "project": project.slug if project else None,
        "status": correction.status,
        "score": correction.score,
        "checklist": correction.checklist,
        "comment": correction.comment,
        "scheduled_at": correction.scheduled_at.isoformat() if correction.scheduled_at else None,
        "files": submission.files if submission else {},
        "tests": submission.tests if submission else []
    }

@router.post("/{correction_id}/review")
def submit_review(correction_id: str, payload: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    correction = db.query(Correction).filter(Correction.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="Correction non trouvée")
    if correction.corrector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le correcteur peut noter")
    
    correction.score = payload.score
    correction.comment = payload.comment
    if payload.checklist:
        correction.checklist = payload.checklist
    correction.status = "completed"
    
    # Award correction points
    corrector = db.query(User).filter(User.id == current_user.id).first()
    if corrector:
        points = CorrectionService.calculate_correction_points(correction)
        corrector.correction_points += points
    
    # Update submission if score high enough, mark as validated
    submission = db.query(Submission).filter(Submission.id == correction.submission_id).first()
    
    db.commit()
    
    return {
        "ok": True,
        "score": payload.score,
        "correction_points_earned": CorrectionService.calculate_correction_points(correction)
    }

@router.post("/slots")
def create_slot(payload: SlotCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slot = CorrectionSlot(
        corrector_id=current_user.id,
        project_id=payload.project_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_booked=False
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return {"id": slot.id, "start": slot.start_time.isoformat(), "end": slot.end_time.isoformat()}

@router.get("/slots/available")
def available_slots(project_id: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(CorrectionSlot).filter(
        CorrectionSlot.is_booked == False,
        CorrectionSlot.start_time >= datetime.utcnow()
    )
    if project_id:
        query = query.filter(CorrectionSlot.project_id == project_id)
    
    slots = query.order_by(CorrectionSlot.start_time.asc()).limit(20).all()
    
    result = []
    for s in slots:
        corrector = db.query(User).filter(User.id == s.corrector_id).first()
        result.append({
            "id": s.id,
            "corrector": corrector.username if corrector else "unknown",
            "corrector_level": corrector.level if corrector else 0,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
            "project_id": s.project_id
        })
    
    return result

@router.post("/slots/{slot_id}/book")
def book_slot(slot_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slot = db.query(CorrectionSlot).filter(CorrectionSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot non trouvé")
    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Slot déjà réservé")
    
    slot.is_booked = True
    slot.booked_by = current_user.id
    
    # Create correction linked to slot
    # Find latest submission for project
    if slot.project_id:
        submission = db.query(Submission).filter(
            Submission.user_id == current_user.id,
            Submission.project_id == slot.project_id
        ).order_by(Submission.created_at.desc()).first()
        
        if submission:
            correction = Correction(
                submission_id=submission.id,
                author_id=current_user.id,
                corrector_id=slot.corrector_id,
                status="scheduled",
                scheduled_at=slot.start_time,
                checklist=CorrectionService.get_checklist_for_project(slot.project_id, db)
            )
            db.add(correction)
    
    db.commit()
    return {"ok": True, "slot_id": slot_id}
