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
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    @property
    def is_pro(self) -> bool:
        """Check if user has active Pro subscription"""
        if not self.subscription:
            return False
        return self.subscription.status == "active" and self.subscription.plan_type == "pro"


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


class Subscription(Base):
    """
    User subscription - tracks Stripe subscription status
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Stripe Data
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True, nullable=True)
    stripe_price_id = Column(String)

    # Subscription Status
    status = Column(String, default="incomplete")  # incomplete, active, canceled, past_due, unpaid
    plan_type = Column(String, default="free")  # free, pro
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscription")
    payment_history = relationship("PaymentHistory", back_populates="subscription")


class PaymentHistory(Base):
    """
    Payment transaction history
    """
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))

    # Stripe Data
    stripe_payment_intent_id = Column(String, unique=True, index=True)
    stripe_invoice_id = Column(String, unique=True, index=True, nullable=True)

    # Payment Details
    amount = Column(Integer)  # Amount in cents
    currency = Column(String, default="usd")
    status = Column(String)  # succeeded, failed, pending, canceled
    payment_method = Column(String, nullable=True)

    # Metadata
    description = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="payment_history")


class StripeWebhookEvent(Base):
    """
    Stripe webhook events - ensures idempotency
    """
    __tablename__ = "stripe_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    stripe_event_id = Column(String, unique=True, index=True)
    event_type = Column(String)
    processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
