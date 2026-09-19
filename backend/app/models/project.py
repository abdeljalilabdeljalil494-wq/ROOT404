"""Project and Submission ORM models (README Phase 1 scope)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    #: easy | medium | hard (validated at schema level)
    difficulty: Mapped[str] = mapped_column(String(16), default="easy")
    xp_reward: Mapped[int] = mapped_column(Integer, default=100)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_submissions_project_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    #: python | c | cpp (validated at schema level)
    language: Mapped[str] = mapped_column(String(16))
    code: Mapped[str] = mapped_column(Text)
    #: pending | passed | failed — the moulinette/judge engine sets this later
    status: Mapped[str] = mapped_column(String(16), default="pending")
    score: Mapped[int | None] = mapped_column(Integer, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    project: Mapped[Project] = relationship(back_populates="submissions")
