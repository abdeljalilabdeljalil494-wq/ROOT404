from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.project import UserProjectProgress, Project
from app.models import UserBadge, Badge

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/{username}")
def get_portfolio(username: str, db: Session = Depends(get_db), viewer: User = Depends(get_current_user_optional)):
    user = db.query(User).filter(User.username == username.lower()).first()
    if not user or not user.is_active or (not user.public_profile and (viewer is None or viewer.id != user.id)):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Projects
    progresses = db.query(UserProjectProgress).filter(
        UserProjectProgress.user_id == user.id,
        UserProjectProgress.status == "passed"
    ).all()

    projects = []
    for prog in progresses:
        proj = db.query(Project).filter(Project.id == prog.project_id).first()
        if proj:
            projects.append({
                "name": proj.name,
                "slug": proj.slug,
                "level": proj.level,
                "score": prog.best_score,
                "xp": proj.xp
            })

    # Badges
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == user.id).all()
    badges = []
    for ub in user_badges:
        badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()
        if badge:
            badges.append({
                "name": badge.name,
                "icon": badge.icon,
                "tier": badge.tier
            })

    from app.services.beta_progress import achievements
    measured=achievements(db,user)
    badges.extend({'name':badge['name'],'tier':badge['tier'],'icon':'Trophy'} for badge in measured['badges'] if badge['earned'] and badge['name'] not in {row['name'] for row in badges})

    # Skills - simplified
    skills = []
    if user.skills:
        for group, vals in user.skills.items():
            if isinstance(vals, dict):
                avg = sum(vals.values()) / len(vals) if vals else 0
                skills.append({
                    "group": group,
                    "value": int(avg),
                    "details": [{"name": k, "value": v} for k, v in vals.items()]
                })

    return {
        "username": user.username,
        "displayName": user.display_name,

        "avatar": user.avatar_url,
        "level": round(user.level, 2),
        "xp": user.xp,
        "campus": user.campus,
        "coalition": user.coalition_id,
        "bio": user.bio or f"Étudiant ROOT 404 - Level {user.level:.2f}",
        "projectsDone": user.projects_done,
        "projects": projects,
        "skills": skills,
        "badges": badges,
        "reputation": measured["reputation"],
        "streak": measured["streak"],
        "joined": user.created_at.strftime("%b. %Y") if user.created_at else "",
        "socials": user.socials or {},
        "url": f"root404.tn/u/{user.username}"
    }

@router.get("/me/portfolio")
def my_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_portfolio(current_user.username, db, current_user)

@router.get("/public/{username}/widget")
def get_widget(username: str, db: Session = Depends(get_db)):
    """Public widget for embedding - returns minimal data"""
    user = db.query(User).filter(User.username == username.lower()).first()
    if not user or not user.is_active or not user.public_profile:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return {
        "username": user.username,
        "level": round(user.level, 2),
        "xp": user.xp,
        "projectsDone": user.projects_done,
        "campus": user.campus,
        "badge": None,
        "embed_html": f'<iframe src="https://root404.tn/u/{user.username}/embed" width="300" height="200"></iframe>'
    }
