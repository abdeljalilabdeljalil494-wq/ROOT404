from pydantic import BaseModel, EmailStr
from typing import Optional

class OtpRequest(BaseModel):
    email: EmailStr

class OtpVerify(BaseModel):
    email: EmailStr
    code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    full_name: Optional[str] = None
    campus: Optional[str] = "Tunis"
    password: Optional[str] = None  # Optional for OTP flow

class UserResponse(BaseModel):
    id: str
    username: str
    displayName: str
    email: str
    level: float
    xp: int
    campus: str
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True
