"""
Celery configuration and background tasks
"""

from celery import Celery
from pydantic_settings import BaseSettings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    celery_broker_url: str = "redis://localhost:6379/3"
    celery_result_backend: str = "redis://localhost:6379/3"
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()

# Celery app
celery_app = Celery(
    "prism",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
)


# Background Tasks
@celery_app.task(name="prism.post_scheduled_tweet")
def post_scheduled_tweet(scheduled_post_id: int):
    """
    Post a scheduled tweet to X

    Args:
        scheduled_post_id: ID of ScheduledPost in database

    Returns:
        Tweet data with ID
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import User, ScheduledPost
    from app.x_api import XAPIClient
    from app.encryption import decrypt_token
    from app.redis_client import check_x_post_rate_limit, increment_x_post_count

    logger.info(f"Attempting to post scheduled tweet {scheduled_post_id}")

    # Database connection
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Fetch scheduled post from DB
        scheduled_post = db.query(ScheduledPost).filter(ScheduledPost.id == scheduled_post_id).first()
        if not scheduled_post:
            logger.error(f"Scheduled post {scheduled_post_id} not found")
            raise ValueError(f"Scheduled post {scheduled_post_id} not found")

        # Check if already posted
        if scheduled_post.status == "posted":
            logger.warning(f"Scheduled post {scheduled_post_id} already posted")
            return {"status": "already_posted"}

        # 2. Get user and decrypt X access token
        user = db.query(User).filter(User.id == scheduled_post.user_id).first()
        if not user or not user.x_access_token:
            scheduled_post.status = "failed"
            scheduled_post.error_message = "User not found or no X access token"
            db.commit()
            raise ValueError(f"User {scheduled_post.user_id} not found or no token")

        # 3. Check rate limit (100 posts per 15 minutes)
        allowed, remaining, reset_in = check_x_post_rate_limit(user.id)

        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user.id}. Retrying in {reset_in} seconds")
            # Reschedule for after rate limit resets
            scheduled_post.scheduled_for = datetime.utcnow() + timedelta(seconds=reset_in + 60)
            db.commit()
            # Retry task after rate limit reset
            raise self.retry(countdown=reset_in + 60, max_retries=3)

        # 4. Post tweet via X API
        access_token = decrypt_token(user.x_access_token)
        x_client = XAPIClient(access_token=access_token)

        try:
            tweet_data = x_client.post_tweet(scheduled_post.content)

            # 5. Update scheduled_post status
            scheduled_post.status = "posted"
            scheduled_post.x_post_id = tweet_data["id"]
            scheduled_post.posted_at = datetime.utcnow()
            scheduled_post.error_message = None

            # Increment rate limit counter
            increment_x_post_count(user.id)

            db.commit()

            logger.info(f"Successfully posted tweet {tweet_data['id']} for user {user.id}")

            return tweet_data

        except Exception as e:
            # Mark as failed
            scheduled_post.status = "failed"
            scheduled_post.error_message = str(e)
            db.commit()

            logger.error(f"Failed to post tweet for scheduled post {scheduled_post_id}: {e}")
            raise

    except Exception as e:
        logger.error(f"Error in post_scheduled_tweet for {scheduled_post_id}: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task(name="prism.discover_viral_posts")
def discover_viral_posts(user_id: int):
    """
    Search X for viral posts in user's niche

    Args:
        user_id: User ID
    """
    # Implementation:
    # 1. Get user's detected niche
    # 2. Search X API for viral posts
    # 3. Save posts to database
    pass


@celery_app.task(name="prism.analyze_user_voice")
def analyze_user_voice(user_id: int):
    """
    Analyze user's tweets to build voice profile

    Args:
        user_id: User ID

    Returns:
        Voice profile dict
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import User
    from app.x_api import XAPIClient
    from app.ai_service import AIRemixer
    from app.encryption import decrypt_token

    logger.info(f"Starting voice analysis for user {user_id}")

    # Database connection
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Fetch user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            raise ValueError(f"User {user_id} not found")

        if not user.x_access_token:
            logger.error(f"User {user_id} has no X access token")
            raise ValueError(f"User {user_id} has no X access token")

        # 2. Decrypt X access token
        access_token = decrypt_token(user.x_access_token)

        # 3. Fetch user's recent tweets
        x_client = XAPIClient(access_token=access_token)
        tweets = x_client.get_user_tweets(user_id=user.x_user_id, max_results=100)

        if not tweets:
            logger.warning(f"No tweets found for user {user_id}")
            return {"error": "No tweets found"}

        # Extract just the text from tweets
        tweet_texts = [tweet["text"] for tweet in tweets]

        # 4. Use AI to analyze voice and detect niche
        ai_remixer = AIRemixer()
        voice_profile = ai_remixer.analyze_voice(tweet_texts)

        # 5. Update user's voice_profile and detected_niche
        user.voice_profile = voice_profile
        user.detected_niche = ", ".join(voice_profile.get("niche", []))
        user.analysis_complete = True
        user.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Voice analysis complete for user {user_id}. Niche: {user.detected_niche}")

        return voice_profile

    except Exception as e:
        logger.error(f"Error analyzing voice for user {user_id}: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task(name="prism.auto_pilot")
def auto_pilot(user_id: int):
    """
    Full auto-pilot workflow:
    1. Discover viral posts
    2. Remix in user's voice
    3. Schedule posts

    Args:
        user_id: User ID
    """
    # Implementation:
    # 1. Discover viral posts
    # 2. Remix top posts using AI
    # 3. Schedule remixed posts based on user's posts_per_day setting
    pass


# Periodic Tasks (Celery Beat)
@celery_app.task(name="prism.process_scheduled_posts")
def process_scheduled_posts():
    """
    Check for scheduled posts that are due and post them
    Runs every minute
    """
    # Implementation:
    # 1. Query scheduled_posts where scheduled_for <= now and status = 'pending'
    # 2. Trigger post_scheduled_tweet for each
    pass


@celery_app.task(name="prism.run_auto_pilot_users")
def run_auto_pilot_users():
    """
    Run auto-pilot for all users who have it enabled
    Runs every 6 hours
    """
    # Implementation:
    # 1. Query users where auto_pilot_enabled = True
    # 2. Trigger auto_pilot task for each user
    pass
