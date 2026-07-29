import httpx
import pytest
import respx

from src.core.exceptions import ProviderError
from src.infrastructure.providers.jikan_provider import JikanProvider


@pytest.fixture
def provider() -> JikanProvider:
    return JikanProvider(base_url="https://api.jikan.moe/v4", timeout=1.0)


@pytest.mark.asyncio
@respx.mock
async def test_jikan_fetch_trending_success(provider: JikanProvider) -> None:
    mock_data = {
        "data": [
            {
                "mal_id": 456,
                "title_english": "Test Anime",
                "synopsis": "Anime Overview",
                "aired": {"from": "2023-05-10T00:00:00+00:00"},
                "score": 9.2,
                "members": 50000,
            }
        ]
    }

    route = respx.get("https://api.jikan.moe/v4/top/anime").mock(
        return_value=httpx.Response(200, json=mock_data)
    )

    items = await provider.fetch_trending()

    assert route.called
    assert len(items) == 1
    assert items[0].id == "456"
    assert items[0].title == "Test Anime"
    assert items[0].media_type == "anime"
    assert items[0].release_date == "2023-05-10"
    assert items[0].popularity == 50000.0


@pytest.mark.asyncio
@respx.mock
async def test_jikan_fetch_trending_failure(provider: JikanProvider) -> None:
    respx.get("https://api.jikan.moe/v4/top/anime").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(ProviderError) as exc_info:
        await provider.fetch_trending()

    assert "Operation fetch_trending failed" in str(exc_info.value)
