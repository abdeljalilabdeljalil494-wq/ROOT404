from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, rate_limit
from app.models.user import User
from app.services.room_service import RoomService

router = APIRouter(prefix="/rooms", tags=["Rooms"])

class CreateRoomRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field("study", pattern="^(study|correction|pair|competition|mentor|live)$")
    project: Optional[str] = Field(None, max_length=100)
    capacity: int = Field(10, ge=1, le=1000)
    tags: List[str] = Field(default_factory=list, max_length=10)
    is_private: bool = False

    @field_validator('name')
    @classmethod
    def nonempty_name(cls, value):
        if not value.strip(): raise ValueError('Room name cannot be empty')
        return value.strip()

    @field_validator('tags')
    @classmethod
    def bounded_tags(cls, tags):
        if any(len(tag)>32 for tag in tags): raise ValueError('Tag too long')
        return tags

class MessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    type: str = Field("text",pattern="^(text|code)$")

@router.get("/")
def list_rooms(type: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return RoomService.list_rooms(type, db)

@router.post("/")
def create_room(payload: CreateRoomRequest, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rate_limit(request,max_requests=10,window=60,key_prefix='room-create:'+current_user.id)
    from app.models.room import Room
    if db.query(Room).filter_by(host_id=current_user.id).count()>=100:
        raise HTTPException(409,'Hosted room quota reached')
    room = RoomService.create_room(
        current_user.id, payload.name, payload.type,
        payload.project, payload.capacity, payload.tags, db, is_private=payload.is_private
    )
    return {
        "id": room.id,
        "name": room.name,
        "type": room.type,
        "project": room.project,
        "capacity": room.capacity,
        "tags": room.tags
    }

def require_membership(room_id: str, user: User, db: Session):
    from app.models.room import RoomMember, Room
    if not db.get(Room, room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    if not db.query(RoomMember).filter_by(room_id=room_id, user_id=user.id).first():
        raise HTTPException(status_code=403, detail="Room membership required")

@router.get("/{room_id}")
def get_room(room_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_membership(room_id, current_user, db)
    details = RoomService.get_room_details(room_id, db)
    if not details:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    for message in details["messages"]:
        message["me"] = message["user"] == current_user.username
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
def get_messages(room_id: str, limit: int = Query(100, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_membership(room_id, current_user, db)
    messages = RoomService.get_messages(room_id, limit, db)
    # Mark own messages
    for m in messages:
        m["me"] = m["user"] == current_user.username
    return messages

@router.post("/{room_id}/messages")
def send_message(room_id: str, payload: MessageRequest, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    require_membership(room_id, current_user, db)
    rate_limit(request,max_requests=60,window=60,key_prefix='room-message:'+current_user.id)
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
    require_membership(room_id, current_user, db)
    return RoomService.get_room_members(room_id, db)

# WebSocket endpoint for real-time would be here
# @router.websocket("/ws/{room_id}")
# async def websocket_endpoint...

@router.post("/seed", dependencies=[Depends(require_admin)])
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
