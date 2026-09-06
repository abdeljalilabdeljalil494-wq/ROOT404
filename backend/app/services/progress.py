"""XP / Level engine (0.00 → 21.00, 42-style).

Formula: level = xp / XP_PER_LEVEL (continuous, capped at 21.00).
XP_PER_LEVEL = 3860 makes the seeded demo student land exactly on
level 6.42 / 42 % / 2240 XP remaining — consistent with the UI.
"""

from datetime import timedelta

from .serializers import now

XP_PER_LEVEL = 3860
MAX_LEVEL = 21.0
PASS_SCORE = 95  # Moulinette pass threshold (and no failed test row)


def recompute_level(user) -> None:
    user.level = min(MAX_LEVEL, round(user.xp / XP_PER_LEVEL, 2))
    remainder = user.xp % XP_PER_LEVEL
    user.level_progress = int(remainder / XP_PER_LEVEL * 100)
    user.xp_to_next = XP_PER_LEVEL - remainder


def apply_judge_result(db, user, project, up, score: int, passed: bool) -> None:
    """Update the user's project state + activity feed after a judge run.
    XP is awarded once, on the first passing run of a project."""
    first_pass = passed and (up is None or up.status != "done")

    if passed:
        if first_pass:
            user.xp += project.xp
            user.projects_done += 1
            user.account_value += project.xp // 10
            user.jetons += 1
            user.streak += 1 if user.streak == 0 else 0
        db.add(_upsert(up, user, project, status="done", score=score))
        db.add(_event(user, project.slug, "Moulinette réussie", str(score), "ok",
                      project.xp if first_pass else 0))
    else:
        _upsert(up, user, project, status="failed", score=score,
                retry_after=now() + timedelta(days=2))
        db.add(_event(user, project.slug, "Moulinette échouée", str(score), "danger", 0))


def _upsert(up, user, project, *, status: str, score: int, retry_after=None):
    from .. import models

    if up is None:
        up = models.UserProject(user_id=user.id, project_id=project.id)
    up.status = status
    up.score = score
    up.progress = 100 if status == "done" else up.progress
    up.retry_after = retry_after
    return up


def _event(user, slug, kind, score, tone, xp):
    from .. import models

    return models.ActivityEvent(
        user_id=user.id, project=slug, kind=kind, score=score,
        tone=tone, xp=xp,
    )
