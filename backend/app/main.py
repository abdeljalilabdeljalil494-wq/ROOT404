"""FastAPI entrypoint.

Run locally (from ``backend/`` with the virtualenv active):

    uvicorn app.main:app --reload --port 8000

Startup (lifespan): schema creation (dev convenience) + idempotent seeding.
Production deployments should manage schema with migrations once they land —
see README "Database & migrations".
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.routes import auth, health, projects
from app.core.config import get_settings
from app.core.db import Base, SessionLocal, engine
from app.core.middleware import BodySizeLimitMiddleware, SecurityHeadersMiddleware
from app.core.rate_limit import RateLimitMiddleware, RateRule, SlidingWindowRateLimiter
from app.services.seed import seed_projects

logger = logging.getLogger("root404")


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    if settings.SEED_DEMO_DATA:
        with SessionLocal() as db:
            try:
                seed_projects(db)
            except Exception:  # noqa: BLE001 — a broken DB must fail loudly
                logger.exception("Startup seeding failed")
                raise
    yield


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        summary="42-inspired peer-learning platform for Tunisia.",
        docs_url=f"{settings.API_PREFIX}/docs",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (order matters: last added runs first) ────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(BodySizeLimitMiddleware, max_body_bytes=settings.MAX_BODY_BYTES)
    application.add_middleware(SecurityHeadersMiddleware)
    if settings.RATE_LIMIT_ENABLED:
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limiter = SlidingWindowRateLimiter()
        application.state.rate_limiter = limiter  # tests reset this per test
        application.add_middleware(
            RateLimitMiddleware,
            rules=[
                RateRule(f"{settings.API_PREFIX}/auth/login", "login", settings.RATE_LIMIT_LOGIN_PER_WINDOW, window),
                RateRule(f"{settings.API_PREFIX}/auth/register", "register", settings.RATE_LIMIT_REGISTER_PER_WINDOW, window),
                RateRule(f"{settings.API_PREFIX}/projects", "submit", settings.RATE_LIMIT_SUBMIT_PER_WINDOW, window,
                         suffix="/submissions", method="POST"),
            ],
            limiter=limiter,
        )

    # ── Routers ──────────────────────────────────────────────────────────────
    application.include_router(health.router, prefix=settings.API_PREFIX)
    application.include_router(auth.router, prefix=settings.API_PREFIX)
    application.include_router(projects.router, prefix=settings.API_PREFIX)

    # ── Errors: never leak stack traces to clients ───────────────────────────
    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})

    return application


app = create_application()
