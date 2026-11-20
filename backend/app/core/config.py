from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import field_validator
from functools import lru_cache
from typing import List, Annotated
import os
import secrets
import warnings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ROOT 404 API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Elite Coder Platform — École 1337 / TounsiCoder-AI"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    MENTOR_RETENTION_DAYS: int = 30
    SUBMISSION_RETENTION_DAYS: int = 90
    MESSAGE_RETENTION_DAYS: int = 90
    NOTIFICATION_RETENTION_DAYS: int = 90
    AUDIT_RETENTION_DAYS: int = 90

    # Security - MUST be overridden in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENABLE_DEV_OTP: bool = False
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_PER_HOUR: int = 5  # Max OTP requests per email per hour
    
    EMAIL_PROVIDER: str = "development"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_SSL: bool = False
    SEED_DEMO_DATA: bool = False
    ENABLE_DEMO_FEATURES: bool = False
    JUDGE_URL: str = ""
    JUDGE_SHARED_SECRET: str = ""

    REDIS_URL: str = ""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./root404.db")
    
    # CORS - Strict in production
    CORS_ORIGINS: Annotated[List[str], NoDecode] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:4173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            import json
            return json.loads(value) if value.lstrip().startswith("[") else [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    
    # Explicit fixed provider credentials; redirect targets are operator-configured.
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = ""

    # Sandbox
    JUDGE_CA_FILE: str = ""
    JUDGE_EXPECTED_IMAGE: str = ""
    JUDGE_ENABLED: bool = os.getenv("JUDGE_ENABLED", "false").lower() == "true"
    JUDGE_TIMEOUT: int = 30
    JUDGE_MEMORY_LIMIT: str = "512m"
    JUDGE_CPU_LIMIT: float = 1.0
    JUDGE_NETWORK_DISABLED: bool = True
    JUDGE_MAX_FILE_SIZE: int = 1024 * 1024  # 1MB per file
    JUDGE_MAX_FILES: int = 20
    JUDGE_MAX_TOTAL_SIZE: int = 5 * 1024 * 1024  # 5MB total
    
    # AI Mentor
    AI_PROVIDER: str = "disabled"
    AI_MODEL: str = "gpt-4o-mini"
    AI_REQUESTS_PER_HOUR: int = 30
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_AUTH_REQUESTS: int = 10  # Stricter for auth endpoints
    RATE_LIMIT_AUTH_WINDOW: int = 60
    RATE_LIMIT_JUDGE_REQUESTS: int = 20
    RATE_LIMIT_JUDGE_WINDOW: int = 60
    
    # Security headers
    ENABLE_SECURITY_HEADERS: bool = True
    
    # Black Hole
    BLACKHOLE_CHECK_INTERVAL: int = 3600
    BLACKHOLE_WARNING_DAYS: int = 7
    
    # Campus
    DEFAULT_CAMPUS: str = "Tunis"
    CAMPUSES: List[str] = ["Tunis", "Sfax", "Sousse", "Ariana"]
    
    # Input validation
    MAX_USERNAME_LENGTH: int = 30
    MIN_USERNAME_LENGTH: int = 3
    MAX_EMAIL_LENGTH: int = 254
    MAX_BIO_LENGTH: int = 1000
    MAX_PROJECT_NAME_LENGTH: int = 100
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generate secure secret if not provided in dev, require in prod
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                raise ValueError("SECRET_KEY must be set in production environment!")
            else:
                # Generate a random secret for dev, but warn
                self.SECRET_KEY = secrets.token_urlsafe(64)
                warnings.warn("SECRET_KEY not set, using generated random key for development. Set SECRET_KEY env var for production!")
        
        # Validate secret key strength in production
        if self.ENVIRONMENT == "production" and len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production!")
        
        if self.ENVIRONMENT != "development" and self.ENABLE_DEV_OTP:
            raise ValueError("ENABLE_DEV_OTP is permitted only in development")

        if self.ENVIRONMENT == "production":
            if self.EMAIL_PROVIDER != "smtp" or not self.SMTP_HOST or not self.SMTP_FROM:
                raise ValueError("Production requires configured SMTP email delivery")
            if self.SEED_DEMO_DATA or self.ENABLE_DEMO_FEATURES:
                raise ValueError("Demo seeding is forbidden in production")
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("Production requires PostgreSQL")
            if self.JUDGE_ENABLED and (not self.JUDGE_URL.startswith("https://") or len(self.JUDGE_SHARED_SECRET) < 48):
                raise ValueError("Enabled production judge requires HTTPS and a >=48 character shared secret")
            if self.JUDGE_ENABLED:
                import re
                if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}',self.JUDGE_EXPECTED_IMAGE):
                    raise ValueError('Enabled production judge requires an approved immutable JUDGE_EXPECTED_IMAGE')

        # Optional OAuth stays disabled if absent; partial/unsafe production
        # configuration must fail startup rather than advertise a broken provider.
        if self.ENVIRONMENT == "production":
            from urllib.parse import urlsplit
            for provider in ("GOOGLE", "GITHUB"):
                values=[getattr(self,provider+"_"+suffix) for suffix in ("CLIENT_ID","CLIENT_SECRET","REDIRECT_URI")]
                if any(values):
                    uri=urlsplit(values[2])
                    if not all(values) or uri.scheme!="https" or not uri.hostname or uri.username or uri.password or uri.query or uri.fragment or uri.path!="/oauth/callback/"+provider.lower():
                        raise ValueError("Complete HTTPS OAuth configuration required for "+provider)

        # Validate CORS in production
        if self.ENVIRONMENT == "production":
            if "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS cannot contain '*' in production!")
            if not self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS must be set in production!")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Security: ensure no secrets in logs
def get_safe_database_url() -> str:
    # Log only backend kind. Credentials can appear in userinfo, query or path;
    # no connection-string component is needed for operational diagnostics.
    from urllib.parse import urlsplit
    try:
        scheme = urlsplit(settings.DATABASE_URL).scheme
        return scheme if scheme in {"postgresql", "postgresql+psycopg", "sqlite"} else "database"
    except ValueError:
        return "database"
