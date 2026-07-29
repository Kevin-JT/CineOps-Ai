import asyncio
import time
from typing import NamedTuple

from src.domain.interfaces import CacheProvider


class CacheEntry(NamedTuple):
    value: str
    expires_at: float | None


class InMemoryCacheProvider(CacheProvider):
    """
    A simple thread-safe, async-friendly in-memory cache provider.
    Maintains a Redis-ready signature (stores strings).
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> str | None:
        """
        Retrieves a value from the cache if it exists and has not expired.
        """
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            if entry.expires_at is not None and time.time() > entry.expires_at:
                # Expired
                del self._store[key]
                return None

            return entry.value

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        """
        Stores a value in the cache with an optional TTL.
        """
        expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
        async with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=expires_at)
