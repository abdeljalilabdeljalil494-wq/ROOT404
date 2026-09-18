"""
Collaboration Rooms Service — Study, Correction, Pair, Competition, Mentor, Live
"""
from sqlalchemy.orm import Session
from app.models.room import Room, RoomMember, RoomMessage
from app.models.user import User
from typing import List, Optional
from datetime import datetime
import uuid

class RoomService:
    @staticmethod
    def create_room(host_id: str, name: str, room_type: str, project: str = None, capacity: int = 10, tags: List[str] = None, db: Session = None) -> Room:
        room = Room(
            name=name,
            type=room_type,
            project=project,
            host_id=host_id,
            capacity=capacity,
            tags=tags or [],
            is_live=True if room_type in ["live", "competition"] else False
        )
        db.add(room)
        db.commit()
        db.refresh(room)
        
        # Add host as member
        member = RoomMember(room_id=room.id, user_id=host_id, role="host")
        db.add(member)
        db.commit()
        
        return room
    
    @staticmethod
    def join_room(room_id: str, user_id: str, db: Session) -> tuple:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            return None, "Room not found"
        
        # Check capacity
        current = db.query(RoomMember).filter(RoomMember.room_id == room_id).count()
        if current >= room.capacity:
            return None, "Room full"
        
        # Check already member
        existing = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        ).first()
        if existing:
            return room, "Already member"
        
        member = RoomMember(room_id=room_id, user_id=user_id, role="member")
        db.add(member)
        db.commit()
        return room, "Joined"
    
    @staticmethod
    def leave_room(room_id: str, user_id: str, db: Session) -> bool:
        member = db.query(RoomMember).filter(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id
        ).first()
        if member:
            db.delete(member)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_room_members(room_id: str, db: Session) -> List[dict]:
        members = db.query(RoomMember).filter(RoomMember.room_id == room_id).all()
        result = []
        for m in members:
            user = db.query(User).filter(User.id == m.user_id).first()
            if user:
                result.append({
                    "id": user.id,
                    "name": user.username,
                    "displayName": user.display_name,
                    "avatar": user.avatar_url,
                    "role": m.role,
                    "status": "online",  # Would be real presence in production
                    "joined_at": m.joined_at.isoformat()
                })
        return result
    
    @staticmethod
    def send_message(room_id: str, user_id: str, content: str, msg_type: str = "text", db: Session = None) -> RoomMessage:
        msg = RoomMessage(
            room_id=room_id,
            user_id=user_id,
            content=content,
            type=msg_type
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    
    @staticmethod
    def get_messages(room_id: str, limit: int = 50, db: Session = None) -> List[dict]:
        messages = db.query(RoomMessage).filter(
            RoomMessage.room_id == room_id
        ).order_by(RoomMessage.created_at.asc()).limit(limit).all()
        
        result = []
        for msg in messages:
            user = db.query(User).filter(User.id == msg.user_id).first()
            result.append({
                "id": msg.id,
                "user": user.username if user else "unknown",
                "avatar": user.avatar_url if user else None,
                "time": msg.created_at.strftime("%H:%M") if msg.created_at else "",
                "text": msg.content,
                "type": msg.type
            })
        return result
    
    @staticmethod
    def list_rooms(room_type: str = None, db: Session = None, limit: int = 100) -> List[dict]:
        query = db.query(Room)
        if room_type:
            query = query.filter(Room.type == room_type)
        rooms = query.order_by(Room.created_at.desc()).limit(limit).all()
        
        result = []
        for r in rooms:
            members_count = db.query(RoomMember).filter(RoomMember.room_id == r.id).count()
            host = db.query(User).filter(User.id == r.host_id).first()
            result.append({
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "project": r.project,
                "members": members_count,
                "capacity": r.capacity,
                "live": r.is_live,
                "host": host.username if host else "system",
                "tags": r.tags or [],
                "created_at": r.created_at.isoformat() if r.created_at else None
            })
        return result
    
    @staticmethod
    def get_room_details(room_id: str, db: Session) -> Optional[dict]:
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            return None
        
        members = RoomService.get_room_members(room_id, db)
        messages = RoomService.get_messages(room_id, 100, db)
        host = db.query(User).filter(User.id == room.host_id).first()
        
        return {
            "id": room.id,
            "name": room.name,
            "type": room.type,
            "project": room.project,
            "capacity": room.capacity,
            "is_live": room.is_live,
            "tags": room.tags,
            "host": {"username": host.username, "displayName": host.display_name} if host else None,
            "members": members,
            "messages": messages,
            "created_at": room.created_at.isoformat() if room.created_at else None
        }
