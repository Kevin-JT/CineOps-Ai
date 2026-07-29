import json
import logging
from pathlib import Path

from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class JsonHistoryRepository(HistoryRepository):
    """
    JSON file-backed implementation of the HistoryRepository.
    Persists recommendation history to disk to survive restarts.
    """

    def __init__(self, file_path: str) -> None:
        import asyncio

        self._file_path = Path(file_path)
        self._history: dict[str, MediaItem] = {}
        self._lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, val in data.items():
                    self._history[key] = MediaItem(**val)
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to load history from {self._file_path}: {e}")
            self._history = {}

    def _save_to_disk(self) -> None:
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                data = {k: v.model_dump() for k, v in self._history.items()}
                json.dump(data, f, indent=2)
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to save history to {self._file_path}: {e}")

    async def save(self, item: MediaItem) -> bool:
        import asyncio

        async with self._lock:
            self._history[item.id] = item
            await asyncio.to_thread(self._save_to_disk)
        return True

    async def exists(self, item_id: str) -> bool:
        return item_id in self._history


class JsonBlacklistRepository(BlacklistRepository):
    """
    JSON file-backed implementation of the BlacklistRepository.
    Persists blacklisted items to disk.
    """

    def __init__(self, file_path: str) -> None:
        import asyncio

        self._file_path = Path(file_path)
        self._blacklist: set[str] = set()
        self._lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._blacklist = set(data)
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to load blacklist from {self._file_path}: {e}")
            self._blacklist = set()

    def _save_to_disk(self) -> None:
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(list(self._blacklist), f, indent=2)
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to save blacklist to {self._file_path}: {e}")

    async def add(self, item_id: str) -> None:
        import asyncio

        async with self._lock:
            self._blacklist.add(item_id)
            await asyncio.to_thread(self._save_to_disk)

    async def is_blacklisted(self, item_id: str) -> bool:
        return item_id in self._blacklist
