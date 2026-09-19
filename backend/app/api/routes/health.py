"""Liveness/readiness endpoint used by Docker health checks and monitoring."""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def read_health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
