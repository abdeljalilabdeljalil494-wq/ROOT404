"""Health/readiness endpoint: application + database + Redis components.

Response contract:
    * database unreachable            -> 503 {"status": "unhealthy"}
    * database ok, Redis unreachable  -> 200 {"status": "degraded"}
    * all components ok               -> 200 {"status": "ok"}

Docker/Compose health checks and monitoring should key off ``status`` and the
HTTP status code.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db

router = APIRouter(tags=["health"])


def _check_database(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 — any DB failure must not leak details
        return False


def _check_redis() -> bool:
    try:
        import redis as redis_lib

        client = redis_lib.Redis.from_url(
            get_settings().REDIS_URL,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        try:
            return bool(client.ping())
        finally:
            client.close()
    except Exception:  # noqa: BLE001 — Redis is optional in dev
        return False


@router.get("/health")
def read_health(response: Response, db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    db_ok = _check_database(db)
    redis_ok = _check_redis()

    components = {
        "database": "ok" if db_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
    }
    if not db_ok:
        response.status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE
        overall = "unhealthy"
    elif not redis_ok:
        response.status_code = http_status.HTTP_200_OK
        overall = "degraded"
    else:
        response.status_code = http_status.HTTP_200_OK
        overall = "ok"

    return {
        "status": overall,
        "components": components,
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
