from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.services.coalition import CoalitionService
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/coalitions", tags=["Coalitions"])

class JoinRequest(BaseModel):
    coalition_id: str = Field(min_length=1, max_length=32)

@router.get("/")
def list_coalitions(db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    return CoalitionService.get_leaderboard(db)

@router.post("/join")
def join_coalition(payload: JoinRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    member = CoalitionService.assign_user_to_coalition(current_user, db, payload.coalition_id)
    if member is None:
        raise HTTPException(404, "Coalition not found")
    if member.coalition_id != payload.coalition_id:
        raise HTTPException(409, "Already a member of another coalition")
    return {"ok": True, "coalition_id": member.coalition_id}

@router.get("/wars")
def get_wars(db: Session = Depends(get_db)):
    return CoalitionService.get_active_wars(db)

@router.post("/wars")
def create_war(name: str, description: str = "", duration_hours: int = 48, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    if not name.strip() or len(name)>100 or len(description)>500 or not 1<=duration_hours<=168:
        raise HTTPException(422, 'Invalid war parameters')
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
        "points": sum(u.xp for u in db.query(User).filter_by(coalition_id=coalition.id,is_active=True)),
        "members": db.query(User).filter_by(coalition_id=coalition.id,is_active=True).count(),
        "contribution": contribution,
        "rank": db.query(Coalition).filter(Coalition.points > coalition.points).count() + 1
    }
