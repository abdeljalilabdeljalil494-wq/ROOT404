from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api.router import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (simple)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log audit for sensitive actions
    if request.url.path.startswith("/api/") and request.method in ["POST", "PUT", "DELETE"]:
        logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s - {request.client.host if request.client else 'unknown'}")
    
    return response

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.PROJECT_NAME else "Unknown"}
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Root endpoints
@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs": "/api/docs",
        "health": "/api/health",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok", "version": settings.VERSION}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL[:30]}...")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    
    # Initialize DB
    try:
        init_db()
        logger.info("Database initialized")
        
        # Seed default data
        from app.core.database import SessionLocal
        from app.models.coalition import Coalition
        from app.services.coalition import CoalitionService
        
        db = SessionLocal()
        try:
            CoalitionService.seed_default_coalitions(db)
            
            # Seed projects if empty
            from app.models.project import Project
            if db.query(Project).count() == 0:
                logger.info("Seeding default projects...")
                # Call seed endpoint logic
                from app.api.projects import seed_projects
                # Manually seed
                default_projects = [
                    {"slug": "get_next_line", "name": "get_next_line", "description": "Lis une ligne depuis un file descriptor, sans jamais perdre le fil.", "level": "Niveau 1", "level_value": 1.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "I/O", "Buffer"], "xp": 1200, "duration": "1 sem.", "difficulty": 2, "status_default": "done"},
                    {"slug": "ft_printf", "name": "ft_printf", "description": "Recode la fonction variadique la plus utilisée de la libc.", "level": "Niveau 2", "level_value": 2.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Variadic", "Parsing"], "xp": 1500, "duration": "2 sem.", "difficulty": 3, "status_default": "done"},
                    {"slug": "minishell", "name": "minishell", "description": "Écris ton propre shell : parsing, pipes, redirections, builtins et signaux.", "level": "Niveau 4", "level_value": 4.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Unix", "Parsing"], "xp": 3200, "duration": "4 sem.", "difficulty": 5, "status_default": "progress"},
                    {"slug": "philosophers", "name": "philosophers", "description": "Résous le problème des philosophes avec threads et mutex, sans data race.", "level": "Niveau 3", "level_value": 3.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Solo", "Threads", "Concurrence"], "xp": 2100, "duration": "2 sem.", "difficulty": 4, "status_default": "available"},
                    {"slug": "netpractice", "name": "netpractice", "description": "Configure des réseaux TCP/IP et comprends enfin le masque de sous-réseau.", "level": "Niveau 4", "level_value": 4.2, "lang": "Réseau", "lang_color": "#2ECC71", "tags": ["Solo", "Réseau"], "xp": 1100, "duration": "3 j.", "difficulty": 2, "status_default": "done"},
                    {"slug": "cub3d", "name": "cub3d", "description": "Un moteur de rendu 3D en raycasting, inspiré du légendaire Wolfenstein 3D.", "level": "Niveau 5", "level_value": 5.0, "lang": "C", "lang_color": "#3B9EFF", "tags": ["Duo", "Graphique", "Maths"], "xp": 3600, "duration": "4 sem.", "difficulty": 5, "status_default": "available"},
                    {"slug": "webserv", "name": "webserv", "description": "Implémente un serveur HTTP/1.1 conforme, non-bloquant, façon NGINX.", "level": "Niveau 6", "level_value": 6.0, "lang": "C++", "lang_color": "#F26FA4", "tags": ["Trio", "Réseau", "HTTP"], "xp": 4200, "duration": "5 sem.", "difficulty": 5, "status_default": "locked", "requires": "minishell"},
                    {"slug": "inception", "name": "inception", "description": "Orchestre une infrastructure multi-conteneurs avec Docker Compose.", "level": "Niveau 6", "level_value": 6.5, "lang": "Docker", "lang_color": "#3B9EFF", "tags": ["Solo", "DevOps", "Docker"], "xp": 2800, "duration": "3 sem.", "difficulty": 4, "status_default": "locked", "requires": "webserv"},
                    {"slug": "ft_transcendence", "name": "ft_transcendence", "description": "Le projet final : une SPA temps réel avec un Pong multijoueur en ligne.", "level": "Niveau 8", "level_value": 8.0, "lang": "Web", "lang_color": "#F5B942", "tags": ["Groupe", "Fullstack", "WebSocket"], "xp": 8000, "duration": "8 sem.", "difficulty": 5, "status_default": "locked", "requires": "inception"},
                ]
                for data in default_projects:
                    if not db.query(Project).filter(Project.slug == data["slug"]).first():
                        p = Project(**data)
                        db.add(p)
                db.commit()
                logger.info("Projects seeded")
            
            # Seed demo user if empty
            from app.models.user import User
            from app.services.skill_graph import SkillGraphService
            if db.query(User).count() == 0:
                logger.info("Seeding demo user...")
                demo = User(
                    username="abdeljalil",
                    email="abdeljalil@root404.tn",
                    display_name="Abdeljalil",
                    full_name="Abdeljalil Ben Youssef",
                    campus="Tunis",
                    level=6.42,
                    xp=24780,
                    xp_to_next=3220,
                    projects_done=38,
                    correction_points=1250,
                    account_value=2450,
                    jetons=4,
                    streak=24,
                    accuracy=81,
                    reputation=88,
                    integrity_score=96,
                    bio="Étudiant en systèmes & réseaux. J'aime le C, les pointeurs et les segfaults à 3h du matin.",
                    is_active=True,
                    is_verified=True,
                    skills=SkillGraphService.initialize_skills()
                )
                db.add(demo)
                db.commit()
                # Assign coalition
                try:
                    CoalitionService.assign_user_to_coalition(demo, db)
                except:
                    pass
                logger.info("Demo user seeded")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ROOT 404 API")

# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
