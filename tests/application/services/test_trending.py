import pytest

from src.application.services.trending import TrendingService
from src.domain.interfaces import MediaProvider
from src.domain.models.media_item import MediaItem


class MockProvider(MediaProvider):
    def __init__(self, items: list[MediaItem], fail: bool = False):
        self._items = items
        self._fail = fail

    async def fetch_trending(self) -> list[MediaItem]:
        if self._fail:
            raise ValueError("API Failed")
        return self._items


@pytest.mark.asyncio
async def test_trending_service_success() -> None:
    item1 = MediaItem(id="1", title="Movie 1", overview="", media_type="movie")
    item2 = MediaItem(id="2", title="Anime 1", overview="", media_type="anime")

    provider1 = MockProvider([item1])
    provider2 = MockProvider([item2])

    service = TrendingService(providers=[provider1, provider2])
    results = await service.fetch_all_trending()

    assert len(results) == 2
    assert "1" in [i.id for i in results]
    assert "2" in [i.id for i in results]


@pytest.mark.asyncio
async def test_trending_service_partial_failure() -> None:
    item1 = MediaItem(id="1", title="Movie 1", overview="", media_type="movie")

    provider1 = MockProvider([item1])
    provider2 = MockProvider([], fail=True)

    service = TrendingService(providers=[provider1, provider2])
    results = await service.fetch_all_trending()

    # Should not crash, and should return the successful items
    assert len(results) == 1
    assert results[0].id == "1"
