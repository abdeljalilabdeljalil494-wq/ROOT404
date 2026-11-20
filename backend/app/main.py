from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import time
import logging
import os
import threading
import asyncio

from app.core.config import settings, get_safe_database_url
from app.core.database import init_db
from app.api.router import api_router

# Configure logging with security considerations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from app.core.logging import install_secret_filters
install_secret_filters()
logger = logging.getLogger(__name__)

# Security: Don't log sensitive data
if settings.ENVIRONMENT == "production":
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} in {settings.ENVIRONMENT} mode")
    logger.info(f"Database: {get_safe_database_url()}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        if not settings.SEED_DEMO_DATA:
            yield
            return
        # Seed default data
        from app.core.database import SessionLocal
        from app.services.coalition import CoalitionService
        
        db = SessionLocal()
        try:
            CoalitionService.seed_default_coalitions(db)
            
            from app.models.project import Project
            if db.query(Project).count() == 0:
                logger.info("Seeding default projects...")
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
                try:
                    CoalitionService.assign_user_to_coalition(demo, db)
                except Exception as e:
                    logger.warning(f"Failed to assign coalition to demo user: {e}")
                logger.info("Demo user seeded")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}", exc_info=True)
        if settings.ENVIRONMENT == "production":
            raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ROOT 404 API")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION + f"\n\nEnvironment: {settings.ENVIRONMENT}",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    if settings.ENABLE_SECURITY_HEADERS:
        # Prevent XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (only in production with HTTPS)
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Don't expose server info
        response.headers["Server"] = "ROOT404"
    
    return response

# Request size limiting and logging middleware
_body_slots = threading.BoundedSemaphore(8)
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Enforce actual streamed bytes, not only a caller-supplied Content-Length.
    content_length = request.headers.get("content-length")
    if content_length and (not content_length.isdecimal() or int(content_length) > 10 * 1024 * 1024):
        return JSONResponse(status_code=413 if content_length.isdecimal() else 400,
                            content={"detail": "Invalid or oversized request body"})
    body_slot = False
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if not _body_slots.acquire(blocking=False):
            return JSONResponse(status_code=429, content={"detail": "Upload capacity reached"}, headers={"Retry-After":"2"})
        body_slot = True
        try:
            body = bytearray()
            async with asyncio.timeout(10):
                async for chunk in request.stream():
                    if len(body) + len(chunk) > 10 * 1024 * 1024:
                        _body_slots.release()
                        body_slot = False
                        return JSONResponse(status_code=413, content={"detail":"Request body exceeds10MiB"})
                    body.extend(chunk)
            request._body = bytes(body)
            del body
        except TimeoutError:
            _body_slots.release()
            body_slot = False
            return JSONResponse(status_code=408, content={"detail":"Request body timed out"})
        except BaseException:
            _body_slots.release()
            raise

    # Uvicorn applies explicitly trusted proxy processing; never trust raw headers
    # a second time for security/audit identity.
    client_ip = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error for {request.method} {request.url.path} from {client_ip}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    finally:
        if body_slot:
            _body_slots.release()

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Request-ID"] = os.urandom(8).hex()
    
    # Audit log for sensitive actions
    if request.url.path.startswith("/api/") and request.method in ["POST", "PUT", "DELETE"]:
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s - {client_ip}")
    
    return response

# CORS - Strict configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Request-ID"],
    max_age=600,
)

# Exception handlers with security
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Don't leak internal details
    detail = exc.detail
    if exc.status_code == 500 and settings.ENVIRONMENT == "production":
        detail = "Internal server error"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail, "status": exc.status_code},
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Sanitize validation errors to prevent info leakage
    errors = []
    for err in exc.errors():
        # Remove potentially sensitive info
        safe_err = {
            "type": err.get("type"),
            "loc": err.get("loc"),
            "msg": err.get("msg")
        }
        errors.append(safe_err)
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors, "message": "Validation error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    
    # Don't leak details in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)[:200]}
        )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Root endpoints
@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs" if settings.ENVIRONMENT != "production" else "Disabled in production",
        "health": "/api/health",
        "status": "running"
    }

@app.get("/health", tags=["Root"])
def health():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }

@app.get("/ready", tags=["Root"])
def ready():
    from app.core.database import check_db_health
    from app.core.cache import check_redis_health
    database_ok = check_db_health()
    redis_ok = check_redis_health()
    healthy = database_ok and redis_ok is not False
    return JSONResponse(status_code=200 if healthy else 503,
        content={"status": "ready" if healthy else "unavailable", "database": "ok" if database_ok else "unavailable",
                 "redis": "not_configured" if redis_ok is None else "ok" if redis_ok else "unavailable"})

# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT != "production",
        log_level="info"
    )
