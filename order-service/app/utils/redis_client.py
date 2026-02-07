import redis
import os
from typing import Optional

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(REDIS_URL)

    def acquire_lock(self, lock_key: str, ttl_seconds: int = 30) -> bool:
        """Acquire a distributed lock with TTL"""
        return self.client.set(lock_key, "locked", ex=ttl_seconds, nx=True)

    def release_lock(self, lock_key: str) -> bool:
        """Release a distributed lock"""
        return self.client.delete(lock_key) > 0

    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        return self.client.get(key)

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in Redis with optional TTL"""
        return self.client.set(key, value, ex=ttl_seconds)

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        return self.client.delete(key) > 0

    def ping(self) -> bool:
        """Check Redis connectivity"""
        try:
            return self.client.ping()
        except:
            return False

# Global Redis client instance
redis_client = RedisClient()
