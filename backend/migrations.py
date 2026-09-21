"""
Database migration tracking system.
Ensures seeds only run once and tracks schema changes.
"""
import os
import sqlite3
from datetime import datetime

MIGRATIONS_TABLE = "migrations"


def get_db_path():
    """Path of the SQLite file the application itself uses.

    Read from DATABASE_URL rather than hardcoded. When the two disagree the
    ledger records a seed against one database while the tables and users are
    created in another, and a later run can then skip seeding a database that
    has no admin user in it.

    The path is left relative exactly as the URL gives it, so it resolves
    against the working directory the same way SQLAlchemy's engine does.
    """
    from app.config import get_settings

    url = get_settings().database_url
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        raise RuntimeError(
            f"Migration tracking is SQLite-only; DATABASE_URL is {url!r}"
        )
    return url[len(prefix):]


def init_migrations_table(db_path):
    """Create migrations tracking table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


#: Columns added to existing tables after those tables shipped. SQLAlchemy's
#: ``create_all`` creates missing *tables* but never alters an existing one, so
#: a column added later has to be applied here or older databases silently keep
#: the old shape and every query against the new column fails.
#:
#: Each entry is (table, column, SQL type). Adding a column is safe to repeat:
#: the applier checks what is already there and skips it.
ADDED_COLUMNS = [
    # Which machine a remediation runs on. NULL keeps the original behaviour,
    # so existing rows stay valid without a backfill.
    ("remediation_requests", "device_id", "VARCHAR"),
]


def apply_schema_migrations(db_path=None):
    """Add any column in :data:`ADDED_COLUMNS` the database does not have yet.

    Idempotent and safe to call on every start: existing columns are skipped,
    and a table that does not exist yet is left alone because ``create_all``
    will build it complete.

    Returns the list of columns actually added, for logging.
    """
    db_path = db_path or get_db_path()
    if not os.path.exists(db_path):
        return []

    added = []
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for table, column, sql_type in ADDED_COLUMNS:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (table,),
            )
            if cursor.fetchone() is None:
                continue

            existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
            if column in existing:
                continue

            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
            added.append(f"{table}.{column}")
        conn.commit()
    finally:
        conn.close()
    return added


def migration_applied(migration_name):
    """Check if a migration has been applied."""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT COUNT(*) FROM {MIGRATIONS_TABLE} 
            WHERE name = ?
        """, (migration_name,))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0
    except Exception:
        return False


def record_migration(migration_name):
    """Record that a migration has been applied."""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            INSERT INTO {MIGRATIONS_TABLE} (name, applied_at)
            VALUES (?, ?)
        """, (migration_name, datetime.now()))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Failed to record migration: {e}")
