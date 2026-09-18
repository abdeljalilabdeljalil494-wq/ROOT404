from fastapi import APIRouter
from . import auth, projects, dashboard, leaderboard, rooms, judge, ai, analytics, peer_review, coalitions, piscine, arena, portfolio, hiring, exam, mentorship

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(dashboard.router)
api_router.include_router(leaderboard.router)
api_router.include_router(rooms.router)
api_router.include_router(judge.router)
api_router.include_router(ai.router)
api_router.include_router(analytics.router)
api_router.include_router(peer_review.router)
api_router.include_router(coalitions.router)
api_router.include_router(piscine.router)
api_router.include_router(arena.router)
api_router.include_router(portfolio.router)
api_router.include_router(hiring.router)
api_router.include_router(exam.router)
api_router.include_router(mentorship.router)

# Additional endpoints
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

@api_router.get("/health")
def health_check():
    return {"status": "ok", "service": "ROOT 404 API", "version": "1.0.0"}

@api_router.get("/user/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@api_router.get("/search")
def search(q: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.project import Project
    from app.models.user import User as UserModel
    
    projects = db.query(Project).filter(Project.name.ilike(f"%{q}%")).limit(5).all()
    users = db.query(UserModel).filter(UserModel.username.ilike(f"%{q}%")).limit(5).all()
    
    return {
        "projects": [{"slug": p.slug, "name": p.name, "level": p.level} for p in projects],
        "users": [{"username": u.username, "displayName": u.display_name, "level": u.level} for u in users],
        "query": q
    }
