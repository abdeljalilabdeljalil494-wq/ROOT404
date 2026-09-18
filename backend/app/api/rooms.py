from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])

class CreateRoomRequest(BaseModel):
    name: str
    type: str = "study"
    project: Optional[str] = None
    capacity: int = 10
    tags: List[str] = []
    is_private: bool = False

class MessageRequest(BaseModel):
    content: str
    type: str = "text"

@router.get("/")
def list_rooms(type: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RoomService.list_rooms(type, db)

@router.post("/")
def create_room(payload: CreateRoomRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = RoomService.create_room(
        current_user.id, payload.name, payload.type,
        payload.project, payload.capacity, payload.tags, db
    )
    return {
        "id": room.id,
        "name": room.name,
        "type": room.type,
        "project": room.project,
        "capacity": room.capacity,
        "tags": room.tags
    }

@router.get("/{room_id}")
def get_room(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    details = RoomService.get_room_details(room_id, db)
    if not details:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    return details

@router.post("/{room_id}/join")
def join_room(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    room, msg = RoomService.join_room(room_id, current_user.id, db)
    if not room:
        raise HTTPException(status_code=404, detail=msg)
    return {"ok": True, "message": msg, "room_id": room_id}

@router.post("/{room_id}/leave")
def leave_room(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = RoomService.leave_room(room_id, current_user.id, db)
    return {"ok": ok}

@router.get("/{room_id}/messages")
def get_messages(room_id: str, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = RoomService.get_messages(room_id, limit, db)
    # Mark own messages
    for m in messages:
        m["me"] = m["user"] == current_user.username
    return messages

@router.post("/{room_id}/messages")
def send_message(room_id: str, payload: MessageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = RoomService.send_message(room_id, current_user.id, payload.content, payload.type, db)
    return {
        "id": msg.id,
        "user": current_user.username,
        "text": msg.content,
        "time": msg.created_at.strftime("%H:%M") if msg.created_at else "",
        "me": True
    }

@router.get("/{room_id}/members")
def get_members(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RoomService.get_room_members(room_id, db)

# WebSocket endpoint for real-time would be here
# @router.websocket("/ws/{room_id}")
# async def websocket_endpoint...

@router.post("/seed")
def seed_rooms(db: Session = Depends(get_db)):
    from app.models.room import Room
    from app.models.user import User
    
    # Check if already seeded
    if db.query(Room).count() > 0:
        return {"ok": True, "message": "Already seeded"}
    
    # Create system user if not exists
    system_user = db.query(User).filter(User.username == "system").first()
    if not system_user:
        system_user = User(
            username="system",
            email="system@root404.tn",
            display_name="System",
            campus="Tunis",
            is_active=True
        )
        db.add(system_user)
        db.commit()
    
    rooms_data = [
        {"name": "Correction Room 1", "type": "correction", "project": "minishell", "capacity": 2, "tags": ["C", "Peer Review"]},
        {"name": "Pointeurs & Mémoire", "type": "study", "project": "get_next_line", "capacity": 10, "tags": ["C", "Débutant"]},
        {"name": "Duo cub3d", "type": "pair", "project": "cub3d", "capacity": 2, "tags": ["Raycasting"]},
        {"name": "Coalition War — Sprint 48h", "type": "competition", "project": "Algo Dojo", "capacity": 40, "tags": ["Compétition"]},
        {"name": "Office Hours — Systèmes", "type": "mentor", "project": "Mentorat", "capacity": 20, "tags": ["Mentor", "Level 15+"]},
        {"name": "Live: Build a Web Server", "type": "live", "project": "webserv", "capacity": 500, "tags": ["Stream"]},
    ]
    
    for rd in rooms_data:
        room = Room(
            name=rd["name"],
            type=rd["type"],
            project=rd["project"],
            capacity=rd["capacity"],
            tags=rd["tags"],
            host_id=system_user.id,
            is_live=True
        )
        db.add(room)
    
    db.commit()
    return {"ok": True, "count": len(rooms_data)}
