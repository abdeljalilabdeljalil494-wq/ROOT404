"""Peer Review — smart matchmaking, slots & correction flow.

Rules (à la 42, simplifiées) :
- un slot s'ouvre seulement pour un projet **déjà validé à la moulinette**
  (UserProject.status == "done");
- le correcteur doit avoir un niveau **≥** celui de l'étudiant corrigé;
- au terme de la correction : note ≥ 75 → projet validé (done), sinon le
  projet repasse en "failed" avec une pénalité de 2 jours;
- le correcteur gagne +20 CP et +50 XP, l'étudiant gagne ou perd le projet.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from .. import models

REVIEWER_CP = 20
REVIEWER_XP = 50
PASS_SCORE = 75
RETRY_DAYS = 2

_DAYS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_MONTHS_FR = [
    "janv.", "févr.", "mars", "avril", "mai", "juin",
    "juil.", "août", "sept.", "oct.", "nov.", "déc.",
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def fr_when(dt: datetime) -> str:
    """« Aujourd'hui 16:30 » / « Demain 10:00 » / « jeudi 11 sept. 11:00 »."""
    d = _aware(dt)
    n = now_utc()
    hm = d.strftime("%H:%M")
    if d.date() == n.date():
        return f"Aujourd'hui {hm}"
    if d.date() == (n + timedelta(days=1)).date():
        return f"Demain {hm}"
    return f"{_DAYS_FR[d.weekday()]} {d.day} {_MONTHS_FR[d.month - 1]} {hm}"


def fr_date(dt: datetime) -> str:
    d = _aware(dt)
    return f"{d.day} {_MONTHS_FR[d.month - 1]} {d.year}"


def match_pct(a: models.User, b: models.User) -> int:
    """Affinité 0-100 : proximité de niveau (70 %) + réputation moyenne (30 %)."""
    level_gap = abs(a.level - b.level)
    level_score = max(0.0, 1.0 - level_gap / 3.0)
    rep_score = (a.reputation + b.reputation) / 200.0
    return max(35, min(99, int(round(100 * (0.7 * level_score + 0.3 * rep_score)))))


def can_review(reviewer: models.User, student: models.User) -> bool:
    return reviewer.id != student.id and reviewer.level >= student.level


def _peer_view(u: models.User) -> dict:
    return {
        "username": u.username,
        "displayName": u.display_name,
        "avatar": u.avatar,
        "level": round(float(u.level), 2),
        "languages": u.languages,
        "reputation": u.reputation,
    }


def slot_upcoming_payload(slot: models.PeerSlot, me: models.User) -> dict:
    """Row for « Mes slots » — the peer is whoever is *not* me.
    My own still-open slot has no reviewer yet → peer is None (waiting)."""
    peer = slot.student if slot.reviewer_id == me.id else slot.reviewer
    base = {
        "id": slot.id,
        "project": slot.project.slug,
        "when": fr_when(slot.scheduled_at),
        "role": "Tu corriges" if slot.reviewer_id == me.id else "Tu es corrigé",
        "match": slot.match_pct,
        "status": slot.status,
        "canCancel": slot.status in ("open", "reserved"),
    }
    if peer is None:
        return {**base, "peer": None, "displayName": None, "avatar": "",
                "level": 0, "languages": "", "waiting": True}
    return {
        **base,
        "peer": peer.username,
        "displayName": peer.display_name,
        "avatar": peer.avatar,
        "level": round(float(peer.level), 2),
        "languages": peer.languages,
        "waiting": False,
    }


def slot_available_payload(slot: models.PeerSlot, me: models.User) -> dict:
    """Row for « Slots disponibles » — open slots from other students."""
    s = slot.student
    return {
        "id": slot.id,
        "peer": s.username,
        "displayName": s.display_name,
        "avatar": s.avatar,
        "level": round(float(s.level), 2),
        "languages": s.languages,
        "rep": s.reputation,
        "project": slot.project.slug,
        "when": fr_when(slot.scheduled_at),
        "match": match_pct(me, s),
        "canReserve": can_review(me, s),
    }


