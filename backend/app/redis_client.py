"""
Redis client for caching and rate limiting
"""

import redis
from typing import Optional
from app.database import settings

# Global Redis client
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True
)


class RateLimiter:
    """
    Rate limiting using Redis counters with TTL
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_rate_limit(self, key: str, limit: int, window_seconds: int = 900) -> tuple[bool, int]:
        """
        Check if rate limit is exceeded

        Args:
            key: Redis key (e.g., "rate_limit:user_123:posts")
            limit: Max requests allowed
            window_seconds: Time window in seconds (default 900 = 15 min)

        Returns:
            (allowed: bool, current_count: int)
        """
        current = self.redis.get(key)

        if current is None:
            # First request in window
            return True, 0

        current_count = int(current)

        if current_count >= limit:
            # Rate limit exceeded
            return False, current_count

        # Within limit
        return True, current_count

    def increment_rate_limit(self, key: str, window_seconds: int = 900) -> int:
        """
        Increment rate limit counter

        Args:
            key: Redis key
            window_seconds: TTL for the key

        Returns:
            New count value
        """
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        results = pipe.execute()

        return results[0]  # Return new count

    def get_remaining(self, key: str, limit: int) -> int:
        """
        Get remaining requests in current window

        Args:
            key: Redis key
            limit: Max requests allowed

        Returns:
            Remaining requests (0 if limit exceeded)
        """
        current = self.redis.get(key)
        if current is None:
            return limit

        current_count = int(current)
        remaining = limit - current_count

        return max(0, remaining)

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get time remaining until rate limit resets

        Args:
            key: Redis key

        Returns:
            Seconds until reset, or None if key doesn't exist
        """
        ttl = self.redis.ttl(key)
        return ttl if ttl > 0 else None


# Global rate limiter instance
rate_limiter = RateLimiter(redis_client)


# X API Rate Limit Constants
X_API_POST_LIMIT = 100  # tweets per 15 minutes
X_API_WINDOW = 900  # 15 minutes in seconds


def check_x_post_rate_limit(user_id: int) -> tuple[bool, int, Optional[int]]:
    """
    Check X API post rate limit for a user

    Args:
        user_id: User ID

    Returns:
        (allowed: bool, remaining: int, reset_in_seconds: Optional[int])
    """
    key = f"rate_limit:user_{user_id}:x_posts"
    allowed, current = rate_limiter.check_rate_limit(key, X_API_POST_LIMIT, X_API_WINDOW)
    remaining = X_API_POST_LIMIT - current
    reset_in = rate_limiter.get_ttl(key) if not allowed else None

    return allowed, remaining, reset_in


def increment_x_post_count(user_id: int) -> int:
    """
    Increment X API post counter for a user

    Args:
        user_id: User ID

    Returns:
        New count
    """
    key = f"rate_limit:user_{user_id}:x_posts"
    return rate_limiter.increment_rate_limit(key, X_API_WINDOW)
