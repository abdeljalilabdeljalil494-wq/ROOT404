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
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.is_active == True).order_by(desc(User.level), desc(User.xp))
    
    if campus:
        query = query.filter(User.campus == campus)
    if coalition:
        # Find coalition id by name
        coal = db.query(Coalition).filter(Coalition.name == coalition).first()
        if coal:
            query = query.filter(User.coalition_id == coal.id)
    
    users = query.limit(limit).all()
    
    result = []
    for idx, u in enumerate(users, 1):
        coal = db.query(Coalition).filter(Coalition.id == u.coalition_id).first() if u.coalition_id else None
        result.append({
            "rank": idx,
            "user": u.username,
            "name": u.full_name or u.display_name,
            "level": round(u.level, 2),
            "xp": f"{u.xp:,}".replace(",", " "),
            "xp_raw": u.xp,
            "projects": u.projects_done,
            "accuracy": u.accuracy,
            "coalition": coal.name if coal else "Sans coalition",
            "campus": u.campus,
            "avatar": u.avatar_url or f"https://i.pravatar.cc/80?u={u.username}",
            "me": current_user.id == u.id if current_user else False
        })
    
    # If no users, return mock data
    if not result:
        from app.models import User as UserModel
        # Return mock leaderboard from frontend mock.js equivalent
        mock = [
            {"rank": 1, "user": "BlackHoleSurvivor", "name": "Yassine T.", "level": 11.36, "xp": "58,420", "xp_raw": 58420, "projects": 64, "accuracy": 93, "coalition": "The Phoenix", "campus": "Tunis", "avatar": "https://i.pravatar.cc/80?img=12", "me": False},
            {"rank": 2, "user": "chaimacoder", "name": "Chaima B.", "level": 10.87, "xp": "51,110", "xp_raw": 51110, "projects": 60, "accuracy": 91, "coalition": "Neon Wolves", "campus": "Tunis", "avatar": "https://i.pravatar.cc/80?img=45", "me": False},
            {"rank": 3, "user": "mehdi42", "name": "Mehdi K.", "level": 9.94, "xp": "46,230", "xp_raw": 46230, "projects": 52, "accuracy": 90, "coalition": "Data Vipers", "campus": "Sfax", "avatar": "https://i.pravatar.cc/80?img=33", "me": False},
            {"rank": 4, "user": "abdeljalil", "name": "Abdeljalil B.", "level": 6.42, "xp": "24,780", "xp_raw": 24780, "projects": 38, "accuracy": 81, "coalition": "The Phoenix", "campus": "Tunis", "avatar": "https://i.pravatar.cc/160?img=13", "me": True},
        ]
        return mock
    
    return result

@router.get("/coalitions")
def get_coalitions(db: Session = Depends(get_db)):
    CoalitionService.seed_default_coalitions(db)
    return CoalitionService.get_leaderboard(db)

@router.get("/campus")
def get_campus_leaderboard(db: Session = Depends(get_db)):
    from app.core.config import settings
    result = {}
    for campus in settings.CAMPUSES:
        count = db.query(User).filter(User.campus == campus, User.is_active == True).count()
        top_user = db.query(User).filter(User.campus == campus).order_by(desc(User.level)).first()
        result[campus] = {
            "campus": campus,
            "members": count,
            "top_user": top_user.username if top_user else None,
            "top_level": top_user.level if top_user else 0
        }
    return result

@router.get("/arena")
def get_arena_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    # Arena has separate scoring
    # For now return global with arena points simulated
    users = db.query(User).filter(User.is_active == True).order_by(desc(User.xp)).limit(limit).all()
    result = []
    for idx, u in enumerate(users, 1):
        arena_score = 2400 - idx * 137 + (u.xp % 100)
        result.append({
            "rank": idx,
            "user": u.username,
            "arena_score": max(0, arena_score),
            "wins": u.projects_done // 2,
            "accuracy": u.accuracy,
            "avatar": u.avatar_url
        })
    
    if not result:
        # Mock
        return [
            {"rank": 1, "user": "mehdi42", "arena_score": 2400, "wins": 24, "accuracy": 92},
            {"rank": 2, "user": "ines_dev", "arena_score": 2263, "wins": 19, "accuracy": 88},
            {"rank": 3, "user": "chaimacoder", "arena_score": 2126, "wins": 17, "accuracy": 90},
        ]
    
    return result
