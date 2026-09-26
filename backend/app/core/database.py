"""
Database configuration and session management.
"""
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()


def sqlite_file_path(database_url: str) -> Optional[Path]:
    """The file a SQLite URL names, or ``None`` when it names no file.

    In-memory databases (``sqlite://``, ``:memory:``, ``mode=memory``) have no
    file, and ``file:`` URIs are left to SQLite to interpret, so neither gets a
    directory. The path stays relative exactly as the URL gives it, so it
    resolves against the working directory as SQLite itself resolves it.
    """
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        return None
    database = url.database
    if not database or database == ":memory:" or database.startswith("file:"):
        return None
    if url.query.get("mode") == "memory":
        return None
    return Path(database)


def create_app_engine(database_url: str) -> Engine:
    """The engine for ``database_url``, able to start from a clean clone.

    ``data/processed`` is ignored by git, so a fresh checkout has no directory
    for the default database and SQLite refuses to open the file. The directory
    of the configured file - and nothing else - is created at the moment of
    the first connection, not at import, so merely importing the app changes
    nothing on disk.
    """
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # Needed for SQLite
    )

    path = sqlite_file_path(database_url)
    if path is not None:
        @event.listens_for(engine, "do_connect")
        def _create_database_directory(dialect, connection_record, cargs, cparams):
            path.parent.mkdir(parents=True, exist_ok=True)

    return engine


engine = create_app_engine(settings.database_url)

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
