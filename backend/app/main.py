"""ROOT 404 — FastAPI entrypoint.

Phase 1 — Core MVP (steps 1-2):
    POST /api/auth/otp            send e-mail OTP
    POST /api/auth/verify         verify OTP → JWT
    POST /api/auth/register       Piscine application
    GET  /api/auth/me             current user
    POST /api/auth/logout         drop session (stateless JWT)

    GET  /api/projects            per-user project list
    GET  /api/projects/{slug}     project detail
    POST /api/projects/{slug}/submit   queue a submission + background Judge
    GET  /api/projects/{slug}/template   workspace sample code
    GET  /api/projects/{slug}/last-result   latest judge result

    GET  /api/dashboard/stats     KPI tiles
    GET  /api/dashboard/activity  recent timeline
    GET  /api/dashboard/weekly    last 7 days

    POST /api/judge/run           workspace « Exécuter » (compile + run)
    POST /api/judge/moulinette/{slug}   full Moulinette (tests + score + XP)

    GET  /api/peer-review         mes slots / slots dispo / historique / stats
    POST /api/peer-review/slot    ouvrir un créneau (moulinette OK requise)
    POST /api/peer-review/{id}/reserve   me proposer comme correcteur
    POST /api/peer-review/{id}/cancel    annuler un créneau
    POST /api/peer-review/{id}/complete  valider la correction (note + CP)

Sandbox: hybrid executor — Docker Ubuntu containers when Docker is
available, restricted local subprocess (CPU/RAM/disk caps) otherwise.
Rooms, AI mentor, leaderboard & analytics endpoints land in the following
steps — the frontend keeps serving mock data for them meanwhile.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, dashboard, judge, peer, projects
from .core.config import settings
from .core.db import Base, engine
from .services.seed import seed_if_empty

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("root404")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Zero-migration dev flow: create tables + seed the demo dataset if empty.
    # (Alembic migrations are introduced together with the Judge step.)
    Base.metadata.create_all(bind=engine)
    if seed_if_empty():
        log.info("Seed data loaded (first run).")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="École 1337 — TounsiCoder-AI backend (Phase 1 Core MVP).",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if _origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",  # dev: the preview host changes on every run
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

api = APIRouter(prefix="/api")
api.include_router(auth.router, prefix="/auth", tags=["auth"])
api.include_router(projects.router, prefix="/projects", tags=["projects"])
api.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api.include_router(judge.router, prefix="/judge", tags=["judge"])
api.include_router(peer.router, prefix="/peer-review", tags=["peer-review"])
app.include_router(api)


@app.get("/api/health", tags=["meta"])
def health():
    return {
        "status": "ok",
        "service": "root404-api",
        "version": settings.app_version,
        "debug": settings.debug,
    }


@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "api": "/api",
        "health": "/api/health",
    }
