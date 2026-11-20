"""Redis connectivity check. Authentication state intentionally lives in SQL."""
from .config import settings


def check_redis_health():
    if not settings.REDIS_URL:
        return None
    from redis import Redis
    try:
        with Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2) as client:
            return bool(client.ping())
    except Exception:
        # Never include the connection URL/credentials in a log or response.
        return False
