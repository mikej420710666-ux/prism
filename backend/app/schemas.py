"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime


# Auth Schemas
class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    x_username: Optional[str]
    detected_niche: Optional[str]
    auto_pilot_enabled: bool
    posts_per_day: int
    preferred_ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Post Schemas
class PostResponse(BaseModel):
    id: int
    x_post_id: str
    author_username: str
    content: str
    engagement_score: int
    detected_niche: str
    is_remixed: bool
    remixed_content: Optional[str]
    ai_model_used: Optional[str]
    discovered_at: datetime

    class Config:
        from_attributes = True


class RemixRequest(BaseModel):
    post_id: int
    ai_model: Optional[str] = "claude"  # claude, mistral, grok


class RemixResponse(BaseModel):
    post_id: int
    original_content: str
    remixed_content: str
    ai_model_used: str


# Scheduled Post Schemas
class SchedulePostRequest(BaseModel):
    content: str
    scheduled_for: datetime


class ScheduledPostResponse(BaseModel):
    id: int
    content: str
    scheduled_for: datetime
    status: str
    posted_at: Optional[datetime]
    x_post_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Voice Analysis Schema
class VoiceAnalysisResponse(BaseModel):
    niche: str
    voice_profile: Dict
    sample_tweets_analyzed: int
