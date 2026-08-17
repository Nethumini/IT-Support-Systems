"""
Database initialization script with seed data for RBAC system.
Run this to set up the database with initial users and roles.
"""
import sys
from pathlib import Path
import sqlite3
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrations import init_migrations_table, migration_applied, record_migration

# DON'T import models here - we need to check database first
# from sqlalchemy.orm import Session
# from app.core.database import engine, SessionLocal, Base
# from app.models.user import UserDB
# from app.models.ticket import TicketDB
# from app.models.audit_log import AuditLogDB
# from app.models.role import Role
# from app.core.security import get_password_hash


def init_database():
    """Initialize database tables."""
    db_path = "data/processed/it_support_systems.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # First, check if database exists
    db_already_exists = False
    if os.path.exists(db_path):
        print("[i] Existing database detected, checking schema...")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Check if role column exists in users table
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'role' not in columns:
                    print("[*] Old database schema detected (missing RBAC fields).")
                    print("   Recreating database...")
                    conn.close()
                    try:
                        os.remove(db_path)
                        print(f"[OK] Old database removed")
                    except PermissionError:
                        print(f"[!] Could not remove locked database file, will attempt forced removal...")
                        import time
                        time.sleep(0.5)
                        try:
                            os.remove(db_path)
                        except:
                            print(f"[!] Failed to remove database, using fresh schema")
                else:
                    print("[OK] Database schema is up to date, skipping recreation")
                    db_already_exists = True
                    conn.close()
            else:
                conn.close()
        except Exception as e:
            print(f"[!] Database check error")
    
    # NOW import models and create tables
    print("Creating database tables...")
    from sqlalchemy.orm import Session
    from app.core.database import engine, SessionLocal, Base
    from app.models.user import UserDB
    from app.models.ticket import TicketDB
    from app.models.audit_log import AuditLogDB
    from app.models.role import Role
    from app.core.security import get_password_hash
    
    # Only create tables if database doesn't already exist
    if not db_already_exists:
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully")
        # Initialize migrations table
        init_migrations_table(db_path)
    else:
        print("[OK] Database already exists, skipping table creation")
        # Initialize migrations table (safe even if exists)
        init_migrations_table(db_path)
    
    return SessionLocal, UserDB, Role, get_password_hash


def seed_initial_users(db, UserDB, Role, get_password_hash):
    """Seed initial users with different roles."""
    print("\nSeeding initial users...")
    
    # Check if this migration has already been applied
    migration_name = "seed_initial_users_001"
    if migration_applied(migration_name):
        print(f"[i] Migration '{migration_name}' already applied. Skipping seed.")
        return
    
    # Check if admin user exists
    try:
        existing_admin = db.query(UserDB).filter(
            UserDB.email == "admin@acme.com"
        ).first()
        
        if existing_admin:
            print("[i] Admin user already exists. Recording migration.")
            record_migration(migration_name)
            return
    except Exception as e:
        print(f"[i] Checking existing users...")
        db.rollback()
    
    users = [
        # System Admin
        UserDB(
            email="admin@acme.com",
            name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=Role.SYSTEM_ADMIN.value,
            department="IT",
            is_active=True
        ),
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"[OK] Seeded {len(users)} users successfully")
    
    # Record that this migration has been applied
    record_migration(migration_name)
    
    # Print credentials
    print("\n[*] Initial User Credentials:")
    print("=" * 60)
    print(f"{'Email':<35} {'Password':<15} {'Role':<20}")
    print("=" * 60)
    print(f"{'admin@acme.com':<35} {'admin123':<15} {'System Admin':<20}")
    print("=" * 60)
    print("\n[i] Other users can be registered through the /auth/register endpoint")


def main():
    """Main initialization function."""
    print("[*] Initializing IT Support Systems Database with RBAC System")
    print("=" * 80)
    
    # Initialize database and get imports
    SessionLocal, UserDB, Role, get_password_hash = init_database()
    
    # Create session and seed data
    db = SessionLocal()
    try:
        seed_initial_users(db, UserDB, Role, get_password_hash)
        
        print("\n[OK] Database initialization completed successfully!")
        print("\n[i] You can now login with the admin user listed above")
        
    except Exception as e:
        print(f"\n[ERROR] Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
