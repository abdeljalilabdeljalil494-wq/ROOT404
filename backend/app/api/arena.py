from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models import ArenaMatch
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

router = APIRouter(prefix="/arena", tags=["Arena"])

class CreateMatchRequest(BaseModel):
    mode: str = "1v1"
    problem: Optional[str] = None

@router.get("/modes")
def get_modes():
    return [
        {"key": "1v1", "name": "1v1 Coding Battle", "desc": "Duel direct sur un même problème. Le plus rapide gagne.", "icon": "Swords", "players": "2", "time": "15 min"},
        {"key": "team", "name": "Team Battle", "desc": "Trois contre trois, score cumulé de la coalition.", "icon": "Users", "players": "3v3", "time": "45 min"},
        {"key": "speed", "name": "Speed Coding", "desc": "Le maximum de problèmes en un minimum de temps.", "icon": "Timer", "players": "∞", "time": "20 min"},
        {"key": "algo", "name": "Algorithm Duel", "desc": "Meilleure complexité gagnante, pas la plus rapide à écrire.", "icon": "GitBranch", "players": "2", "time": "30 min"},
        {"key": "debug", "name": "Debugging Battle", "desc": "Un code cassé, sept bugs, un chronomètre.", "icon": "Bug", "players": "2", "time": "12 min"},
    ]

@router.get("/live")
def get_live_matches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = db.query(ArenaMatch).filter(ArenaMatch.status == "live").order_by(ArenaMatch.created_at.desc()).limit(10).all()
    
    result = []
    for m in matches:
        # Get usernames
        from app.models.user import User
        player_a = db.query(User).filter(User.id == m.player_a_id).first() if m.player_a_id else None
        player_b = db.query(User).filter(User.id == m.player_b_id).first() if m.player_b_id else None
        
        result.append({
            "id": m.id,
            "a": player_a.username if player_a else "unknown",
            "b": player_b.username if player_b else "unknown",
            "problem": m.problem,
            "time": m.started_at.isoformat() if m.started_at else None,
            "viewers": m.viewers
        })
    
    return result

@router.post("/match")
def create_match(payload: CreateMatchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    problems = ["Binary Search", "LRU Cache", "Merge Intervals", "Reverse Linked List", "Two Sum", "Valid Parentheses"]
    problem = payload.problem or random.choice(problems)
    
    match = ArenaMatch(
        mode=payload.mode,
        problem=problem,
        player_a_id=current_user.id,
        status="waiting",
        viewers=0
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return {
        "id": match.id,
        "mode": match.mode,
        "problem": match.problem,
        "status": match.status,
        "message": "En attente d'un adversaire..."
    }

@router.post("/match/{match_id}/join")
def join_match(match_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = db.query(ArenaMatch).filter(ArenaMatch.id == match_id).first()
    if not match:
        return {"ok": False, "message": "Match non trouvé"}
    
    if match.player_a_id == current_user.id:
        return {"ok": False, "message": "Tu es déjà dans ce match"}
    
    if match.player_b_id:
        return {"ok": False, "message": "Match déjà complet"}
    
    match.player_b_id = current_user.id
    match.status = "live"
    match.started_at = datetime.utcnow()
    
    db.commit()
    
    return {"ok": True, "match_id": match_id, "status": "live"}

@router.get("/leaderboard")
def arena_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    from app.api.leaderboard import get_arena_leaderboard
    return get_arena_leaderboard(limit, db)
