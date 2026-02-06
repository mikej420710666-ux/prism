"""
PRISM Backend API
Main FastAPI application
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import os

from app.database import get_db
from app.models import User, Post, ScheduledPost
from app.schemas import UserResponse, Token
from app.dependencies import get_current_user
from app.auth import (
    get_x_oauth_url,
    exchange_code_for_token,
    create_access_token
)
from app.encryption import encrypt_token, decrypt_token
from app.redis_client import redis_client
from app.celery_app import analyze_user_voice, post_scheduled_tweet
from app.x_api import XAPIClient
from app.ai_service import AIRemixer
from pydantic import BaseModel
from typing import Optional, List


class Settings(BaseSettings):
    app_name: str = "PRISM"
    app_env: str = "development"
    port: int = 8003
    allowed_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="X Growth Automation - AI-powered tweet remixing and scheduling",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "environment": settings.app_env
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============================================================================
# AUTHENTICATION & OAUTH ROUTES
# ============================================================================

@app.get("/api/auth/connect")
async def connect_x_account():
    """
    Start X OAuth 2.0 flow with PKCE

    Returns:
        Redirect to X authorization URL
    """
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Generate OAuth URL and code_verifier
    auth_url, code_verifier = get_x_oauth_url(state)

    # Store state and code_verifier in Redis (expires in 10 minutes)
    redis_client.setex(f"oauth_state:{state}", 600, code_verifier)

    return {
        "authorization_url": auth_url,
        "state": state
    }


@app.get("/api/auth/callback")
async def oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    OAuth callback - exchange code for tokens

    Args:
        code: Authorization code from X
        state: State parameter for CSRF protection

    Returns:
        JWT access token for our API
    """
    # Verify state and get code_verifier from Redis
    code_verifier = redis_client.get(f"oauth_state:{state}")

    if not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter"
        )

    # Delete state from Redis
    redis_client.delete(f"oauth_state:{state}")

    try:
        # Exchange code for X access token
        token_data = await exchange_code_for_token(code, code_verifier)

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data.get("expires_in", 7200)  # Default 2 hours

        # Get user info from X API
        x_client = XAPIClient(access_token=access_token)

        # Use the "me" endpoint to get current user
        # For now, we'll need the user ID - tweepy might need adjustment
        # This is a placeholder - actual implementation depends on Tweepy version
        me_response = x_client.client.get_me(user_fields=["username"])
        x_user_id = str(me_response.data.id)
        x_username = me_response.data.username

        # Check if user already exists
        user = db.query(User).filter(User.x_user_id == x_user_id).first()

        if not user:
            # Create new user
            user = User(
                username=x_username,
                x_user_id=x_user_id,
                x_username=x_username,
                x_access_token=encrypt_token(access_token),
                x_refresh_token=encrypt_token(refresh_token),
                x_token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            db.add(user)
        else:
            # Update existing user's tokens
            user.x_access_token = encrypt_token(access_token)
            user.x_refresh_token = encrypt_token(refresh_token)
            user.x_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            user.x_username = x_username

        db.commit()
        db.refresh(user)

        # Trigger voice analysis in background
        analyze_user_voice.delay(user.id)

        # Create JWT token for our API
        jwt_token = create_access_token(data={"sub": user.id})

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "x_username": user.x_username
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code for token: {str(e)}"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info

    Returns:
        User profile data
    """
    return current_user


# ============================================================================
# USER & VOICE ANALYSIS ROUTES
# ============================================================================

@app.post("/api/user/voice/analyze")
async def trigger_voice_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger voice analysis for current user

    Returns:
        Task ID and status
    """
    if not current_user.x_access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X account not connected"
        )

    # Trigger Celery task
    task = analyze_user_voice.delay(current_user.id)

    return {
        "task_id": task.id,
        "status": "processing",
        "message": "Voice analysis started"
    }


@app.get("/api/user/voice")
async def get_voice_profile(current_user: User = Depends(get_current_user)):
    """
    Get user's voice profile

    Returns:
        Voice profile data
    """
    if not current_user.analysis_complete:
        return {
            "status": "pending",
            "message": "Voice analysis not complete yet"
        }

    return {
        "status": "complete",
        "niche": current_user.detected_niche,
        "voice_profile": current_user.voice_profile,
        "analysis_complete": current_user.analysis_complete
    }


# ============================================================================
# DISCOVERY & REMIX ROUTES
# ============================================================================

# Pydantic models for request bodies
class RemixRequest(BaseModel):
    source_tweet_id: str
    source_text: str
    model: str = "claude"  # claude/mistral/grok

class ScheduleRequest(BaseModel):
    post_id: int
    scheduled_time: datetime


