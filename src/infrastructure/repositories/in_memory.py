from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem


class InMemoryHistoryRepository(HistoryRepository):
    """
    In-memory implementation of the HistoryRepository.
    Uses a capped dictionary to prevent unbounded memory growth.
    """

    def __init__(self, max_size: int = 10000) -> None:
        self._history: dict[str, MediaItem] = {}
        self._max_size = max_size

    async def save(self, item: MediaItem) -> bool:
        if len(self._history) >= self._max_size:
            # Simple eviction: remove oldest key (first in dict)
            first_key = next(iter(self._history))
            del self._history[first_key]
        self._history[item.id] = item
        return True

    async def exists(self, item_id: str) -> bool:
        return item_id in self._history


class InMemoryBlacklistRepository(BlacklistRepository):
    """
    In-memory implementation of the BlacklistRepository.
    Uses a capped set to prevent unbounded memory growth.
    """

    def __init__(self, max_size: int = 10000) -> None:
        self._blacklist: set[str] = set()
        self._max_size = max_size

    async def is_blacklisted(self, item_id: str) -> bool:
        return item_id in self._blacklist

    async def add(self, item_id: str) -> None:
        if len(self._blacklist) >= self._max_size:
            # Simple eviction for set: pop arbitrary element
            self._blacklist.pop()
        self._blacklist.add(item_id)
