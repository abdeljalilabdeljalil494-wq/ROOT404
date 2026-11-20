from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.coalition import Coalition
from app.services.coalition import CoalitionService

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("/")
def get_global_leaderboard(
    campus: str = Query(None),
    coalition: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.is_active == True, User.directory_visible == True).order_by(desc(User.level), desc(User.xp), User.username)
    
    if campus:
        query = query.filter(User.campus == campus)
    if coalition:
        # Find coalition id by name
        coal = db.query(Coalition).filter(Coalition.name == coalition).first()
        if not coal:
            return []
        query = query.filter(User.coalition_id == coal.id)
    
    users = query.limit(limit).all()
    
    result = []
    for idx, u in enumerate(users, 1):
        coal = db.query(Coalition).filter(Coalition.id == u.coalition_id).first() if u.coalition_id else None
        result.append({
            "rank": idx,
            "user": u.username,
            "name": u.display_name,
            "level": round(u.level, 2),
            "xp": f"{u.xp:,}".replace(",", " "),
            "xp_raw": u.xp,
            "projects": u.projects_done,
            "accuracy": u.accuracy,
            "coalition": coal.name if coal else "Sans coalition",
            "campus": u.campus,
            "avatar": u.avatar_url,
            "me": current_user.id == u.id if current_user else False
        })
    
    return result

@router.get("/coalitions")
def get_coalitions(db: Session = Depends(get_db)):
    return CoalitionService.get_leaderboard(db)

@router.get("/campus")
def get_campus_leaderboard(db: Session = Depends(get_db)):
    from app.core.config import settings
    result = {}
    for campus in settings.CAMPUSES:
        count = db.query(User).filter(User.campus == campus, User.is_active == True, User.directory_visible == True).count()
        top_user = db.query(User).filter(User.campus == campus, User.is_active == True, User.directory_visible == True).order_by(desc(User.level)).first()
        result[campus] = {
            "campus": campus,
            "members": count,
            "top_user": top_user.username if top_user else None,
            "top_level": top_user.level if top_user else 0
        }
    return result

@router.get("/arena")
def get_arena_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    from app.models import ArenaMatch
    from sqlalchemy import func
    rows = db.query(User, func.count(ArenaMatch.id).label('wins')).join(
        ArenaMatch, ArenaMatch.winner_id == User.id
    ).filter(ArenaMatch.status == 'finished', User.directory_visible == True, User.is_active == True).group_by(User.id).order_by(func.count(ArenaMatch.id).desc()).limit(min(500, max(1, limit))).all()
    return [{"rank": rank, "user": user.username, "wins": wins, "arena_score": wins,
             "avatar": user.avatar_url} for rank, (user, wins) in enumerate(rows, 1)]
