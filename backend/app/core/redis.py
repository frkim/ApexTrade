"""Redis client connection."""

import logging
from typing import Any

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper for async operations."""

    def __init__(self) -> None:
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Redis")

    @property
    def client(self) -> redis.Redis:
        """Get Redis client."""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        return self._client

    async def get(self, key: str) -> str | None:
        """Get value by key."""
        if not self._client:
            return None
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: str | bytes,
        ex: int | None = None,
    ) -> bool:
        """Set key-value pair with optional expiration."""
        if not self._client:
            return False
        await self._client.set(key, value, ex=ex)
        return True

    async def delete(self, key: str) -> int:
        """Delete key."""
        if not self._client:
            return 0
        return await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False
        return await self._client.exists(key) > 0

    async def publish(self, channel: str, message: str) -> int:
        """Publish message to channel."""
        if not self._client:
            return 0
        return await self._client.publish(channel, message)

    async def subscribe(self, *channels: str) -> redis.client.PubSub:
        """Subscribe to channels."""
        if not self._client:
            raise RuntimeError("Redis client not connected")
        pubsub = self._client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to list."""
        if not self._client:
            return 0
        return await self._client.lpush(key, *values)

    async def rpop(self, key: str) -> str | None:
        """Pop value from list."""
        if not self._client:
            return None
        return await self._client.rpop(key)

    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list."""
        if not self._client:
            return []
        return await self._client.lrange(key, start, end)


redis_client = RedisClient()
