from unittest.mock import AsyncMock

import pytest

from src.infrastructure.providers.redis_cache_provider import RedisCacheProvider


@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.get = AsyncMock()
    redis.set = AsyncMock()
    redis.setex = AsyncMock()
    redis.aclose = AsyncMock()
    return redis

@pytest.fixture
def cache_provider(mock_redis: AsyncMock) -> RedisCacheProvider:
    return RedisCacheProvider(mock_redis)

@pytest.mark.asyncio
async def test_get_success(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    mock_redis.get.return_value = b"some_value"
    result = await cache_provider.get("test_key")
    assert result == "some_value"
    mock_redis.get.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_get_not_found(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    mock_redis.get.return_value = None
    result = await cache_provider.get("missing_key")
    assert result is None

@pytest.mark.asyncio
async def test_get_exception(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    mock_redis.get.side_effect = Exception("Redis error")
    result = await cache_provider.get("test_key")
    assert result is None

@pytest.mark.asyncio
async def test_set_without_ttl(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    await cache_provider.set("test_key", "test_value")
    mock_redis.set.assert_called_once_with("test_key", "test_value")

@pytest.mark.asyncio
async def test_set_with_ttl(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    await cache_provider.set("test_key", "test_value", 3600)
    mock_redis.setex.assert_called_once_with("test_key", 3600, "test_value")

@pytest.mark.asyncio
async def test_set_exception(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    mock_redis.set.side_effect = Exception("Redis error")
    # Should not raise
    await cache_provider.set("test_key", "test_value")

@pytest.mark.asyncio
async def test_close(cache_provider: RedisCacheProvider, mock_redis: AsyncMock) -> None:
    await cache_provider.close()
    mock_redis.aclose.assert_called_once()
