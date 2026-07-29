from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem


class InMemoryHistoryRepository(HistoryRepository):
    def __init__(self) -> None:
        self._history: set[str] = set()

    async def exists(self, item_id: str) -> bool:
        return item_id in self._history

    async def save(self, item: MediaItem) -> bool:
        self._history.add(item.id)
        return True


class InMemoryBlacklistRepository(BlacklistRepository):
    def __init__(self) -> None:
        self._blacklist: set[str] = set()

    async def is_blacklisted(self, item_id: str) -> bool:
        return item_id in self._blacklist
