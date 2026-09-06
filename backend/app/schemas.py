"""Pydantic request schemas (responses are plain dicts mirroring the
frontend's `data/mock.js` shapes — the contract defined in
frontend/src/services/api.js)."""

from pydantic import BaseModel, EmailStr


class OtpIn(BaseModel):
    email: EmailStr


class VerifyIn(BaseModel):
    email: EmailStr
    code: str


class RegisterIn(BaseModel):
    full_name: str
    email: EmailStr
    campus: str = "Tunis"
    level: str = "some"  # none | some | good
    terms: bool = False


class FileIn(BaseModel):
    path: str
    content: str = ""


class SubmitIn(BaseModel):
    files: list[FileIn] = []
