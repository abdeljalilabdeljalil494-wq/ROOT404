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
    slug: str | None = None  # used by /judge/run (workspace « Exécuter »)
    note: str | None = None


class SlotIn(BaseModel):
    project: str  # project slug
    when: str | None = None  # ISO datetime (scheduled slot); default: +1 h


class ReviewIn(BaseModel):
    score: int  # 0..100 — note du correcteur
    comment: str = ""


class AskIn(BaseModel):
    message: str
    level: int = 2  # 1..5 — niveau d'assistance
