"""
Authentication API routes for AI Health Navigator.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...database.repositories import UserRepository
from ...core.config import settings
from ...core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserCreate(BaseModel):
    """User registration request model."""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        user_repo = UserRepository(db)
        
        # Check if user already exists
        existing_user = user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        user_dict = user_data.dict()
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]
        
        user = user_repo.create(user_dict)
        
        logger.info(f"New user registered: {user.email}")
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token."""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(form_data.username)
        
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Update last login
        user_repo.update(user.id, {"last_login": "now()"})
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get(current_user.id)
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    try:
        user_repo = UserRepository(db)
        
        # Remove sensitive fields that shouldn't be updated via this endpoint
        if "password" in user_data:
            del user_data["password"]
        if "email" in user_data:
            del user_data["email"]  # Email changes should go through a separate process
        
        user = user_repo.update(current_user.id, user_data)
        logger.info(f"User updated: {user.email}")
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )


@router.post("/logout")
async def logout_user(
    current_user = Depends(get_current_user)
):
    """Logout user (client should discard token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(current_user.id)},
            expires_delta=access_token_expires
        )
        
        user_repo = UserRepository(db)
        user = user_repo.get(current_user.id)
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    try:
        user_repo = UserRepository(db)
        user = user_repo.get(current_user.id)
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_password_hash = get_password_hash(new_password)
        user_repo.update(user.id, {"password_hash": new_password_hash})
        
        logger.info(f"Password changed for user: {user.email}")
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
