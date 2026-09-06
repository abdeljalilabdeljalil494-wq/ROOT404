from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Every field can be overridden via environment
    variables (case-insensitive) or a local `.env` file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ROOT 404 API"
    app_version: str = "0.1.0"

    # Dev mode: returns the generated OTP code inside /auth/otp responses so the
    # demo works without a real mail provider. MUST be false in production.
    debug: bool = True

    # SQLite out of the box; PostgreSQL in production via DATABASE_URL.
    database_url: str = "sqlite:///./data/root404.db"

    jwt_secret: str = "dev-only-change-me-424242-root404-secret"  # ≥32 bytes for HS256
    jwt_algorithm: str = "HS256"
    jwt_expires_days: int = 7

    otp_ttl_minutes: int = 10
    otp_resend_seconds: int = 60

    cors_origins: str = "*"


settings = Settings()
