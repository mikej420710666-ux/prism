"""
X (Twitter) API Integration
OAuth 2.0 authentication and API calls
"""

import tweepy
from typing import List, Dict, Optional
from datetime import datetime
import logging
from app.database import settings

logger = logging.getLogger(__name__)


class XAPIClient:
    """
    Wrapper for X API v2 using Tweepy
    """

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize X API client

        Args:
            access_token: User's OAuth access token (for authenticated requests)
        """
        if access_token:
            # OAuth 2.0 user context
            self.client = tweepy.Client(
                bearer_token=settings.x_bearer_token,
                access_token=access_token
            )
        else:
            # App-only authentication (read-only)
            self.client = tweepy.Client(bearer_token=settings.x_bearer_token)


    def get_user_tweets(self, user_id: str, max_results: int = 100) -> List[Dict]:
        """
        Fetch recent tweets from a user
        Used for voice analysis

        Args:
            user_id: X user ID
            max_results: Number of tweets to fetch (max 100)

        Returns:
            List of tweet dicts with text and metadata
        """
        try:
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "text"],
                exclude=["retweets", "replies"]  # Only original tweets
            )

            if not response.data:
                return []

            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "metrics": {
                        "likes": tweet.public_metrics.get("like_count", 0),
                        "retweets": tweet.public_metrics.get("retweet_count", 0),
                        "replies": tweet.public_metrics.get("reply_count", 0),
                    }
                })

            return tweets

        except tweepy.TweepyException as e:
            logger.error(f"Error fetching user tweets: {e}")
            raise


    def search_viral_posts(self, niche: str, min_engagement: int = 100, max_results: int = 50) -> List[Dict]:
        """
        Search for viral posts in a specific niche

        Args:
            niche: Topic/hashtag to search
            min_engagement: Minimum likes + retweets
            max_results: Number of tweets to fetch

        Returns:
            List of viral tweets with engagement metrics
        """
        try:
            # Build search query
            query = f"{niche} -is:retweet -is:reply lang:en"

            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "author_id"],
                expansions=["author_id"],
                user_fields=["username"]
            )

            if not response.data:
                return []

            # Create username lookup
            users = {user.id: user.username for user in response.includes.get("users", [])}

            viral_posts = []
            for tweet in response.data:
                metrics = tweet.public_metrics
                engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0)

                if engagement >= min_engagement:
                    viral_posts.append({
                        "id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "author_username": users.get(tweet.author_id, "unknown"),
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "engagement_score": engagement,
                        "metrics": {
                            "likes": metrics.get("like_count", 0),
                            "retweets": metrics.get("retweet_count", 0),
                            "replies": metrics.get("reply_count", 0),
                            "views": metrics.get("impression_count", 0)
                        }
                    })

            # Sort by engagement
            viral_posts.sort(key=lambda x: x["engagement_score"], reverse=True)

            return viral_posts

        except tweepy.TweepyException as e:
            logger.error(f"Error searching viral posts: {e}")
            raise


    def post_tweet(self, content: str) -> Dict:
        """
        Post a tweet to user's account

        Args:
            content: Tweet text (max 280 chars)

        Returns:
            Posted tweet data including tweet ID

        Raises:
            ValueError: If content exceeds 280 chars
            tweepy.TweepyException: If posting fails
        """
        if len(content) > 280:
            raise ValueError(f"Tweet exceeds 280 characters ({len(content)} chars)")

        try:
            response = self.client.create_tweet(text=content)

            return {
                "id": response.data["id"],
                "text": content,
                "posted_at": datetime.utcnow().isoformat()
            }

        except tweepy.TweepyException as e:
            logger.error(f"Error posting tweet: {e}")
            raise


    def get_tweet_analytics(self, tweet_id: str) -> Dict:
        """
        Get engagement metrics for a tweet

        Args:
            tweet_id: X tweet ID

        Returns:
            Metrics: likes, retweets, replies, impressions
        """
        try:
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=["public_metrics", "created_at"]
            )

            if not response.data:
                return {}

            tweet = response.data
            metrics = tweet.public_metrics

            return {
                "id": tweet.id,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "views": metrics.get("impression_count", 0),
                "engagement_score": (
                    metrics.get("like_count", 0) +
                    metrics.get("retweet_count", 0) +
                    metrics.get("reply_count", 0)
                )
            }

        except tweepy.TweepyException as e:
            logger.error(f"Error fetching tweet analytics: {e}")
            raise


    def get_user_info(self, user_id: str) -> Dict:
        """
        Get user profile information

        Args:
            user_id: X user ID

        Returns:
            User profile data
        """
        try:
            response = self.client.get_user(
                id=user_id,
                user_fields=["username", "name", "description", "public_metrics"]
            )

            if not response.data:
                return {}

            user = response.data

            return {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "description": user.description,
                "followers_count": user.public_metrics.get("followers_count", 0),
                "following_count": user.public_metrics.get("following_count", 0),
                "tweet_count": user.public_metrics.get("tweet_count", 0)
            }

        except tweepy.TweepyException as e:
            logger.error(f"Error fetching user info: {e}")
            raise
