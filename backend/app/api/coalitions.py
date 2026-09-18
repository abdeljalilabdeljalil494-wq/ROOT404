from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.coalition import CoalitionService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/coalitions", tags=["Coalitions"])

class JoinRequest(BaseModel):
    coalition_id: str

@router.get("/")
def list_coalitions(db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    return CoalitionService.get_leaderboard(db)

@router.post("/join")
def join_coalition(payload: JoinRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    member = CoalitionService.assign_user_to_coalition(current_user, db, payload.coalition_id)
    return {"ok": True, "coalition_id": payload.coalition_id}

@router.get("/wars")
def get_wars(db: Session = Depends(get_db)):
    return CoalitionService.get_active_wars(db)

@router.post("/wars")
def create_war(name: str, description: str = "", duration_hours: int = 48, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    war = CoalitionService.create_war(name, description, duration_hours, db)
    return {"id": war.id, "name": war.name, "status": war.status}

@router.get("/me")
def my_coalition(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    from app.models.coalition import Coalition
    if not current_user.coalition_id:
        return {"coalition": None, "message": "Pas de coalition"}
    
    coalition = db.query(Coalition).filter(Coalition.id == current_user.coalition_id).first()
    if not coalition:
        return {"coalition": None}
    
    contribution = CoalitionService.calculate_user_contribution(current_user.id, db)
    
    return {
        "id": coalition.id,
        "name": coalition.name,
        "color": coalition.color,
        "motto": coalition.motto,
        "points": coalition.points,
        "members": coalition.members_count,
        "contribution": contribution,
        "rank": 2  # Would calculate real rank
    }
