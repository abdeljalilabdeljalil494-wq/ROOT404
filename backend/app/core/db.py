import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

# SQLite is the zero-setup default; PostgreSQL works unchanged via DATABASE_URL.
is_sqlite = settings.database_url.startswith("sqlite")
if is_sqlite:
    # Make sure the directory for the SQLite file exists.
    path = settings.database_url.split("///")[-1]
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency yielding a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
