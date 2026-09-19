"""Application configuration.

Settings are loaded from environment variables and, when present, from a
``.env`` file (repo root or ``backend/`` — never committed to Git).

Security contract:
    * In ``development`` a clearly-labelled insecure default ``SECRET_KEY`` is
      allowed so the app boots on a fresh checkout (local testing only).
    * In ``production`` the app refuses to start unless ``SECRET_KEY`` is set
      to a strong (>= 32 chars) non-default value. This is deliberate and must
      not be weakened.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Placeholder used when no SECRET_KEY is configured (development only).
DEV_INSECURE_SECRET_KEY = "dev-only-INSECURE-secret-key-DO-NOT-USE-in-production"

#: Minimum accepted length of SECRET_KEY in production.
PRODUCTION_MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "ROOT 404 — École 1337 API"
    ENVIRONMENT: Literal["development", "production"] = "development"

    #: All API routes are mounted under this prefix (e.g. ``/api/health``).
    API_PREFIX: str = "/api"

    #: Cryptographic secret for token signing. Required (strong) in production.
    SECRET_KEY: str = DEV_INSECURE_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    #: Comma-separated list of browser origins allowed by the CORS policy.
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:4173,http://localhost:8080"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @model_validator(mode="after")
    def _enforce_production_secret(self) -> "Settings":
        """Fail fast at startup when production security rules are violated."""
        if not self.is_production:
            return self

        if self.SECRET_KEY == DEV_INSECURE_SECRET_KEY:
            raise RuntimeError(
                "Refusing to start: ENVIRONMENT=production but SECRET_KEY is "
                "still the insecure development placeholder. Generate a strong "
                'key, e.g.: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if len(self.SECRET_KEY) < PRODUCTION_MIN_SECRET_KEY_LENGTH:
            raise RuntimeError(
                "Refusing to start: ENVIRONMENT=production requires a SECRET_KEY "
                f"of at least {PRODUCTION_MIN_SECRET_KEY_LENGTH} characters "
                f"(got {len(self.SECRET_KEY)})."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (safe to import anywhere)."""
    return Settings()
