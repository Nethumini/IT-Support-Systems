"""
Authentication service - User registration, login, and password hashing.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import UserDB, UserRegister, UserLogin
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for user authentication."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password. Truncate to 72 bytes for bcrypt compatibility."""
        # Bcrypt has a 72 byte limit, truncate password to 72 characters
        truncated_password = password[:72]
        return pwd_context.hash(truncated_password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash. Truncate to 72 bytes for bcrypt compatibility."""
        # Bcrypt has a 72 byte limit, truncate password to 72 characters
        truncated_password = plain_password[:72]
        return pwd_context.verify(truncated_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> UserDB:
        """Register a new user with inactive status by default."""
        # Check if user already exists
        existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with inactive status by default
        hashed_password = AuthService.hash_password(user_data.password)
        db_user = UserDB(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            tier=user_data.tier,
            is_active=False  # Set inactive by default - admin must activate
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered (inactive): {user_data.email}")
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> UserDB:
        """Authenticate user and return user object."""
        user = db.query(UserDB).filter(UserDB.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not AuthService.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account pending activation. Please contact your administrator."
            )
        
        logger.info(f"User authenticated: {login_data.email}")
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
        """Get user by email."""
        return db.query(UserDB).filter(UserDB.email == email).first()


# Create global service instance
auth_service = AuthService()
