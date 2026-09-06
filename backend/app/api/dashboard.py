"""Dashboard endpoints — computed live from the DB.

    GET /dashboard/stats     → 4 KPI tiles (mock.dashboardStats shape)
    GET /dashboard/activity  → recent timeline (mock.recentActivity shape)
    GET /dashboard/weekly    → last 7 days (mock.weeklyActivity shape)
"""

from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..services.serializers import activity_payload, fmt, now, user_payload, weekly_payload

router = APIRouter()

DONE_KINDS = ("Moulinette réussie", "Niveau validé")
CP_KIND = "Peer Review validé"


def _events(db: Session, user: models.User, since=None, limit=None):
    q = select(models.ActivityEvent).where(models.ActivityEvent.user_id == user.id)
    if since is not None:
        q = q.where(models.ActivityEvent.created_at >= since)
    q = q.order_by(models.ActivityEvent.created_at.desc())
    if limit:
        q = q.limit(limit)
    return db.execute(q).scalars().all()


@router.get("/stats")
def stats(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    week_ago = now() - timedelta(days=7)
    week_events = _events(db, user, since=week_ago)

    xp_week = sum(e.xp for e in week_events)
    done_week = sum(1 for e in week_events if e.kind in DONE_KINDS)
    cp_week = sum(1 for e in week_events if e.kind == CP_KIND) * 80

    n_projects = db.execute(select(models.Project)).scalars().all().__len__()

    return [
        {
            "key": "xp",
            "label": "XP",
            "value": fmt(user.xp),
            "sub": "Total",
            "icon": "Zap",
            "delta": f"+{fmt(xp_week)}",
        },
        {
            "key": "done",
            "label": "Projets terminés",
            "value": str(user.projects_done),
            "sub": f"sur {n_projects}",
            "icon": "CheckCircle2",
            "delta": f"+{done_week}",
        },
        {
            "key": "cp",
            "label": "Correction Points",
            "value": fmt(user.correction_points),
            "sub": f"+{cp_week} cette sem.",
            "icon": "Users",
            "delta": f"+{cp_week}",
        },
        {
            "key": "wallet",
            "label": "Valeur de compte",
            "value": fmt(user.account_value),
            "sub": f"{user.jetons} jetons",
            "icon": "Coins",
            "delta": f"+{fmt(xp_week)}",
        },
    ]


@router.get("/activity")
def activity(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    events = _events(db, user, limit=5)
    return [activity_payload(e) for e in events]


@router.get("/weekly")
def weekly(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    events = _events(db, user, since=now() - timedelta(days=7))
    return weekly_payload(events)
