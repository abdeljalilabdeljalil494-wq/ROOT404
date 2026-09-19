"""Rate limiting, request body limits, and seed idempotency.

The rate-limit and body-size tests build a dedicated app instance with tiny
limits (isolated settings) so they are deterministic and fast.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.db import Base, get_db
from app.main import create_application
from app.models import Project
from app.services.seed import seed_projects
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tests.conftest import make_user


@pytest.fixture()
def hardened_app(monkeypatch, request):
    """App instance with tiny limits: login x2, register x2, submit x2, 512B body."""
    monkeypatch.setenv("RATE_LIMIT_LOGIN_PER_WINDOW", "2")
    monkeypatch.setenv("RATE_LIMIT_REGISTER_PER_WINDOW", "2")
    monkeypatch.setenv("RATE_LIMIT_SUBMIT_PER_WINDOW", "2")
    monkeypatch.setenv("MAX_BODY_BYTES", "512")
    get_settings.cache_clear()
    request.addfinalizer(get_settings.cache_clear)

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestSession()
    seed_projects(session)
    make_user(session, email="rl@example.tn", username="rl")

    application = create_application()

    def _override():
        yield session
        session.commit()

    application.dependency_overrides[get_db] = _override
    yield TestClient(application)
    application.dependency_overrides.clear()
    session.close()
    engine.dispose()


def test_login_rate_limited_returns_429_with_retry_after(hardened_app):
    payload = {"email": "rl@example.tn", "password": "definitely-wrong"}
    assert hardened_app.post("/api/auth/login", json=payload).status_code == 401
    assert hardened_app.post("/api/auth/login", json=payload).status_code == 401
    third = hardened_app.post("/api/auth/login", json=payload)
    assert third.status_code == 429
    assert int(third.headers["Retry-After"]) >= 1
    assert "slow down" in third.json()["detail"].lower()
    #: non-sensitive endpoints are not limited
    assert hardened_app.get("/api/health").status_code in {200, 503}


def test_register_rate_limited(hardened_app):
    for i in range(2):
        response = hardened_app.post(
            "/api/auth/register",
            json={"email": f"rat{i}@example.tn", "username": f"rate{i}", "password": "Str0ng-Pass!"},
        )
        assert response.status_code == 201
    assert (
        hardened_app.post(
            "/api/auth/register",
            json={"email": "ratX@example.tn", "username": "rateX", "password": "Str0ng-Pass!"},
        ).status_code
        == 429
    )


def test_submission_rate_limited(hardened_app):
    login = hardened_app.post(
        "/api/auth/login", json={"email": "rl@example.tn", "password": "S3cure-passw0rd!"}
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    for _ in range(2):
        response = hardened_app.post(
            "/api/projects/libft/submissions",
            json={"language": "python", "code": "print(1)"},
            headers=headers,
        )
        assert response.status_code == 201
    assert (
        hardened_app.post(
            "/api/projects/libft/submissions",
            json={"language": "python", "code": "print(2)"},
            headers=headers,
        ).status_code
        == 429
    )


def test_oversized_request_body_rejected_413(hardened_app):
    big_code = "x" * 1024  # 1 KiB > 512 B cap
    response = hardened_app.post(
        "/api/auth/register",
        json={"email": "big@example.tn", "username": "big", "password": big_code},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_seed_is_idempotent(db_session):
    first_count = db_session.scalar(select(func.count()).select_from(Project))
    created_again = seed_projects(db_session)
    assert created_again == 0, "second seed run must not create duplicates"
    assert db_session.scalar(select(func.count()).select_from(Project)) == first_count


def test_seed_on_empty_database_creates_full_catalogue(db_engine):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        assert seed_projects(session) == 3
        assert seed_projects(session) == 0  # restart simulation
        assert session.scalar(select(func.count()).select_from(Project)) == 3
    engine.dispose()
