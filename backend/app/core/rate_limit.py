"""In-process sliding-window rate limiting for sensitive endpoints.

Design notes:
    * Buckets are keyed by ``(rule name, client IP)`` with a fixed window.
    * The limiter is per-process: correct for the single-container deployment
      this repo ships. Horizontal scaling needs a shared store (Redis) — this
      is documented in README "Security limitations" as a production TODO.
    * Enabled rules are configured from Settings; tests can build an app with
      tiny limits to exercise 429 behaviour deterministically.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


@dataclass(frozen=True)
class RateRule:
    #: Path prefix this rule guards (e.g. ``/api/auth/login``).
    prefix: str
    #: Stable rule name, used in the bucket key.
    name: str
    limit: int
    window_seconds: int
    #: Optional path suffix for precise targeting
    #: (e.g. prefix=/api/projects + suffix=/submissions).
    suffix: str | None = None
    #: Optional HTTP method restriction (e.g. only POST).
    method: str | None = None


class _WindowBucket:
    __slots__ = ("hits", "lock")

    def __init__(self) -> None:
        self.hits: deque[float] = deque()
        self.lock = threading.Lock()


class SlidingWindowRateLimiter:
    """Thread-safe fixed-window counter per bucket key."""

    def __init__(self) -> None:
        self._buckets: dict[str, _WindowBucket] = defaultdict(_WindowBucket)

    def reset(self) -> None:
        """Clear all buckets (used by tests to isolate per-test state)."""
        with threading.Lock():
            self._buckets.clear()

    def hit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """Record one hit. Returns ``(allowed, retry_after_seconds)``."""
        now = time.monotonic()
        bucket = self._buckets[key]
        with bucket.lock:
            window_start = now - window_seconds
            while bucket.hits and bucket.hits[0] <= window_start:
                bucket.hits.popleft()
            if len(bucket.hits) >= limit:
                retry_after = max(1, int(bucket.hits[0] + window_seconds - now) + 1)
                return False, retry_after
            bucket.hits.append(now)
            return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply :class:`RateRule`s to incoming requests by path prefix."""

    def __init__(self, app, rules: list[RateRule], limiter: SlidingWindowRateLimiter | None = None):
        super().__init__(app)
        # Longest prefix first so the most specific rule wins.
        self.rules = sorted(rules, key=lambda r: len(r.prefix), reverse=True)
        self.limiter = limiter or SlidingWindowRateLimiter()

    async def dispatch(self, request: Request, call_next) -> Response:
        rule = next(
            (
                r
                for r in self.rules
                if request.url.path.startswith(r.prefix)
                and (r.suffix is None or request.url.path.endswith(r.suffix))
                and (r.method is None or request.method == r.method)
            ),
            None,
        )
        if rule is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = self.limiter.hit(
            f"{rule.name}:{client_ip}", rule.limit, rule.window_seconds
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down and try again later."},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)
