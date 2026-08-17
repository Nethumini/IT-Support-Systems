"""
Authentication endpoints - Registration and login.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user (account will be inactive until admin approves).
    
    - **email**: Valid email address
    - **name**: Full name
    - **password**: Strong password (min 6 characters)
    - **tier**: User tier (staff, manager, contractor)
    
    Note: New accounts are created as inactive and require admin activation.
    """
    try:
        user = auth_service.register_user(db, user_data)
        logger.info(f"User registered, pending activation: {user_data.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT token and user information.
    """
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, login_data)
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Return token and user info with permissions
        return Token(
            access_token=access_token,
            user=UserResponse.from_db(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Get current user information with permissions.
    """
    user = auth_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_db(user)
