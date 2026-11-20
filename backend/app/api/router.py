from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.core.dependencies import get_current_user, rate_limit, require_demo_mode
from app.core.security import sanitize_input
from app.models.user import User
from app.core.config import settings
import logging

from . import beta, oauth, notifications, account, auth, projects, dashboard, leaderboard, rooms, judge, ai, analytics, peer_review, coalitions, piscine, arena, portfolio, hiring, exam, mentorship

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(beta.router)
api_router.include_router(oauth.router)
api_router.include_router(account.router)
api_router.include_router(notifications.router)
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
api_router.include_router(hiring.router, dependencies=[Depends(require_demo_mode)])
api_router.include_router(exam.router, dependencies=[Depends(require_demo_mode)])
api_router.include_router(mentorship.router, dependencies=[Depends(require_demo_mode)])

@api_router.get("/health", tags=["Root"])
def health_check(request: Request):
    # Apply rate limiting to health check to prevent abuse
    rate_limit(request, max_requests=60, window=60, key_prefix="health")

    return {"status": "ok", "service": "ROOT 404 API", "version": "1.0.0", "environment": settings.ENVIRONMENT}

@api_router.get("/user/me", tags=["Root"])
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@api_router.get("/search", tags=["Root"])
def search(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Secure search with input sanitization and SQL injection prevention"""
    # Rate limit search
    if request:
        from app.core.dependencies import rate_limit
        rate_limit(request, max_requests=30, window=60, key_prefix="search")
    
    # Sanitize input
    q = sanitize_input(q, max_length=100)
    
    if not q.strip():
        return {"projects": [], "users": [], "query": ""}
    from app.models.project import Project
    from app.models.user import User as UserModel
    # Parameterization prevents SQL injection; escaping LIKE metacharacters
    # separately makes search literal rather than a wildcard directory dump.
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    search_term = "%" + escaped + "%"
    try:
        projects = db.query(Project).filter(Project.name.ilike(search_term, escape="\\")).order_by(Project.name).limit(5).all()
        users = db.query(UserModel).filter(
            UserModel.username.ilike(search_term, escape="\\"), UserModel.directory_visible == True,
            UserModel.public_profile == True, UserModel.is_active == True
        ).order_by(UserModel.username).limit(5).all()
    except SQLAlchemyError:
        logger.error("Search storage unavailable")
        raise HTTPException(503, "Search temporarily unavailable")
    return {
        "projects": [{"slug": p.slug, "name": p.name, "level": p.level} for p in projects],
        "users": [{"username": u.username, "displayName": u.display_name, "level": u.level} for u in users],
        "query": q,
    }