def slot_history_payload(slot: models.PeerSlot, me: models.User) -> dict:
    """Row for « Historique » — the peer is the *other* side of the correction."""
    peer = slot.student if slot.reviewer_id == me.id else slot.reviewer
    return {
        "id": slot.id,
        "peer": peer.username,
        "avatar": peer.avatar,
        "project": slot.project.slug,
        "date": fr_date(slot.updated_at or slot.created_at),
        "score": slot.score,
        "given": slot.reviewer_id == me.id,
    }


def list_payload(db, me: models.User) -> dict:
    """Everything the Peer Review page needs in one call."""
    n = now_utc()
    my_slots = db.execute(
        select(models.PeerSlot).where(
            models.PeerSlot.status.in_(("open", "reserved")),
            (models.PeerSlot.student_id == me.id) | (models.PeerSlot.reviewer_id == me.id),
        )
    ).scalars().all()
    upcoming = sorted(my_slots, key=lambda s: _aware(s.scheduled_at))

    available = db.execute(
        select(models.PeerSlot).where(
            models.PeerSlot.status == "open",
            models.PeerSlot.student_id != me.id,
            models.PeerSlot.scheduled_at >= n,
        )
    ).scalars().all()
    available = sorted(available, key=lambda s: match_pct(me, s.student), reverse=True)

    done = db.execute(
        select(models.PeerSlot).where(
            models.PeerSlot.status == "done",
            (models.PeerSlot.student_id == me.id) | (models.PeerSlot.reviewer_id == me.id),
        ).order_by(models.PeerSlot.updated_at.desc())
    ).scalars().all()

    given = sum(1 for s in done if s.reviewer_id == me.id)
    received = len(done) - given
    return {
        "upcoming": [slot_upcoming_payload(s, me) for s in upcoming],
        "available": [slot_available_payload(s, me) for s in available],
        "history": [slot_history_payload(s, me) for s in done],
        "stats": {"given": given, "received": received},
    }


def apply_review(db, slot: models.PeerSlot, score: int, comment: str) -> dict:
    """Close a slot: grade the student's project, reward the reviewer."""
    student, reviewer = slot.student, slot.reviewer
    slot.status = "done"
    slot.score = score
    slot.comment = comment
    slot.updated_at = now_utc()

    # Reviewer reward.
    reviewer.correction_points += REVIEWER_CP
    reviewer.xp += REVIEWER_XP
    reviewer.reputation = min(100, reviewer.reputation + 1)

    # Student outcome on the project.
    up = db.execute(
        select(models.UserProject).where(
            models.UserProject.user_id == student.id,
            models.UserProject.project_id == slot.project_id,
        )
    ).scalar_one_or_none()
    if up is not None:
        if score >= PASS_SCORE:
            if up.status != "done":
                student.projects_done += 1
            up.status = "done"
            up.score = max(up.score or 0, score)
            up.progress = 100
            up.retry_after = None
        else:
            up.status = "failed"
            up.retry_after = now_utc() + timedelta(days=RETRY_DAYS)

    db.add(models.ActivityEvent(
        user_id=reviewer.id, project=slot.project.slug,
        kind="Correction effectuée", score=f"+{REVIEWER_CP} CP", tone="brand", xp=REVIEWER_XP,
    ))
    db.add(models.ActivityEvent(
        user_id=student.id, project=slot.project.slug,
        kind="Peer Review validé" if score >= PASS_SCORE else "Peer Review refusé",
        score=str(score), tone="ok" if score >= PASS_SCORE else "danger",
        xp=0,
    ))
    return {
        "ok": True,
        "score": score,
        "passed": score >= PASS_SCORE,
        "reviewer_cp": REVIEWER_CP,
        "reviewer_xp": REVIEWER_XP,
    }
