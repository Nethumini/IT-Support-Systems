"""
Database configuration and session management.
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logger = logging.getLogger(__name__)


def init_db():
    """Initialize database tables.

    ``create_all`` builds tables that do not exist yet, but never alters one
    that does - so a column added to a shipped table is applied separately.
    Both steps are idempotent, so this is safe on every start.
    """
    Base.metadata.create_all(bind=engine)

    try:
        from migrations import apply_schema_migrations

        added = apply_schema_migrations()
        if added:
            logger.info("Applied schema migrations: %s", ", ".join(added))
    except Exception as exc:
        # A migration failure must be loud but must not stop the app starting;
        # the queries that need the new column will fail visibly instead.
        logger.error("Schema migration failed: %s", exc)
