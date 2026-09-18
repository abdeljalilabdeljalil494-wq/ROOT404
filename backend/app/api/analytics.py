from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.skill_graph import SkillGraphService
from app.services.integrity import IntegrityService
from app.services.gamification import GamificationService, calculate_level_progress
from app.services.blackhole import BlackHoleService
from app.models.project import UserProjectProgress
from app.models.submission import Submission
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Time to solve trends
    time_to_solve = [
        {"label": "Algo", "you": 3.2, "avg": 4.1},
        {"label": "Mémoire", "you": 7.8, "avg": 4.6},
        {"label": "Réseau", "you": 5.1, "avg": 5.4},
        {"label": "Parsing", "you": 4.4, "avg": 5.0},
        {"label": "Threads", "you": 6.9, "avg": 5.2},
    ]
    
    # Tolerance
    tolerance = [
        {"label": "Easy", "value": 100},
        {"label": "Medium", "value": 88},
        {"label": "Hard", "value": 61},
        {"label": "Extreme", "value": 28},
    ]
    
    # Calculate velocity and consistency
    submissions = db.query(Submission).filter(Submission.user_id == current_user.id).order_by(Submission.created_at.desc()).limit(20).all()
    
    velocity = 78  # Mock, would be calculated from completion times
    consistency = 91
    
    if submissions:
        # Simple consistency based on regular submissions
        if len(submissions) >= 5:
            consistency = min(95, 70 + len(submissions) * 2)
    
    return {
        "velocity": velocity,
        "consistency": consistency,
        "tolerance": tolerance,
        "insight": "Tu résous les exercices d'algorithmie rapidement, mais tu passes 2,4× plus de temps à déboguer les problèmes liés à la mémoire.",
        "forecast": "14 mars 2027",
        "timeToSolve": time_to_solve
    }

@router.get("/skills")
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SkillGraphService.get_skill_graph_for_user(current_user)

@router.get("/journey")
def get_journey(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Journey stages
    stages = [
        {"id": 0, "title": "LEVEL 00 — Piscine", "status": "done", "projects": 12, "skills": ["Shell", "Logique", "C basics"], "progress": 100},
        {"id": 1, "title": "C / Programming", "status": "done", "projects": 8, "skills": ["Pointeurs", "Structs", "Libc"], "progress": 100},
        {"id": 2, "title": "Algorithms", "status": "current", "projects": 6, "skills": ["Tri", "Récursion", "Complexité"], "progress": 62},
        {"id": 3, "title": "Memory / Systems", "status": "next", "projects": 7, "skills": ["Threads", "Processus", "Signaux"], "progress": 0},
        {"id": 4, "title": "Advanced", "status": "locked", "projects": 9, "skills": ["Réseau", "Graphique", "C++"], "progress": 0},
        {"id": 5, "title": "Final Project", "status": "locked", "projects": 1, "skills": ["Fullstack", "Temps réel"], "progress": 0},
    ]
    
    # Adjust based on user level
    level = current_user.level
    if level >= 6:
        stages[2]["status"] = "done"
        stages[2]["progress"] = 100
        stages[3]["status"] = "current"
        stages[3]["progress"] = int((level - 6) * 30)
    
    return stages

@router.get("/heatmap")
def get_heatmap(current_user: User = Depends(get_current_user)):
    heatmap = []
    for i in range(53 * 7):
        seed = (i * 2654435761 + hash(current_user.id)) % 4294967296
        r = (seed / 4294967296 + (i * 0.7 % 1) * 0.3 + 0.2) % 1
        if r < 0.32:
            heatmap.append(0)
        elif r < 0.5:
            heatmap.append(1)
        elif r < 0.7:
            heatmap.append(2)
        elif r < 0.88:
            heatmap.append(3)
        else:
            heatmap.append(4)
    return heatmap

@router.get("/reputation")
def get_reputation(current_user: User = Depends(get_current_user)):
    return [
        {"label": "Code Quality", "value": 92},
        {"label": "Peer Reviewer", "value": 87},
        {"label": "Community", "value": 78},
        {"label": "Mentorship", "value": 91},
        {"label": "Reliability", "value": 95},
    ]

@router.get("/integrity")
def get_integrity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return IntegrityService.calculate_score(current_user, db)

@router.get("/blackhole")
def get_blackhole(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    days_left = BlackHoleService.calculate_days_left(current_user, db)
    recommendation = BlackHoleService.get_recommendation(current_user, days_left)
    return {
        "daysLeft": days_left,
        "total": current_user.blackhole_total,
        "warning": current_user.blackhole_warning,
        "recommendation": recommendation
    }

@router.get("/velocity")
def get_velocity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Learning velocity over time
    return {
        "velocity": 78,
        "trend": "+5% cette semaine",
        "history": [
            {"week": "W1", "value": 65},
            {"week": "W2", "value": 70},
            {"week": "W3", "value": 72},
            {"week": "W4", "value": 78},
        ]
    }
