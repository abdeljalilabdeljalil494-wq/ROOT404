from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

router = APIRouter(prefix="/hiring", tags=["Hiring & Corporate"])

# Mock corporate data - in prod would be separate tables
COMPANIES = [
    {"id": "c1", "name": "InstaDeep", "logo": "https://via.placeholder.com/80", "sector": "AI", "location": "Tunis", "open_positions": 5},
    {"id": "c2", "name": "Talan Tunisie", "logo": "https://via.placeholder.com/80", "sector": "SRE", "location": "Tunis", "open_positions": 3},
    {"id": "c3", "name": "Expensya", "logo": "https://via.placeholder.com/80", "sector": "FinTech", "location": "Tunis", "open_positions": 8},
]

CHALLENGES = [
    {"id": "hc1", "company": "InstaDeep", "title": "Optimise un pipeline de données", "difficulty": 4, "xp": 2000, "applicants": 24, "deadline": "2026-10-01"},
    {"id": "hc2", "company": "Talan", "title": "Débug un microservice en prod", "difficulty": 5, "xp": 3000, "applicants": 18, "deadline": "2026-09-25"},
]

class ApplicationRequest(BaseModel):
    challenge_id: str
    cover_letter: Optional[str] = None
    portfolio_url: Optional[str] = None

@router.get("/companies")
def list_companies():
    return COMPANIES

@router.get("/challenges")
def list_challenges():
    return CHALLENGES

@router.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: str):
    for c in CHALLENGES:
        if c["id"] == challenge_id:
            return c
    return {"detail": "Not found"}

@router.post("/challenges/{challenge_id}/apply")
def apply_challenge(challenge_id: str, payload: ApplicationRequest, current_user: User = Depends(get_current_user)):
    return {
        "ok": True,
        "challenge_id": challenge_id,
        "user": current_user.username,
        "status": "applied",
        "message": "Candidature envoyée, l'entreprise va examiner ton portfolio"
    }

@router.get("/portfolio/{username}/hiring")
def get_hiring_portfolio(username: str, db: Session = Depends(get_db)):
    from app.models.user import User as UserModel
    user = db.query(UserModel).filter(UserModel.username == username.lower()).first()
    if not user:
        return {"detail": "User not found"}
    
    return {
        "username": user.username,
        "level": user.level,
        "projects_done": user.projects_done,
        "skills": user.skills,
        "reputation": user.reputation,
        "integrity": user.integrity_score,
        "hireable": user.level >= 5,
        "contact": f"{user.username}@root404.tn",
        "portfolio_url": f"https://root404.tn/u/{user.username}"
    }

@router.get("/fair")
def partner_fair():
    return {
        "name": "ROOT 404 Partner Fair — Automne 2026",
        "date": "2026-10-15",
        "companies": COMPANIES,
        "workshops": [
            {"title": "Comment réussir un entretien système", "company": "Talan", "time": "10:00"},
            {"title": "De 0 à 10k utilisateurs : infra", "company": "Expensya", "time": "14:00"},
        ],
        "stats": {
            "companies": 12,
            "positions": 47,
            "hired_last_edition": 23
        }
    }
