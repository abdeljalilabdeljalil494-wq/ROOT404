from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "ROOT 404 API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Elite Coder Platform — École 1337 / TounsiCoder-AI"
    API_V1_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "root404-dev-secret-key-change-in-production-32chars!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    
    # Database - defaults to SQLite for local dev, supports Postgres via DATABASE_URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./root404.db")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Sandbox
    JUDGE_ENABLED: bool = False  # Set True to use real Docker
    JUDGE_TIMEOUT: int = 30
    JUDGE_MEMORY_LIMIT: str = "512m"
    JUDGE_CPU_LIMIT: float = 1.0
    JUDGE_NETWORK_DISABLED: bool = True
    
    # AI Mentor
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")  # mock, openai, etc.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Black Hole
    BLACKHOLE_CHECK_INTERVAL: int = 3600
    BLACKHOLE_WARNING_DAYS: int = 7
    
    # Campus
    DEFAULT_CAMPUS: str = "Tunis"
    CAMPUSES: List[str] = ["Tunis", "Sfax", "Sousse", "Ariana"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
