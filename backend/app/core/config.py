"""Application configuration.

Settings are loaded from environment variables and, when present, from a
``.env`` file (repo root or ``backend/`` — never committed to Git).

Security contract (do not weaken):
    * ``development`` boots with a clearly-labelled insecure ``SECRET_KEY`` so
      a fresh checkout runs out of the box (local testing only).
    * ``production`` refuses to start unless:
        - ``SECRET_KEY`` is set, >= 32 chars, and not the dev placeholder;
        - ``DATABASE_URL`` points at PostgreSQL (SQLite is dev-only).
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

#: URL prefixes accepted as production-grade databases.
PRODUCTION_DB_PREFIXES = ("postgresql://", "postgresql+psycopg2://", "postgres://")


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

    #: Database / cache. SQLite default is for local development ONLY —
    #: production refuses to boot on it. Compose injects PostgreSQL + Redis.
    DATABASE_URL: str = "sqlite:///./root404.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    #: Comma-separated list of browser origins allowed by the CORS policy.
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:4173,http://localhost:8080"
    )

    #: ── Abuse protection ────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_LOGIN_PER_WINDOW: int = 10
    RATE_LIMIT_REGISTER_PER_WINDOW: int = 10
    RATE_LIMIT_SUBMIT_PER_WINDOW: int = 30

    #: Maximum accepted JSON request body (bytes). Submissions are code
    #: strings; 1 MiB is generous and protects against accidental abuse.
    MAX_BODY_BYTES: int = 1_048_576

    #: Insert the demo project catalogue on startup (idempotent). Keep enabled
    #: in production for the first boot; harmless afterwards.
    SEED_DEMO_DATA: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @model_validator(mode="after")
    def _enforce_production_security(self) -> "Settings":
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
        if not self.DATABASE_URL.startswith(PRODUCTION_DB_PREFIXES):
            raise RuntimeError(
                "Refusing to start: ENVIRONMENT=production requires a "
                "PostgreSQL DATABASE_URL (SQLite is a development-only "
                f"convenience, got: {self.DATABASE_URL.split('@')[-1][:40]}...)."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (safe to import anywhere)."""
    return Settings()
