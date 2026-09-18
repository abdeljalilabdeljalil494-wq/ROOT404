from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import UserProjectProgress, Project
from app.models.submission import Submission
from app.models import DailyMission
from app.services.gamification import GamificationService, calculate_level_progress, xp_to_level
from app.services.blackhole import BlackHoleService
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate stats
    progress_count = db.query(UserProjectProgress).filter(
        UserProjectProgress.user_id == current_user.id,
        UserProjectProgress.status == "passed"
    ).count()
    
    return [
        {"key": "xp", "label": "XP", "value": f"{current_user.xp:,}".replace(",", " "), "sub": "Total", "icon": "Zap", "delta": "+1,240"},
        {"key": "done", "label": "Projets terminés", "value": str(progress_count), "sub": "sur 92", "icon": "CheckCircle2", "delta": "+2"},
        {"key": "cp", "label": "Correction Points", "value": f"{current_user.correction_points:,}".replace(",", " "), "sub": "+80 cette sem.", "icon": "Users", "delta": "+80"},
        {"key": "wallet", "label": "Valeur de compte", "value": f"{current_user.account_value:,}".replace(",", " "), "sub": f"{current_user.jetons} jetons", "icon": "Coins", "delta": "+150"},
    ]

@router.get("/activity")
def get_activity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).order_by(Submission.created_at.desc()).limit(5).all()
    
    result = []
    for sub in submissions:
        project = db.query(Project).filter(Project.id == sub.project_id).first()
        result.append({
            "id": sub.id,
            "project": project.slug if project else "unknown",
            "kind": "Moulinette réussie" if sub.score and sub.score >= 80 else "Moulinette échouée" if sub.score else "Soumission en attente",
            "score": str(sub.score) if sub.score else "En cours",
            "tone": "ok" if sub.score and sub.score >= 80 else "danger" if sub.score and sub.score < 80 else "brand",
            "time": "il y a 2 h"  # Simplified
        })
    
    if not result:
        result = [
            {"id": 1, "project": "get_next_line", "kind": "Moulinette réussie", "score": "100", "tone": "ok", "time": "il y a 2 h"},
            {"id": 2, "project": "ft_printf", "kind": "Peer Review validé", "score": "115", "tone": "ok", "time": "il y a 5 h"},
            {"id": 3, "project": "minishell", "kind": "Soumission en attente", "score": "En cours", "tone": "brand", "time": "hier"},
        ]
    
    return result

@router.get("/weekly")
def get_weekly(current_user: User = Depends(get_current_user)):
    # Mock weekly activity - in prod from real data
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    values = [42, 68, 95, 54, 78, 88, 31]
    return [{"day": d, "value": v} for d, v in zip(days, values)]

@router.get("/overview")
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = get_stats(current_user, db)
    activity = get_activity(current_user, db)
    weekly = get_weekly(current_user)
    
    # Daily mission
    mission = GamificationService.generate_daily_mission(current_user, db)
    
    # Black hole
    days_left = BlackHoleService.calculate_days_left(current_user, db)
    bh_status = BlackHoleService.get_recommendation(current_user, days_left)
    
    # Level progress
    level_progress = calculate_level_progress(current_user.xp)
    
    return {
        "user": current_user.to_dict(),
        "level": current_user.level,
        "levelProgress": level_progress,
        "xpToNext": current_user.xp_to_next,
        "stats": stats,
        "recentActivity": activity,
        "weeklyActivity": weekly,
        "dailyMission": {
            "title": mission.title if mission else "Reverse a linked list",
            "difficulty": mission.difficulty if mission else 3,
            "time": "~30 min",
            "reward": mission.reward_xp if mission else 120,
            "skill": mission.skill if mission else "Structures de données"
        },
        "blackHole": {
            "daysLeft": days_left,
            "total": current_user.blackhole_total,
            "status": bh_status
        }
    }

@router.get("/heatmap")
def get_heatmap(current_user: User = Depends(get_current_user)):
    # 53 weeks * 7 days deterministic heatmap
    heatmap = []
    for i in range(53 * 7):
        seed = (i * 2654435761) % 4294967296
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
