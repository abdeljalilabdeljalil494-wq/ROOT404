"""Authentication: registration, login, token handling, password hashing."""
from __future__ import annotations

import jwt
import pytest
from sqlalchemy import func, select

from app.core.config import DEV_INSECURE_SECRET_KEY
from app.core.security import (
    MAX_PASSWORD_BYTES,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from tests.conftest import login_headers, make_user


# ── Registration ─────────────────────────────────────────────────────────────

def test_register_success_persists_bcrypt_hash(client, db_session):
    response = client.post(
        "/api/auth/register",
        json={"email": "Yasmine@Example.tn", "username": "yasmine", "password": "Str0ng-Pass!"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "yasmine@example.tn"  # lower-cased
    assert body["username"] == "yasmine"
    assert "password" not in body and "hashed_password" not in body

    user = db_session.scalar(select(User).where(User.email == "yasmine@example.tn"))
    assert user is not None
    assert user.hashed_password != "Str0ng-Pass!"
    assert user.hashed_password.startswith("$2")
    assert verify_password("Str0ng-Pass!", user.hashed_password)


def test_register_duplicate_email_conflict(client):
    payload = {"email": "dupe@example.tn", "username": "first", "password": "Str0ng-Pass!"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    conflict = payload | {"username": "second"}
    response = client.post("/api/auth/register", json=conflict)
    assert response.status_code == 409


def test_register_duplicate_username_conflict(client):
    payload = {"email": "u1@example.tn", "username": "samename", "password": "Str0ng-Pass!"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    conflict = payload | {"email": "u2@example.tn"}
    assert client.post("/api/auth/register", json=conflict).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "not-an-email", "username": "abc", "password": "Str0ng-Pass!"},  # bad email
        {"email": "a@example.tn", "username": "ab", "password": "Str0ng-Pass!"},   # username too short
        {"email": "a@example.tn", "username": "Bad Upper", "password": "Str0ng-Pass!"},  # charset
        {"email": "a@example.tn", "username": "abc", "password": "short"},          # weak password
        {"email": "a@example.tn", "username": "abc", "password": ""},               # empty password
        {"email": "a@example.tn", "username": "abc", "password": "x" * 129},        # > schema max
    ],
)
def test_register_invalid_payloads_rejected(client, db_session, payload):
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    assert db_session.scalar(select(func.count()).select_from(User)) == 0


def test_register_rejects_password_over_bcrypt_72_bytes(client):
    long_password = "x" * 100  # 100 bytes, > bcrypt limit
    response = client.post(
        "/api/auth/register",
        json={"email": "a@example.tn", "username": "abc", "password": long_password},
    )
    assert response.status_code == 422
    detail = response.json()["detail"][0]["msg"].lower()
    assert "72" in detail


# ── Login ────────────────────────────────────────────────────────────────────

def test_login_success_returns_usable_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@example.tn", "username": "loginuser", "password": "Str0ng-Pass!"},
    )
    response = client.post(
        "/api/auth/login", json={"email": "login@example.tn", "password": "Str0ng-Pass!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "loginuser"


def test_login_wrong_password_generic_error(client):
    client.post(
        "/api/auth/register",
        json={"email": "gen@example.tn", "username": "gen", "password": "Str0ng-Pass!"},
    )
    wrong = client.post(
        "/api/auth/login", json={"email": "gen@example.tn", "password": "Wrong-Password!"}
    )
    unknown = client.post(
        "/api/auth/login", json={"email": "ghost@example.tn", "password": "Whatever-123!"}
    )
    assert wrong.status_code == unknown.status_code == 401
    #: identical message -> no account enumeration
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_login_disabled_account_forbidden(client, db_session):
    make_user(db_session, email="off@example.tn", username="off", is_active=False)
    response = client.post(
        "/api/auth/login", json={"email": "off@example.tn", "password": "S3cure-passw0rd!"}
    )
    assert response.status_code == 403


# ── Current user / token handling ────────────────────────────────────────────

def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_garbage_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert response.status_code == 401


def test_me_rejects_expired_token(client):
    expired = create_access_token("12345", expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired)
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_me_rejects_token_signed_with_wrong_key(client):
    forged = jwt.encode(
        {"sub": "1", "exp": 4102444800}, "attacker-key-that-is-long-enough", algorithm="HS256"
    )
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


def test_me_rejects_token_for_deleted_user(client, db_session):
    user = make_user(db_session, email="vanish@example.tn", username="vanish")
    headers = login_headers(client, user.email, "S3cure-passw0rd!")
    db_session.delete(user)
    db_session.commit()
    assert client.get("/api/auth/me", headers=headers).status_code == 401


# ── Password hashing primitives ──────────────────────────────────────────────

def test_hash_password_is_salted_and_verifiable():
    h1, h2 = hash_password("same-password"), hash_password("same-password")
    assert h1 != h2  # unique salts
    assert verify_password("same-password", h1)
    assert not verify_password("different-password", h1)


def test_hash_password_rejects_overlong_input():
    with pytest.raises(ValueError, match="72"):
        hash_password("y" * (MAX_PASSWORD_BYTES + 1))


def test_verify_password_malformed_hash_is_false():
    assert verify_password("whatever", "not-a-bcrypt-hash") is False


# ── Production configuration guard rails ─────────────────────────────────────

def test_production_rejects_dev_placeholder_secret():
    from app.core.config import Settings

    with pytest.raises(RuntimeError, match="placeholder"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=DEV_INSECURE_SECRET_KEY,
                 DATABASE_URL="postgresql://u:p@db:5432/x")


def test_production_rejects_weak_or_short_secret():
    from app.core.config import Settings

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="too-short",
                 DATABASE_URL="postgresql://u:p@db:5432/x")


def test_production_rejects_sqlite_database():
    from app.core.config import Settings

    with pytest.raises(RuntimeError, match="PostgreSQL"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="q" * 48,
                 DATABASE_URL="sqlite:///./prod.db")


def test_production_accepts_strong_config():
    from app.core.config import Settings

    settings = Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="s" * 48,
                        DATABASE_URL="postgresql://u:p@db:5432/root404")
    assert settings.is_production
