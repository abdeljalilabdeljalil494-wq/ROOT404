from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/mentorship", tags=["Mentorship"])

class MentorRequest(BaseModel):
    topic: str
    message: str
    preferred_time: Optional[datetime] = None

class ScheduleRequest(BaseModel):
    mentor_id: str
    start_time: datetime
    duration: int = 30
    topic: str

@router.get("/mentors")
def list_mentors(skill: Optional[str] = None, db: Session = Depends(get_db)):
    mentors = db.query(User).filter(User.is_mentor == True, User.is_active == True).all()
    
    if not mentors:
        # Mock mentors
        return [
            {"id": "m1", "username": "BlackHoleSurvivor", "displayName": "Yassine T.", "level": 11.36, "specialties": ["C", "Systems", "Memory"], "rating": 4.9, "sessions": 127, "avatar": "https://i.pravatar.cc/80?img=12"},
            {"id": "m2", "username": "chaimacoder", "displayName": "Chaima B.", "level": 10.87, "specialties": ["Web", "SRE", "Docker"], "rating": 4.8, "sessions": 94, "avatar": "https://i.pravatar.cc/80?img=45"},
        ]
    
    result = []
    for m in mentors:
        result.append({
            "id": m.id,
            "username": m.username,
            "displayName": m.display_name,
            "level": m.level,
            "specialties": list(m.skills.keys()) if m.skills else ["C", "Systems"],
            "rating": 4.8,
            "sessions": 50,
            "avatar": m.avatar_url
        })
    
    if skill:
        result = [r for r in result if skill.lower() in str(r["specialties"]).lower()]
    
    return result

@router.post("/request")
def request_mentorship(payload: MentorRequest, current_user: User = Depends(get_current_user)):
    return {
        "ok": True,
        "request_id": f"mr_{current_user.id[:4]}_{payload.topic[:3]}",
        "topic": payload.topic,
        "status": "pending",
        "message": "Demande envoyée, un mentor va te répondre sous 24h"
    }

@router.post("/schedule")
def schedule_session(payload: ScheduleRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mentor = db.query(User).filter(User.id == payload.mentor_id).first()
    if not mentor:
        # Allow mock
        pass
    
    return {
        "ok": True,
        "session_id": f"sess_{payload.mentor_id[:4]}_{int(datetime.utcnow().timestamp())}",
        "mentor_id": payload.mentor_id,
        "student_id": current_user.id,
        "start_time": payload.start_time.isoformat(),
        "duration": payload.duration,
        "topic": payload.topic,
        "status": "scheduled",
        "room_url": f"/rooms/mentor_{payload.mentor_id[:4]}"
    }

@router.get("/sessions")
def my_sessions(current_user: User = Depends(get_current_user)):
    return {
        "as_mentor": [
            {"id": "sess_1", "student": "nour_dev", "topic": "Pointeurs", "time": "Aujourd'hui 16:30", "status": "scheduled"},
        ] if current_user.is_mentor else [],
        "as_student": [
            {"id": "sess_2", "mentor": "BlackHoleSurvivor", "topic": "Minishell parsing", "time": "Demain 10:00", "status": "scheduled"},
        ]
    }

@router.post("/become-mentor")
def become_mentor(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.level < 7:
        raise HTTPException(status_code=400, detail="Niveau 7.00 minimum requis pour devenir mentor")
    
    current_user.is_mentor = True
    db.commit()
    
    return {"ok": True, "message": "Félicitations, tu es maintenant mentor !", "level": current_user.level}
