import httpx
import pytest
import respx

from src.core.exceptions import ProviderError
from src.infrastructure.providers.tmdb_provider import TMDbProvider


@pytest.fixture
def provider() -> TMDbProvider:
    return TMDbProvider(api_key="test_key", client=httpx.AsyncClient(), timeout=1.0)


@pytest.mark.asyncio
@respx.mock
async def test_tmdb_fetch_trending_success(provider: TMDbProvider) -> None:
    mock_data = {
        "results": [
            {
                "id": 123,
                "title": "Test Movie",
                "overview": "Test Overview",
                "release_date": "2024-01-01",
                "vote_average": 8.5,
                "popularity": 1234.5,
            }
        ]
    }

    route = respx.get(f"{provider.BASE_URL}/trending/movie/day").mock(
        return_value=httpx.Response(200, json=mock_data)
    )

    items = await provider.fetch_trending()

    assert route.called
    assert len(items) == 1
    assert items[0].id == "123"
    assert items[0].title == "Test Movie"
    assert items[0].media_type == "movie"
    assert items[0].popularity == 1234.5


@pytest.mark.asyncio
@respx.mock
async def test_tmdb_fetch_trending_failure(provider: TMDbProvider) -> None:
    respx.get(f"{provider.BASE_URL}/trending/movie/day").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(ProviderError) as exc_info:
        await provider.fetch_trending()

    assert "Operation fetch_trending failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tmdb_fetch_missing_api_key() -> None:
    provider = TMDbProvider(api_key="", client=httpx.AsyncClient())
    with pytest.raises(ProviderError, match="not configured"):
        await provider.fetch_trending()
