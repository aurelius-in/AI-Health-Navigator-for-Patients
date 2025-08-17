"""
Database session management for AI Health Navigator.

This module handles database connections, session creation, and connection pooling.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from ..core.config import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    return settings.database.url


def create_database_engine():
    """Create SQLAlchemy engine with connection pooling."""
    global _engine
    
    if _engine is not None:
        return _engine
    
    database_url = get_database_url()
    
    # Engine configuration for production
    engine_kwargs = {
        "poolclass": QueuePool,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "echo": False,  # Set to True for SQL query logging
    }
    
    # Add SSL configuration for production databases
    if "postgresql" in database_url and "localhost" not in database_url:
        engine_kwargs["connect_args"] = {
            "sslmode": "require"
        }
    
    try:
        _engine = create_engine(database_url, **engine_kwargs)
        logger.info("Database engine created successfully")
        return _engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_database_engine():
    """Get the database engine, creating it if necessary."""
    global _engine
    
    if _engine is None:
        _engine = create_database_engine()
    
    return _engine


def create_session_factory():
    """Create SQLAlchemy session factory."""
    global _SessionLocal
    
    if _SessionLocal is not None:
        return _SessionLocal
    
    engine = get_database_engine()
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    logger.info("Database session factory created successfully")
    return _SessionLocal


def get_session_factory():
    """Get the session factory, creating it if necessary."""
    global _SessionLocal
    
    if _SessionLocal is None:
        _SessionLocal = create_session_factory()
    
    return _SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    This is a dependency function for FastAPI that provides a database session.
    The session is automatically closed when the request is complete.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session_context() as session:
            # Use session here
            pass
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseSession:
    """Database session manager class."""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        SessionLocal = get_session_factory()
        self.session = SessionLocal()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


def init_database():
    """Initialize database tables."""
    from .models import Base
    
    engine = get_database_engine()
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        with get_db_session_context() as session:
            session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def close_database_connections():
    """Close all database connections."""
    global _engine
    
    if _engine is not None:
        _engine.dispose()
        logger.info("Database connections closed")
