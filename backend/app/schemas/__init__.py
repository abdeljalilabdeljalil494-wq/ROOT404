"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import MAX_PASSWORD_BYTES

#: Languages accepted by the submission endpoint (judge engine expands this).
ALLOWED_LANGUAGES = ("python", "c", "cpp")

#: Maximum submitted source-code size, in characters.
MAX_CODE_CHARS = 100_000


# ── Auth / users ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def reject_overlong_password(cls, value: str) -> str:
        # bcrypt silently truncates at 72 bytes — fail loudly instead.
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(
                f"Password must be at most {MAX_PASSWORD_BYTES} bytes (UTF-8)."
            )
        return value


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


# ── Projects / submissions ───────────────────────────────────────────────────

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    difficulty: str
    xp_reward: int
    is_published: bool


class SubmissionCreate(BaseModel):
    language: str = Field(pattern=r"^(python|c|cpp)$")
    code: str = Field(min_length=1, max_length=MAX_CODE_CHARS)


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    language: str
    status: str
    score: int | None
    created_at: datetime
