"""Tests for the JWT helpers in app.core.security."""
from __future__ import annotations

import pytest
import jwt

from app.core.config import Settings, DEV_INSECURE_SECRET_KEY
from app.core.security import ALGORITHM, create_access_token, decode_access_token


@pytest.fixture()
def dev_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Deterministic development settings for token tests."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    return Settings(_env_file=None)


def test_token_roundtrip(dev_settings: Settings) -> None:
    token = create_access_token("student-42")
    payload = decode_access_token(token)
    assert payload["sub"] == "student-42"
    assert payload["exp"] > payload["iat"]


def test_expired_token_is_rejected(dev_settings: Settings) -> None:
    token = create_access_token("student-42", expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_token_signed_with_other_key_is_rejected(
    dev_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    token = create_access_token("student-42")
    # A verifier with a different (strong) secret must not accept the token.
    wrong_key = "another-secret-key-that-is-long-enough-for-hs256"
    assert len(wrong_key) >= 32
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, wrong_key, algorithms=[ALGORITHM])


def test_production_rejects_short_secret() -> None:
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="too-short")


def test_production_rejects_dev_placeholder_secret() -> None:
    with pytest.raises(RuntimeError, match="placeholder"):
        Settings(
            _env_file=None, ENVIRONMENT="production", SECRET_KEY=DEV_INSECURE_SECRET_KEY
        )


def test_production_accepts_strong_secret() -> None:
    settings = Settings(
        _env_file=None, ENVIRONMENT="production", SECRET_KEY="s" * 48
    )
    assert settings.is_production
