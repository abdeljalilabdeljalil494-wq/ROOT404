"""SQLAlchemy ORM models (Object-Oriented data architecture, per README).

Core MVP tables: Coalition, User, Project, UserProject, Submission,
ActivityEvent, OtpCode. Tables for rooms / corrections / coalitions-wars are
added in the following roadmap steps.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core.db import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Coalition(Base):
    __tablename__ = "coalitions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("c"))
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    color: Mapped[str] = mapped_column(String, default="#3B9EFF")
    points: Mapped[int] = mapped_column(Integer, default=0)
    members: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    trend: Mapped[str] = mapped_column(String, default="+0")
    motto: Mapped[str] = mapped_column(String, default="")

    users: Mapped[list["User"]] = relationship(back_populates="coalition")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("u"))
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)

    display_name: Mapped[str] = mapped_column(String, default="")
    full_name: Mapped[str] = mapped_column(String, default="")
    title: Mapped[str] = mapped_column(String, default="Coder")
    campus: Mapped[str] = mapped_column(String, default="Tunis")
    avatar: Mapped[str] = mapped_column(String, default="")
    bio: Mapped[str] = mapped_column(String, default="")
    languages: Mapped[str] = mapped_column(String, default="FR")

    # Socials (flat columns → same shape as the frontend `socials` object)
    github: Mapped[str] = mapped_column(String, default="")
    discord: Mapped[str] = mapped_column(String, default="")
    site: Mapped[str] = mapped_column(String, default="")

    # Progression / gamification
    level: Mapped[float] = mapped_column(Float, default=0.0)
    level_progress: Mapped[int] = mapped_column(Integer, default=0)  # % toward next integer level
    xp: Mapped[int] = mapped_column(Integer, default=0)
    xp_to_next: Mapped[int] = mapped_column(Integer, default=500)
    projects_done: Mapped[int] = mapped_column(Integer, default=0)
    correction_points: Mapped[int] = mapped_column(Integer, default=0)
    account_value: Mapped[int] = mapped_column(Integer, default=0)
    jetons: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[int] = mapped_column(Integer, default=0)
    reputation: Mapped[int] = mapped_column(Integer, default=100)
    integrity: Mapped[int] = mapped_column(Integer, default=100)

    # Black Hole — survival timer
    blackhole_days_left: Mapped[int] = mapped_column(Integer, default=120)
    blackhole_total: Mapped[int] = mapped_column(Integer, default=120)

    joined: Mapped[str] = mapped_column(String, default="2026")
    status: Mapped[str] = mapped_column(String, default="student")  # student | piscine
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    coalition_id: Mapped[str | None] = mapped_column(
        ForeignKey("coalitions.id", ondelete="SET NULL"), nullable=True
    )
    coalition: Mapped["Coalition | None"] = relationship(back_populates="users")

    user_projects: Mapped[list["UserProject"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activity: Mapped[list["ActivityEvent"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    ai_messages: Mapped[list["AiMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
    """A cursus project (subject). One row per subject on the platform."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    level_label: Mapped[str] = mapped_column(String, default="Niveau 1")
    lang: Mapped[str] = mapped_column(String, default="C")
    lang_color: Mapped[str] = mapped_column(String, default="#3B9EFF")
    description: Mapped[str] = mapped_column(String, default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    xp: Mapped[int] = mapped_column(Integer, default=500)
    duration: Mapped[str] = mapped_column(String, default="1 sem.")
    difficulty: Mapped[int] = mapped_column(Integer, default=3)
    requires: Mapped[str | None] = mapped_column(String, nullable=True)  # slug of prerequisite
    order: Mapped[int] = mapped_column(Integer, default=0)

    user_projects: Mapped[list["UserProject"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class UserProject(Base):
    """A student's state on a project (status, score, progress, retry lock)."""

    __tablename__ = "user_projects"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_user_project"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("up"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)

    status: Mapped[str] = mapped_column(String, default="progress")  # done | progress | failed
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bonus: Mapped[bool] = mapped_column(Boolean, default=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    retry_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    user: Mapped["User"] = relationship(back_populates="user_projects")
    project: Mapped["Project"] = relationship(back_populates="user_projects")


class Submission(Base):
    """A submitted code package, awaiting the Judge / Moulinette (next step)."""

    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("s"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    files: Mapped[list] = mapped_column(JSON, default=list)  # [{path, content}]
    status: Mapped[str] = mapped_column(String, default="pending")  # pending | running | passed | failed
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests: Mapped[list] = mapped_column(JSON, default=list)   # moulinette rows
    terminal: Mapped[list] = mapped_column(JSON, default=list)  # terminal lines
    via: Mapped[str] = mapped_column(String, default="local")  # docker | local
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)

    user: Mapped["User"] = relationship(back_populates="submissions")


class ActivityEvent(Base):
    """Timeline feed + source of truth for weekly activity / dashboard deltas."""

    __tablename__ = "activity_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("a"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project: Mapped[str] = mapped_column(String, default="")  # project slug
    kind: Mapped[str] = mapped_column(String, default="")
    score: Mapped[str] = mapped_column(String, default="")
    tone: Mapped[str] = mapped_column(String, default="ok")  # ok | brand | danger | muted
    xp: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)

    user: Mapped["User"] = relationship(back_populates="activity")


class PeerSlot(Base):
    """A peer-correction slot: a student (who passed the moulinette) is
    corrected by a reviewer of equal or higher level.

    Status flow: open → reserved → done | cancelled.
    """

    __tablename__ = "peer_slots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("pr"))
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reviewer_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    status: Mapped[str] = mapped_column(String, default="open")  # open | reserved | done | cancelled
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str] = mapped_column(String, default="")
    match_pct: Mapped[int] = mapped_column(Integer, default=80)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    student: Mapped["User"] = relationship(foreign_keys=[student_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewer_id])
    project: Mapped["Project"] = relationship()


class AiMessage(Base):
    """AI Mentor conversation line (single thread per student)."""

    __tablename__ = "ai_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("ai"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String, default="user")  # user | ai
    text: Mapped[str] = mapped_column(String, default="")
    extra: Mapped[dict] = mapped_column(JSON, default=dict)  # {list?, footer?, chips?}
    project: Mapped[str | None] = mapped_column(String, nullable=True)  # slug du contexte
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)

    user: Mapped["User"] = relationship(back_populates="ai_messages")


class OtpCode(Base):
    """Single-use e-mail OTP, stored hashed with a short TTL."""

    __tablename__ = "otp_codes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("otp"))
    email: Mapped[str] = mapped_column(String, index=True)
    code_hash: Mapped[str] = mapped_column(String)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
