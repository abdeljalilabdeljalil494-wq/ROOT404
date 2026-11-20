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
from app.services.activity import daily_counts

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Calculate stats
    progress_count = db.query(UserProjectProgress).filter(
        UserProjectProgress.user_id == current_user.id,
        UserProjectProgress.status == "passed"
    ).count()
    
    return [
        {"key": "xp", "label": "XP", "value": f"{current_user.xp:,}".replace(",", " "), "sub": "Total", "icon": "Zap", "delta": ""},
        {"key": "done", "label": "Projets terminés", "value": str(progress_count), "sub": "Total", "icon": "CheckCircle2", "delta": ""},
        {"key": "cp", "label": "Correction Points", "value": f"{current_user.correction_points:,}".replace(",", " "), "sub": "Total", "icon": "Users", "delta": ""},
        {"key": "wallet", "label": "Valeur de compte", "value": f"{current_user.account_value:,}".replace(",", " "), "sub": f"{current_user.jetons} jetons", "icon": "Coins", "delta": ""},
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
            "kind": "Moulinette réussie" if sub.score is not None and sub.score >= 80 else "Moulinette échouée" if sub.score is not None else "Soumission en attente",
            "score": str(sub.score) if sub.score is not None else "En cours",
            "tone": "ok" if sub.score is not None and sub.score >= 80 else "danger" if sub.score is not None and sub.score < 80 else "brand",
            "time": sub.created_at.isoformat()
        })
    
    return result

@router.get("/weekly")
def get_weekly(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"day": day.isoformat(), "value": count} for day, count in daily_counts(db, current_user.id, 7)]

@router.get("/overview")
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = get_stats(current_user, db)
    activity = get_activity(current_user, db)
    weekly = get_weekly(current_user, db)
    
    # Daily mission
    from app.services.beta_progress import mission as current_mission
    mission = current_mission(db,current_user)
    
    # Black hole
    days_left = BlackHoleService.calculate_days_left(current_user, db)
    bh_status = BlackHoleService.get_recommendation(current_user, days_left)
    
    # Level progress
    level_progress = calculate_level_progress(current_user.xp)
    
    return {
        "user": current_user.to_dict(),
        "level": current_user.level,
        "levelProgress": level_progress,
        "xpToNext": current_user.to_dict()["xpToNext"],
        "stats": stats,
        "recentActivity": activity,
        "weeklyActivity": weekly,
        "dailyMission": {**mission,"reward":mission['reward_xp'],"difficulty":1,"time":"UTC","skill":"Stream Sum — Python"},
        "blackHole": {
            "daysLeft": days_left,
            "total": current_user.blackhole_total,
            "status": bh_status
        }
    }

@router.get("/heatmap")
def get_heatmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [min(4, count) for _, count in daily_counts(db, current_user.id, 371)]
