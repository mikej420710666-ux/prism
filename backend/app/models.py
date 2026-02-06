"""
SQLAlchemy Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User account - linked to X account via OAuth
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)

    # X Account Info
    x_user_id = Column(String, unique=True, index=True)
    x_username = Column(String)
    x_access_token = Column(Text)  # Encrypted
    x_refresh_token = Column(Text)  # Encrypted
    x_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Voice Analysis
    detected_niche = Column(String, nullable=True)
    voice_profile = Column(JSON, nullable=True)  # AI-analyzed writing style
    # Structure: {"niche": ["AI", "coding"], "tone": "technical", "topics": [...], "best_content": [...]}
    analysis_complete = Column(Boolean, default=False)
    best_posting_times = Column(JSON, nullable=True)  # Optimal posting times based on engagement

    # Settings
    auto_pilot_enabled = Column(Boolean, default=False)
    posts_per_day = Column(Integer, default=3)
    preferred_ai_model = Column(String, default="claude")  # claude, mistral, grok

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    posts = relationship("Post", back_populates="user")
    scheduled_posts = relationship("ScheduledPost", back_populates="user")


class Post(Base):
    """
    Original viral posts discovered from X
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # X Post Data
    x_post_id = Column(String, unique=True, index=True)
    author_username = Column(String)
    content = Column(Text)
    engagement_score = Column(Integer)  # likes + retweets + replies
    detected_niche = Column(String)
    source_tweet_stats = Column(JSON, nullable=True)  # Full engagement metrics
    # Structure: {"views": 150000, "likes": 2000, "retweets": 500, "timestamp": "..."}

    # AI Remix
    remixed_content = Column(Text, nullable=True)
    ai_model_used = Column(String, nullable=True)

    # Status
    is_remixed = Column(Boolean, default=False)
    is_scheduled = Column(Boolean, default=False)

    # Timestamps
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    remixed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="posts")


class ScheduledPost(Base):
    """
    Posts scheduled for auto-publishing
    """
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    original_post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    # Content
    content = Column(Text)

    # Scheduling
    scheduled_for = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="pending")  # pending, posted, failed

    # X Response
    x_post_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="scheduled_posts")
