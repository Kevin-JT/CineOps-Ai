import logging

from redis.asyncio import Redis

from src.domain.interfaces import CacheProvider

logger = logging.getLogger(__name__)


class RedisCacheProvider(CacheProvider):
    """
    A Redis-backed cache provider implementing the CacheProvider interface.
    """

    def __init__(self, redis_client: Redis) -> None:
        """
        Initialize the provider with a pre-configured async Redis client.
        """
        self._redis = redis_client

    async def get(self, key: str) -> str | None:
        """
        Retrieves a value from Redis by key.
        """
        try:
            value = await self._redis.get(key)
            if value is not None:
                # Redis returns bytes by default, decode to string if it's bytes
                if isinstance(value, bytes):
                    return value.decode("utf-8")
                return str(value)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Redis get failed for key {key}: {e}")
        return None

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """
        Stores a value in Redis with an optional TTL.
        """
        try:
            if ttl_seconds is not None:
                await self._redis.setex(key, ttl_seconds, value)
            else:
                await self._redis.set(key, value)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Redis set failed for key {key}: {e}")

    async def close(self) -> None:
        """
        Closes the connection pool.
        """
        await self._redis.aclose()
