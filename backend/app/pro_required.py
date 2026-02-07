"""
Pro Plan Dependency
Require Pro subscription for protected routes
"""

from fastapi import Depends, HTTPException, status
from app.models import User
from app.dependencies import get_current_user


async def require_pro_plan(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require Pro plan for route access

    Args:
        current_user: Current authenticated user

    Returns:
        User if Pro plan is active

    Raises:
        HTTPException: 403 if user is not on Pro plan

    Usage:
        @app.post("/api/premium-feature")
        async def premium_feature(user: User = Depends(require_pro_plan)):
            ...
    """
    if not current_user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a Pro subscription. Please upgrade to continue."
        )

    return current_user
