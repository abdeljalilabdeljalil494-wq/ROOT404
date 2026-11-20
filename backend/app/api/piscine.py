from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models import PiscineDay, UserPiscineProgress
from datetime import datetime

router = APIRouter(prefix="/piscine", tags=["Piscine"])

@router.get("/days")
def get_days(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    days = db.query(PiscineDay).order_by(PiscineDay.day_number.asc()).all()
    
    # Get user progress
    progress_map = {}
    progresses = db.query(UserPiscineProgress).filter(UserPiscineProgress.user_id == current_user.id).all()
    for p in progresses:
        progress_map[p.day_id] = p
    
    result = []
    for day in days:
        prog = progress_map.get(day.id)
        result.append({
            "id": day.id,
            "day": day.day_number,
            "title": day.title,
            "topic": day.topic,
            "status": prog.status if prog else ("available" if day.day_number == 1 else "locked"),
            "score": prog.score if prog else None,
            "isRush": day.is_rush,
            "exercises": day.exercises
        })
    
    return result

@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    days = db.query(PiscineDay).count()
    done = db.query(UserPiscineProgress).filter(
        UserPiscineProgress.user_id == current_user.id,
        UserPiscineProgress.status == "done"
    ).count()
    
    return [
        {"label": "Jours du programme", "value": str(days), "icon": "CalendarDays"},
        {"label": "Jours validés", "value": str(done), "icon": "CheckCircle2"},
    ]

@router.post("/seed", dependencies=[Depends(require_admin)])
def seed_piscine(db: Session = Depends(get_db)):
    seed_days(db)
    return {"ok": True}

def seed_days(db: Session):
    if db.query(PiscineDay).count() > 0:
        return
    
    topics = ['Shell', 'Variables', 'Boucles', 'Pointeurs', 'Chaînes', 'Structs', 'Rush']
    for i in range(28):
        d = i + 1
        day = PiscineDay(
            day_number=d,
            title=f"Day {str(d).zfill(2)}",
            topic=topics[i % 7],
            is_rush=(d % 7 == 0),
            exercises=[
                {"name": f"ex{str(j).zfill(2)}", "title": f"Exercise {j}", "difficulty": (j % 3) + 1}
                for j in range(1, 6)
            ]
        )
        db.add(day)
    db.commit()
