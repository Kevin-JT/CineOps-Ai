import pytest

from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem
from src.domain.models.performance import PerformanceMetrics
from src.domain.services.deduplication import DeduplicationService


class MockHistoryRepo(HistoryRepository):
    async def exists(self, item_id: str) -> bool:
        return item_id == "history_id"

    async def save(self, item: MediaItem) -> bool:
        return True

    async def save_performance(self, metrics: "PerformanceMetrics") -> bool:
        return True

    async def get_all_performance(self) -> list["PerformanceMetrics"]:
        return []


class MockBlacklistRepo(BlacklistRepository):
    async def is_blacklisted(self, item_id: str) -> bool:
        return item_id == "blacklisted_id"


@pytest.mark.asyncio
async def test_filter_duplicates() -> None:
    history_repo = MockHistoryRepo()
    blacklist_repo = MockBlacklistRepo()

    service = DeduplicationService(history_repo, blacklist_repo)

    items = [
        MediaItem(id="new_id", title="New", overview="", media_type="movie"),
        MediaItem(id="history_id", title="History", overview="", media_type="movie"),
        MediaItem(
            id="blacklisted_id", title="Blacklisted", overview="", media_type="movie"
        ),
    ]

    filtered = await service.filter_duplicates(items)

    assert len(filtered) == 1
    assert filtered[0].id == "new_id"
