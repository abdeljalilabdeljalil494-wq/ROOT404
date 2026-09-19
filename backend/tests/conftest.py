"""Pytest configuration for the ROOT 404 backend test suite.

Isolation contract:
    * Environment is pinned BEFORE any ``app`` import (this file is imported
      first by pytest), so ``app.core.db.engine`` never touches a developer or
      production database.
    * Each test gets a fresh **in-memory SQLite** database via ``StaticPool``
      and the ``get_db`` dependency is overridden — tests cannot see or modify
      anything outside their own database.
    * Redis is never required: the health endpoint tolerates its absence.
"""
from __future__ import annotations

import os
import tempfile

import pytest

# ── Pin test environment BEFORE app imports ──────────────────────────────────
_TEST_DIR = tempfile.mkdtemp(prefix="root404-tests-")
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "unit-test-secret-key-not-used-in-any-real-env"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DIR}/unused-lifespan.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["RATE_LIMIT_ENABLED"] = "true"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.db import Base, get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app as main_app  # noqa: E402
from app.models import User  # noqa: E402
from app.services.seed import seed_projects  # noqa: E402


@pytest.fixture(autouse=True)
def _fast_bcrypt(monkeypatch: pytest.MonkeyPatch):
    """Speed up tests: bcrypt cost 4 instead of 12 (never affects runtime code
    outside this process)."""
    from app.core import security as security_module

    monkeypatch.setattr(security_module, "BCRYPT_ROUNDS", 4)


@pytest.fixture()
def db_engine():
    """Fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Session bound to the per-test engine (already seeded like app startup)."""
    TestSession = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)
    session = TestSession()
    seed_projects(session)
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    """TestClient wired to the per-test database via the get_db override."""

    def _override():
        yield db_session
        # mirror get_db semantics: commit on success, rollback on error
        try:
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    main_app.dependency_overrides[get_db] = _override
    limiter = getattr(main_app.state, "rate_limiter", None)
    if limiter is not None:
        limiter.reset()  # fresh rate-limit buckets per test
    test_client = TestClient(main_app)
    yield test_client
    main_app.dependency_overrides.clear()


# ── Factories ────────────────────────────────────────────────────────────────

def make_user(
    db_session,
    email: str = "amine@example.tn",
    username: str = "amine",
    password: str = "S3cure-passw0rd!",
    *,
    is_active: bool = True,
) -> User:
    user = User(
        email=email.lower(),
        username=username,
        hashed_password=hash_password(password),
        is_active=is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def login_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
