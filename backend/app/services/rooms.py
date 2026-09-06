"""Collaboration Rooms — listing, membership, chat.

Modèle :
- `Room.base_members` = effectif de base non modélisé (grosse room live) ;
- les vrais joins sont des lignes `RoomMember` (rôle host / member /
  observer) — un join déborde en « observer » si la room est pleine ;
- `RoomMessage` : chat persisté par room (le flag `me` est calculé à la
  sérialisation, jamais stocké).
"""

from sqlalchemy import select

from .. import models

ROOM_TYPES = ("study", "correction", "pair", "competition", "mentor", "live")


def room_payload(room: models.Room) -> dict:
    """Shape = mock.rooms (members = base + joins réels, hors observers)."""
    joins = [m for m in room.members if m.role in ("host", "member")]
    return {
        "id": room.id,
        "name": room.name,
        "type": room.type,
        "project": room.project,
        "members": room.base_members + len(joins),
        "capacity": room.capacity,
        "live": room.live,
        "host": room.host,
        "tags": room.tags or [],
    }


def list_rooms(db) -> list[dict]:
    rooms = db.execute(select(models.Room).order_by(models.Room.created_at.desc())).scalars().all()
    return [room_payload(r) for r in rooms]


def _get_room(db, room_id: str) -> models.Room:
    room = db.get(models.Room, room_id)
    if room is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Room introuvable : {room_id}")
    return room


def detail_payload(db, room: models.Room, me: models.User) -> dict:
    rows = db.execute(
        select(models.RoomMember).where(models.RoomMember.room_id == room.id)
    ).scalars().all()
    members = [
        {
            "name": m.user.username,
            "avatar": m.user.avatar,
            "status": m.status,
            "role": {"host": "Hôte", "member": m.role.title(), "observer": "Observateur"}.get(
                m.role, m.role
            ),
            "me": m.user_id == me.id,
        }
        for m in rows
    ]
    is_member = any(m.user_id == me.id and m.role in ("host", "member") for m in rows)
    return {"room": room_payload(room), "members": members, "isMember": is_member}


def messages_payload(db, room: models.Room, me: models.User, limit: int = 100) -> list[dict]:
    rows = db.execute(
        select(models.RoomMessage)
        .where(models.RoomMessage.room_id == room.id)
        .order_by(models.RoomMessage.created_at.desc())
        .limit(limit)
    ).scalars().all()
    out = []
    for m in reversed(rows):
        out.append({
            "id": m.id,
            "user": m.user.username,
            "avatar": m.user.avatar,
            "time": m.created_at.astimezone().strftime("%H:%M"),
            "text": m.text,
            "me": m.user_id == me.id,
        })
    return out


def join_room(db, room: models.Room, user: models.User) -> dict:
    existing = db.execute(
        select(models.RoomMember).where(
            models.RoomMember.room_id == room.id,
            models.RoomMember.user_id == user.id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Tu es déjà dans cette room.")
    joins = [m for m in room.members if m.role in ("host", "member")]
    full = room.base_members + len(joins) >= room.capacity
    db.add(models.RoomMember(
        room_id=room.id, user_id=user.id,
        role="observer" if full else "member", status="online",
    ))
    db.commit()
    db.expire(room, ["members"])  # recharger la collection (sinon comptage pré-join)
    return room_payload(room)


def send_message(db, room: models.Room, user: models.User, text: str) -> dict:
    msg = models.RoomMessage(room_id=room.id, user_id=user.id, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "user": user.username,
        "avatar": user.avatar,
        "time": msg.created_at.astimezone().strftime("%H:%M"),
        "text": msg.text,
        "me": True,
    }


def create_room(db, user: models.User, name: str, rtype: str, project: str,
                capacity: int, live: bool) -> dict:
    room = models.Room(
        name=name, type=rtype, project=project,
        capacity=max(2, int(capacity)), live=live,
        host=user.username,
    )
    db.add(room)
    db.flush()
    db.add(models.RoomMember(
        room_id=room.id, user_id=user.id, role="host", status="online",
    ))
    db.add(models.ActivityEvent(
        user_id=user.id, project=project or rtype,
        kind=f"Room créée — {name}", score="—", tone="brand", xp=0,
    ))
    db.commit()
    db.refresh(room)
    return room_payload(room)
