"""ORM → JSON serializers.

Output shapes intentionally mirror `frontend/src/data/mock.js` so the
frontend needs zero component changes when switching mock → real API.
"""

from datetime import datetime, timezone

DAY_LABELS = {0: "Lun", 1: "Mar", 2: "Mer", 3: "Jeu", 4: "Ven", 5: "Sam", 6: "Dim"}


def now() -> datetime:
    return datetime.now(timezone.utc)


def aware(dt: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes, PostgreSQL aware ones — normalize to
    UTC-aware so comparisons never mix types."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def fmt(n: int) -> str:
    """Thousands formatting matching the mock data (e.g. 24780 → '24,780')."""
    return f"{int(n):,}"


def rel_time(dt: datetime) -> str:
    """Compact French relative time: 'il y a 2 h', 'hier', 'il y a 3 j.' …"""
    dt = aware(dt)
    delta = now() - dt
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "à l'instant"
    if minutes < 60:
        return f"il y a {minutes} min"
    hours = minutes // 60
    if hours < 24:
        return f"il y a {hours} h"
    days = hours // 24
    if days == 1:
        return "hier"
    return f"il y a {days} j."


def user_payload(user, db=None) -> dict:
    """User in the exact shape of mock.currentUser."""
    coalition = None
    if user.coalition is not None:
        rank = coalition_rank(user.coalition, db) if db is not None else 1
        coalition = {
            "name": user.coalition.name,
            "color": user.coalition.color,
            "rank": rank,
            "points": user.coalition.points,
        }
    return {
        "id": user.id,
        "username": user.username,
        "displayName": user.display_name,
        "fullName": user.full_name,
        "title": user.title,
        "campus": user.campus,
        "coalition": coalition,
        "avatar": user.avatar,
        "languages": user.languages,
        "level": round(float(user.level), 2),
        "levelProgress": user.level_progress,
        "xp": user.xp,
        "xpToNext": user.xp_to_next,
        "projectsDone": user.projects_done,
        "correctionPoints": user.correction_points,
        "accountValue": user.account_value,
        "jetons": user.jetons,
        "streak": user.streak,
        "accuracy": user.accuracy,
        "reputation": user.reputation,
        "integrity": user.integrity,
        "blackHole": {"daysLeft": user.blackhole_days_left, "total": user.blackhole_total},
        "joined": user.joined,
        "bio": user.bio,
        "socials": {"github": user.github, "discord": user.discord, "site": user.site},
    }


def coalition_rank(coalition, db) -> int:
    """Rank computed live from coalition points (1 = leader)."""
    from sqlalchemy import func, select

    from .. import models

    q = select(func.count()).select_from(models.Coalition).where(
        models.Coalition.points > coalition.points
    )
    return db.execute(q).scalar_one() + 1


def project_payload(project, up=None, done_slugs: set | None = None) -> dict:
    """Project in the exact shape of mock.projects rows.

    `up` is the user's UserProject row (None → status derived:
    available / locked based on the prerequisite chain).
    """
    if up is not None:
        status = up.status
    else:
        locked = bool(project.requires) and (
            done_slugs is None or project.requires not in done_slugs
        )
        status = "locked" if locked else "available"

    payload = {
        "id": project.id,
        "slug": project.slug,
        "name": project.name,
        "level": project.level_label,
        "lang": project.lang,
        "langColor": project.lang_color,
        "desc": project.description,
        "tags": list(project.tags or []),
        "status": status,
        "xp": project.xp,
        "duration": project.duration,
        "difficulty": project.difficulty,
    }
    if project.requires:
        payload["requires"] = project.requires

    if up is not None:
        if up.score is not None:
            payload["score"] = up.score
        if up.bonus:
            payload["bonus"] = True
        if status == "progress":
            payload["progress"] = up.progress
        if status == "failed" and up.retry_after is not None:
            import math

            secs = (aware(up.retry_after) - now()).total_seconds()
            days = max(1, math.ceil(secs / 86400))
            payload["retryIn"] = f"{days} j."
    return payload


def activity_payload(event) -> dict:
    return {
        "id": int(event.id[-8:]) if event.id[-8:].isdigit() else 0,
        "project": event.project,
        "kind": event.kind,
        "score": event.score,
        "tone": event.tone,
        "time": rel_time(event.created_at),
    }


def weekly_payload(events) -> list[dict]:
    """Last 7 days (Mon-first), value = minutes of code ≈ xp earned / 10."""
    from datetime import timedelta

    today = now().date()
    buckets: dict = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        buckets[day] = 0
    for e in events:
        day = aware(e.created_at).date()
        if day in buckets:
            buckets[day] += e.xp
    return [
        {"day": DAY_LABELS[day.weekday()], "value": round(xp / 10)}
        for day, xp in buckets.items()
    ]
