"""Peer Review endpoints (slot lifecycle).

    GET  /peer-review                 {upcoming, available, history, stats}
    POST /peer-review/slot            {project, when?}   → ouvre un slot (moulinette OK requise)
    POST /peer-review/{id}/reserve    → je me propose comme correcteur
    POST /peer-review/{id}/cancel     → j'annule un slot où je participe
    POST /peer-review/{id}/complete   {score, comment?}  → je termine la correction
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..schemas import ReviewIn, SlotIn
from ..services import peer as peer_svc

router = APIRouter()


def _get_slot(db: Session, slot_id: str) -> models.PeerSlot:
    slot = db.get(models.PeerSlot, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Créneau introuvable.")
    return slot


@router.get("")
def list_slots(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return peer_svc.list_payload(db, user)


@router.post("/slot")
def create_slot(
    body: SlotIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.execute(
        select(models.Project).where(models.Project.slug == body.project)
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail=f"Projet inconnu : {body.project}")

    up = db.execute(
        select(models.UserProject).where(
            models.UserProject.user_id == user.id,
            models.UserProject.project_id == project.id,
        )
    ).scalar_one_or_none()
    if up is None or up.status != "done":
        raise HTTPException(
            status_code=400,
            detail=f"Valide d'abord la Moulinette sur « {project.name} » avant d'ouvrir un créneau.",
        )

    existing = db.execute(
        select(models.PeerSlot).where(
            models.PeerSlot.student_id == user.id,
            models.PeerSlot.project_id == project.id,
            models.PeerSlot.status.in_(("open", "reserved")),
        )
    ).scalars().first()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Tu as déjà un créneau ouvert pour ce projet.",
        )

    if body.when:
        try:
            scheduled = datetime.fromisoformat(body.when)
        except ValueError:
            raise HTTPException(status_code=400, detail="Date invalide (format ISO attendu).")
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
    else:
        scheduled = datetime.now(timezone.utc) + timedelta(hours=1)

    slot = models.PeerSlot(
        student_id=user.id,
        project_id=project.id,
        scheduled_at=scheduled,
        status="open",
    )
    db.add(slot)
    db.add(models.ActivityEvent(
        user_id=user.id, project=project.slug,
        kind="Créneau de correction ouvert", score="—", tone="brand", xp=0,
    ))
    db.commit()
    return {"ok": True, "id": slot.id, "status": slot.status}


@router.post("/{slot_id}/reserve")
def reserve_slot(
    slot_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = _get_slot(db, slot_id)
    if slot.status != "open":
        raise HTTPException(status_code=409, detail="Ce créneau n'est plus disponible.")
    if not peer_svc.can_review(user, slot.student):
        raise HTTPException(
            status_code=400,
            detail="Ton niveau doit être ≥ au niveau de l'étudiant pour le corriger.",
        )
    slot.reviewer_id = user.id
    slot.status = "reserved"
    slot.match_pct = peer_svc.match_pct(user, slot.student)
    db.add(models.ActivityEvent(
        user_id=user.id, project=slot.project.slug,
        kind="Correction réservée", score="—", tone="brand", xp=0,
    ))
    db.add(models.ActivityEvent(
        user_id=slot.student.id, project=slot.project.slug,
        kind="Correcteur trouvé", score="—", tone="ok", xp=0,
    ))
    db.commit()
    return {"ok": True, "id": slot.id, "status": slot.status}


@router.post("/{slot_id}/cancel")
def cancel_slot(
    slot_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = _get_slot(db, slot_id)
    if slot.status not in ("open", "reserved"):
        raise HTTPException(status_code=409, detail="Impossible d'annuler ce créneau.")
    if slot.student_id != user.id and slot.reviewer_id != user.id:
        raise HTTPException(status_code=403, detail="Ce créneau ne te concerne pas.")
    slot.status = "cancelled"
    if slot.reviewer_id == user.id:  # le correcteur se retire
        slot.reviewer_id = None
        slot.status = "open"
    db.add(models.ActivityEvent(
        user_id=user.id, project=slot.project.slug,
        kind="Créneau annulé", score="—", tone="muted", xp=0,
    ))
    db.commit()
    return {"ok": True, "id": slot.id, "status": slot.status}


@router.post("/{slot_id}/complete")
def complete_slot(
    slot_id: str,
    body: ReviewIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = _get_slot(db, slot_id)
    if slot.status != "reserved" or slot.reviewer_id != user.id:
        raise HTTPException(
            status_code=403, detail="Seul le correcteur du créneau peut valider la correction."
        )
    if not 0 <= body.score <= 100:
        raise HTTPException(status_code=400, detail="La note doit être entre 0 et 100.")
    result = peer_svc.apply_review(db, slot, body.score, body.comment)
    db.commit()
    return result
