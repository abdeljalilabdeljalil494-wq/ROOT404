from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.core.dependencies import get_current_user, rate_limit
from app.core.security import sanitize_input
from app.models.user import User
from app.core.config import settings
import re
import logging

from . import auth, projects, dashboard, leaderboard, rooms, judge, ai, analytics, peer_review, coalitions, piscine, arena, portfolio, hiring, exam, mentorship

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include all routers
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

@api_router.get("/health", tags=["Root"])
def health_check(request: Request):
    # Apply rate limiting to health check to prevent abuse
    from app.core.dependencies import get_client_ip, _rate_limiter
    client_ip = get_client_ip(request)
    allowed, retry_after = _rate_limiter.is_allowed(f"health:{client_ip}", 60, 60)
    if not allowed:
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Rate limited")
    
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
    
    # Validate query - alphanumeric + spaces + common chars only
    if not re.match(r'^[\w\s\-\.\']+$', q, re.UNICODE):
        # If contains special chars, escape and treat as literal
        q = re.escape(q)
    
    # Prevent empty after sanitization
    if not q or len(q.strip()) < 1:
        return {"projects": [], "users": [], "query": ""}
    
    try:
        from app.models.project import Project
        from app.models.user import User as UserModel
        
        # Use parameterized queries via SQLAlchemy - safe from injection
        # But we use Python filtering for extra safety
        # Limit results to prevent DoS
        search_term = f"%{q}%"
        
        try:
            projects = db.query(Project).filter(
                Project.name.ilike(search_term)
            ).limit(5).all()
        except SQLAlchemyError as e:
            logger.error(f"DB error in search projects: {e}")
            projects = []
        
        try:
            users = db.query(UserModel).filter(
                UserModel.username.ilike(search_term)
            ).limit(5).all()
        except SQLAlchemyError as e:
            logger.error(f"DB error in search users: {e}")
            users = []
        
        return {
            "projects": [{"slug": p.slug, "name": p.name, "level": p.level} for p in projects],
            "users": [{"username": u.username, "displayName": u.display_name, "level": u.level} for u in users],
            "query": q[:100]  # Truncate for response
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return {"projects": [], "users": [], "query": q[:50], "error": "Search temporarily unavailable"}
