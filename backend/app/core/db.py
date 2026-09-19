"""SQLAlchemy engine/session management.

* ``engine`` is created once from ``Settings.DATABASE_URL``.
* SQLite (development convenience) gets ``check_same_thread=False`` for
  FastAPI's threadpool. Production runs PostgreSQL via Compose.
* ``get_db`` is the FastAPI dependency that guarantees the session is always
  closed; callers commit, and ``rollback`` happens automatically on error via
  the session context semantics (see ``session_scope`` for non-request code).
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _build_engine():
    settings = get_settings()
    connect_args = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False
    return create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # drop dead connections (e.g. after DB restart)
    )


engine = _build_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — always closes the session, even on exceptions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
