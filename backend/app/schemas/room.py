from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RoomCreate(BaseModel):
    name: str
    type: str = "study"
    project: Optional[str] = None
    capacity: int = 10
    tags: List[str] = []
    is_private: bool = False

class RoomResponse(BaseModel):
    id: str
    name: str
    type: str
    project: Optional[str] = None
    members: int
    capacity: int
    live: bool
    host: str
    tags: List[str]
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    type: str = "text"

class MessageResponse(BaseModel):
    id: str
    user: str
    avatar: Optional[str] = None
    time: str
    text: str
    me: bool = False
    
    class Config:
        from_attributes = True
