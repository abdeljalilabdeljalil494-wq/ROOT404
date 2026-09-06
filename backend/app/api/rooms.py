"""Collaboration Rooms endpoints.

    GET  /rooms                  → [room…] (shape = mock.rooms)
    POST /rooms                  {name, type, project?, capacity?} → je crée une room
    GET  /rooms/{id}             → {room, members, isMember}
    GET  /rooms/{id}/messages    → [message…] (flag `me` calculé)
    POST /rooms/{id}/messages    {text} → message persisté
    POST /rooms/{id}/join        → je rejoins (observer si pleine)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..core.db import get_db
from ..core.security import get_current_user
from ..schemas import RoomCreateIn, RoomMessageIn
from ..services import rooms as rooms_svc

router = APIRouter()


@router.get("")
def list_rooms(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return rooms_svc.list_rooms(db)


@router.post("")
def create_room(
    body: RoomCreateIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nom de room vide.")
    if body.type not in rooms_svc.ROOM_TYPES:
        raise HTTPException(status_code=400, detail=f"Type inconnu : {body.type}")
    if body.capacity < 2 or body.capacity > 500:
        raise HTTPException(status_code=400, detail="Capacité entre 2 et 500.")
    return rooms_svc.create_room(
        db, user, name, body.type, body.project.strip(), body.capacity, body.live
    )


@router.get("/{room_id}")
def room_detail(
    room_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = rooms_svc._get_room(db, room_id)
    return rooms_svc.detail_payload(db, room, user)


@router.get("/{room_id}/messages")
def room_messages(
    room_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = rooms_svc._get_room(db, room_id)
    return rooms_svc.messages_payload(db, room, user)


@router.post("/{room_id}/messages")
def room_send(
    room_id: str,
    body: RoomMessageIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message vide.")
    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Message trop long (2000 caractères max).")
    room = rooms_svc._get_room(db, room_id)
    return rooms_svc.send_message(db, room, user, text)


@router.post("/{room_id}/join")
def room_join(
    room_id: str,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    room = rooms_svc._get_room(db, room_id)
    return rooms_svc.join_room(db, room, user)