@app.get("/api/discover")
async def discover_posts(
    niche: Optional[str] = None,
    min_likes: int = 1000,
    max_results: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    Search for viral posts in user's niche

    Args:
        niche: Topic/hashtag to search (defaults to user's detected niche)
        min_likes: Minimum engagement threshold
        max_results: Number of posts to return

    Returns:
        List of viral posts with engagement metrics
    """
    if not current_user.x_access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="X account not connected"
        )

    # Use user's niche if not provided
    search_niche = niche or current_user.detected_niche or "trending"

    try:
        # Use bearer token for search (read-only)
        x_client = XAPIClient()
        viral_posts = x_client.search_viral_posts(
            niche=search_niche,
            min_engagement=min_likes,
            max_results=max_results
        )

        return {
            "niche": search_niche,
            "count": len(viral_posts),
            "posts": viral_posts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search viral posts: {str(e)}"
        )


@app.post("/api/remix")
async def remix_post(
    request: RemixRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remix a viral post using AI in user's voice

    Args:
        source_tweet_id: Original tweet ID
        source_text: Original tweet text
        model: AI model to use (claude/mistral/grok)

    Returns:
        Remixed content and post ID
    """
    if not current_user.analysis_complete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice analysis not complete yet. Please wait for analysis to finish."
        )

    try:
        # Use AI to remix the content
        ai_remixer = AIRemixer()
        remixed_content = ai_remixer.remix_tweet(
            original_content=request.source_text,
            voice_profile=current_user.voice_profile,
            model=request.model
        )

        # Save to Post table
        new_post = Post(
            user_id=current_user.id,
            content=remixed_content,
            source_tweet_id=request.source_tweet_id,
            ai_model=request.model,
            status="draft"
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return {
            "post_id": new_post.id,
            "original": request.source_text,
            "remixed": remixed_content,
            "model": request.model,
            "status": "draft"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remix post: {str(e)}"
        )


# ============================================================================
# SCHEDULING ROUTES
# ============================================================================

@app.post("/api/schedule")
async def schedule_post(
    request: ScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule a remixed post for future posting

    Args:
        post_id: ID of the Post to schedule
        scheduled_time: When to post (datetime)

    Returns:
        Scheduled post details
    """
    # Get the post
    post = db.query(Post).filter(
        Post.id == request.post_id,
        Post.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Validate scheduled time is in the future
    if request.scheduled_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future"
        )

    try:
        # Create ScheduledPost
        scheduled_post = ScheduledPost(
            user_id=current_user.id,
            post_id=post.id,
            content=post.content,
            scheduled_for=request.scheduled_time,
            status="pending"
        )
        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)

        # Queue Celery task with ETA
        post_scheduled_tweet.apply_async(
            args=[scheduled_post.id],
            eta=request.scheduled_time
        )

        return {
            "scheduled_post_id": scheduled_post.id,
            "post_id": post.id,
            "content": post.content,
            "scheduled_for": request.scheduled_time.isoformat(),
            "status": "pending"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}"
        )


@app.get("/api/schedule/queue")
async def get_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's scheduled posts queue

    Returns:
        List of scheduled posts ordered by scheduled_for
    """
    scheduled_posts = db.query(ScheduledPost).filter(
        ScheduledPost.user_id == current_user.id,
        ScheduledPost.status.in_(["pending", "posted", "failed"])
    ).order_by(ScheduledPost.scheduled_for.desc()).all()

    return {
        "count": len(scheduled_posts),
        "posts": [
            {
                "id": sp.id,
                "post_id": sp.post_id,
                "content": sp.content,
                "scheduled_for": sp.scheduled_for.isoformat(),
                "status": sp.status,
                "posted_at": sp.posted_at.isoformat() if sp.posted_at else None,
                "x_post_id": sp.x_post_id,
                "error_message": sp.error_message
            }
            for sp in scheduled_posts
        ]
    }


@app.delete("/api/schedule/{scheduled_post_id}")
async def delete_scheduled(
    scheduled_post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel/delete a scheduled post

    Args:
        scheduled_post_id: ID of the ScheduledPost to delete

    Returns:
        Success message
    """
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == scheduled_post_id,
        ScheduledPost.user_id == current_user.id
    ).first()

    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )

    if scheduled_post.status == "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete already posted tweet"
        )

    try:
        db.delete(scheduled_post)
        db.commit()

        return {
            "success": True,
            "message": f"Scheduled post {scheduled_post_id} deleted"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scheduled post: {str(e)}"
        )


# ============================================================================
# ANALYTICS ROUTES
# ============================================================================

@app.get("/api/analytics/posts")
async def get_post_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics for user's published posts

    Returns:
        List of posts with engagement metrics
    """
    # Get all posted ScheduledPosts with x_post_id
    posted = db.query(ScheduledPost).filter(
        ScheduledPost.user_id == current_user.id,
        ScheduledPost.status == "posted",
        ScheduledPost.x_post_id.isnot(None)
    ).order_by(ScheduledPost.posted_at.desc()).limit(50).all()

    if not posted:
        return {"count": 0, "posts": []}

    try:
        # Get fresh analytics from X API
        access_token = decrypt_token(current_user.x_access_token)
        x_client = XAPIClient(access_token=access_token)

        analytics = []
        for sp in posted:
            try:
                metrics = x_client.get_tweet_analytics(sp.x_post_id)
                analytics.append({
                    "scheduled_post_id": sp.id,
                    "content": sp.content,
                    "posted_at": sp.posted_at.isoformat(),
                    "x_post_id": sp.x_post_id,
                    "metrics": metrics
                })
            except Exception as e:
                # If can't fetch metrics for one tweet, skip it
                continue

        return {
            "count": len(analytics),
            "posts": analytics
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )

