"""
FastAPI dependencies
Reusable dependency functions for route handlers
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.auth import verify_token


# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token

    Used in route handlers:
    @app.get("/api/me")
    async def get_me(current_user: User = Depends(get_current_user)):
        return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user ID from token
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user is active (can add disabled field later)
    """
    # Can add user.is_active check here
    return current_user


async def verify_x_connection(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user has connected their X account

    Used for routes that require X API access
    """
    if not current_user.x_access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X account not connected. Please connect your X account first."
        )

    return current_user
