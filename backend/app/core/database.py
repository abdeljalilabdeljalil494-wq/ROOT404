from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError
import logging
from .config import settings, get_safe_database_url

logger = logging.getLogger(__name__)

# Security: Configure engine with secure defaults
connect_args = {}
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,  # Verify connections before use
}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Use StaticPool for in-memory, QueuePool for file-based with limits
    if ":memory:" in settings.DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = connect_args
    else:
        engine_kwargs["connect_args"] = connect_args
        engine_kwargs["poolclass"] = QueuePool
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_timeout"] = 30
        engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour
    
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    
    # Security: Enable WAL mode and foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.close()
        except Exception as e:
            logger.warning(f"Failed to set SQLite pragmas: {e}")
else:
    # Postgres with secure pooling
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": settings.PROJECT_NAME,
        }
    })
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency with proper error handling and cleanup"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except Exception as e:
            logger.warning(f"Error closing DB session: {e}")

def init_db():
    """Initialize database with all models, with error handling"""
    try:
        # Import all models to register them
        from app.models import user, project, submission, correction, room, coalition  # noqa
        from app.models import DailyMission, Badge, UserBadge, AuditLog, ArenaMatch, PiscineDay, UserPiscineProgress  # noqa
        
        logger.info(f"Initializing database: {get_safe_database_url()}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing database: {e}", exc_info=True)
        raise

def check_db_health() -> bool:
    """Check database connectivity"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
