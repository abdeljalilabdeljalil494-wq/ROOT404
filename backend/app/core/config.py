from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
import secrets
import warnings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ROOT 404 API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Elite Coder Platform — École 1337 / TounsiCoder-AI"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    # Security - MUST be overridden in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_PER_HOUR: int = 5  # Max OTP requests per email per hour
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./root404.db")
    
    # CORS - Strict in production
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:4173").split(",") if os.getenv("CORS_ORIGINS") else ["http://localhost:5173", "http://localhost:3000", "http://localhost:4173"]
    
    # Sandbox
    JUDGE_ENABLED: bool = os.getenv("JUDGE_ENABLED", "false").lower() == "true"
    JUDGE_TIMEOUT: int = 30
    JUDGE_MEMORY_LIMIT: str = "512m"
    JUDGE_CPU_LIMIT: float = 1.0
    JUDGE_NETWORK_DISABLED: bool = True
    JUDGE_MAX_FILE_SIZE: int = 1024 * 1024  # 1MB per file
    JUDGE_MAX_FILES: int = 20
    JUDGE_MAX_TOTAL_SIZE: int = 5 * 1024 * 1024  # 5MB total
    
    # AI Mentor
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
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
    url = settings.DATABASE_URL
    if "@" in url and "://" in url:
        # Mask password
        try:
            prefix = url.split("://")[0] + "://"
            rest = url.split("://")[1]
            if "@" in rest:
                creds, host = rest.split("@", 1)
                if ":" in creds:
                    user, _ = creds.split(":", 1)
                    return f"{prefix}{user}:****@{host}"
            return url
        except:
            return "***masked***"
    return url
