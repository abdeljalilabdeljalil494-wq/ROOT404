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
from app.services.activity import daily_counts

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    counts = daily_counts(db, current_user.id, 28)
    active = sum(count > 0 for _, count in counts)
    return {"velocity": sum(count for _, count in counts[-7:]),
            "consistency": round(active * 100 / 28), "tolerance": [],
            "insight": "Vitesse : soumissions sur 7 jours. Régularité : jours actifs sur 28 jours (UTC).",
            "forecast": None, "timeToSolve": [], "source": "submissions.created_at"}

@router.get("/skills")
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SkillGraphService.get_skill_graph_for_user(current_user)

@router.get("/journey")
def get_journey(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.project import Project
    rows = db.query(Project, UserProjectProgress).outerjoin(UserProjectProgress,
        (UserProjectProgress.project_id == Project.id) & (UserProjectProgress.user_id == current_user.id)
    ).order_by(Project.level_value, Project.slug).all()
    return [{"id": project.id, "title": project.name,
             "status": "done" if progress and progress.status == "passed" else "current" if progress else "next",
             "projects": 1, "skills": project.tags or [], "progress": progress.progress if progress else 0}
            for project, progress in rows]

@router.get("/heatmap")
def get_heatmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [min(4, count) for _, count in daily_counts(db, current_user.id, 371)]

@router.get("/reputation")
def get_reputation(current_user: User = Depends(get_current_user),db:Session=Depends(get_db)):
    from app.services.beta_progress import achievements
    return [{"label":"Reputation (beta-v1)","value":achievements(db,current_user)['reputation']}]

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
    counts = daily_counts(db, current_user.id, 28)
    history = [{"week": f"W{week + 1}", "value": sum(count for _, count in counts[week * 7:week * 7 + 7])} for week in range(4)]
    return {"velocity": history[-1]["value"], "trend": None, "history": history, "unit": "submissions/week"}
