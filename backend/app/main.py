"""FastAPI entrypoint.

Run locally (from ``backend/`` with the virtualenv active):

    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import health
from app.core.config import get_settings


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        summary="42-inspired peer-learning platform for Tunisia.",
        docs_url=f"{settings.API_PREFIX}/docs",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health.router, prefix=settings.API_PREFIX)

    return application


app = create_application()
