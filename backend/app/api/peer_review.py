from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user, rate_limit
from app.models.user import User
from app.models.correction import Correction, CorrectionSlot
from app.models.submission import Submission
from app.models.project import Project
from app.services.correction import CorrectionService
from datetime import datetime, timedelta, timezone
from sqlalchemy import update

router = APIRouter(prefix="/peer-review", tags=["Peer Review"])

def review_rate_limit(request: Request, user: User = Depends(get_current_user)):
    return rate_limit(request, max_requests=30, window=60, key_prefix='review:' + user.id)


class ScheduleRequest(BaseModel):
    submission_id: str
    preferred_time: Optional[datetime] = None

class ReviewRequest(BaseModel):
    score: int = Field(ge=0, le=100)
    comment: Optional[str] = Field(None, max_length=5000)
    checklist: Optional[List[dict]] = Field(None, max_length=100)
    author_rating: Optional[int] = Field(None, ge=1, le=5)

class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    project_id: Optional[str] = Field(None, max_length=32)

    @model_validator(mode='after')
    def valid_interval(self):
        for name in ('start_time','end_time'):
            value=getattr(self,name)
            if value.tzinfo: setattr(self,name,value.astimezone(timezone.utc).replace(tzinfo=None))
        if self.start_time <= datetime.utcnow() or not timedelta(minutes=5) <= self.end_time-self.start_time <= timedelta(hours=2):
            raise ValueError('Future slots must last5minutes to2hours')
        return self

@router.get("/")
def list_corrections(
    role: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # One joined SELECT per role, independent of correction count.
    query = db.query(Correction).options(
        joinedload(Correction.submission).joinedload(Submission.project),
        joinedload(Correction.author), joinedload(Correction.corrector),
    )
    if role == "corrector" or role == "all":
        as_corrector = query.filter(Correction.corrector_id == current_user.id).all()
    else:
        as_corrector = []
    
    if role == "author" or role == "all":
        as_author = query.filter(Correction.author_id == current_user.id).all()
    else:
        as_author = []
    
    def format_correction(c):
        submission = c.submission
        project = submission.project if submission else None
        author = c.author
        corrector = c.corrector
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

@router.post("/request", dependencies=[Depends(review_rate_limit)])
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

@router.post("/{correction_id}/review", dependencies=[Depends(review_rate_limit)])
def submit_review(correction_id: str, payload: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    correction = db.query(Correction).filter(Correction.id == correction_id).with_for_update().first()
    if not correction:
        raise HTTPException(status_code=404, detail="Correction non trouvée")
    if correction.corrector_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le correcteur peut noter")
    
    if correction.status == "completed":
        raise HTTPException(status_code=409, detail="Review already completed")
    changed = db.execute(update(Correction).where(Correction.id == correction_id,
        Correction.corrector_id == current_user.id, Correction.status != 'completed').values(
            score=payload.score, comment=payload.comment,
            checklist=payload.checklist if payload.checklist is not None else correction.checklist,
            status='completed'))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Review already completed')
    db.refresh(correction)
    points = CorrectionService.calculate_correction_points(correction)
    db.execute(update(User).where(User.id == current_user.id).values(
        correction_points=User.correction_points + points))
    from app.models.notification import Notification
    db.add(Notification(user_id=correction.author_id, kind='review_completed',
        text='Votre correction est terminée : ' + str(payload.score) + '/100.', path='/peer-review'))
    # Human feedback does not automatically validate code or award project XP.
    db.commit()

    return {
        "ok": True,
        "score": payload.score,
        "correction_points_earned": CorrectionService.calculate_correction_points(correction)
    }

@router.post("/slots", dependencies=[Depends(review_rate_limit)])
def create_slot(payload: SlotCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.project_id and not db.get(Project,payload.project_id):
        raise HTTPException(404,'Project not found')
    # Acquires a per-owner write lock on PostgreSQL AND SQLite before checking
    # overlap; a query/FOR UPDATE alone does not serialize SQLite writers.
    db.execute(update(User).where(User.id == current_user.id).values(correction_points=User.correction_points))
    overlap=db.query(CorrectionSlot).filter(CorrectionSlot.corrector_id==current_user.id,
        CorrectionSlot.start_time<payload.end_time,CorrectionSlot.end_time>payload.start_time).first()
    if overlap: raise HTTPException(409,'Overlapping slot')
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

@router.post("/slots/{slot_id}/book", dependencies=[Depends(review_rate_limit)])
def book_slot(slot_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slot = db.query(CorrectionSlot).filter(CorrectionSlot.id == slot_id).with_for_update().first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot non trouvé")
    if slot.corrector_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot book your own review slot")
    if slot.start_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Slot has expired")
    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Slot déjà réservé")
    
    if not slot.project_id:
        raise HTTPException(409,'Slot must specify a project before booking')
    submission=db.query(Submission).filter(Submission.user_id==current_user.id,
        Submission.project_id==slot.project_id).order_by(Submission.created_at.desc()).first()
    if not submission:
        raise HTTPException(409,'Submit this project before booking a review')
    # Atomic compare-and-swap also protects SQLite (FOR UPDATE alone does not).
    claimed=db.execute(update(CorrectionSlot).where(CorrectionSlot.id==slot_id,
        CorrectionSlot.is_booked==False).values(is_booked=True,booked_by=current_user.id))
    if claimed.rowcount!=1:
        db.rollback()
        raise HTTPException(409,'Slot already booked')
    correction=Correction(submission_id=submission.id,author_id=current_user.id,
        corrector_id=slot.corrector_id,status='scheduled',scheduled_at=slot.start_time,
        checklist=CorrectionService.get_checklist_for_project(slot.project_id,db))
    db.add(correction)
    from app.models.notification import Notification
    # Same transaction as the slot claim: rollback must not leave ghost alerts.
    for owner in (current_user.id, slot.corrector_id):
        db.add(Notification(user_id=owner, kind='review_scheduled',
            text='Une correction a été réservée pour le ' + slot.start_time.isoformat() + ' UTC.',
            path='/peer-review'))
    db.commit()
    return {'ok':True,'slot_id':slot_id,'correction_id':correction.id}
