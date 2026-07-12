"""
app/database/engine.py

Purpose:
    SQLAlchemy engine, session factory, init_db(), and reset_database().

Reason:
    Centralizes all database connection logic. reset_database() is the
    developer's best friend — one call to nuke and reseed during iteration.
"""

import os
from app.logger import get_logger

log = get_logger(__name__)
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATABASE_URL, DATABASE_PATH
from app.models import Base

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional database session scope."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def reset_database() -> None:
    """
    Nuclear option for development: delete the SQLite file,
    recreate all tables, and reseed with demo data.

    Usage:
        python -c "from app.database import reset_database; reset_database()"
    """
    # Import here to avoid circular import
    from app.database.seed import seed_all

    # Close all connections
    engine.dispose()

    # Drop all tables instead of deleting the file to avoid Windows lock issues
    Base.metadata.drop_all(bind=engine)
    log.info("Dropped all tables")

    # Ensure data directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Recreate engine bindings
    Base.metadata.create_all(bind=engine)
    log.info("All tables recreated")

    # Reseed
    seed_all()
    log.info("Seed data inserted")
    log.info("Database reset complete")
