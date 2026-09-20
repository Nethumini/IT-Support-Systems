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
