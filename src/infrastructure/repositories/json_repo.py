import json
import logging
import os
from pathlib import Path

from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem
from src.domain.models.performance import PerformanceMetrics

logger = logging.getLogger(__name__)


class JsonHistoryRepository(HistoryRepository):
    """
    JSON file-backed implementation of the HistoryRepository.
    Persists recommendation history and performance metrics to disk atomically.
    """

    def __init__(self, file_path: str) -> None:
        import asyncio

        self._file_path = Path(file_path)
        self._history: dict[str, MediaItem] = {}
        self._performance: list[PerformanceMetrics] = []
        self._lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "history" in data:
                history_data = data.get("history", {})
                for key, val in history_data.items():
                    self._history[key] = MediaItem(**val)

                perf_data = data.get("performance", [])
                if isinstance(perf_data, list):
                    self._performance = [
                        PerformanceMetrics.model_validate(p) for p in perf_data
                    ]
            elif isinstance(data, dict):
                for key, val in data.items():
                    self._history[key] = MediaItem(**val)
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to load history from {self._file_path}: {e}")
            self._history = {}
            self._performance = []

    def _save_to_disk(self) -> None:
        try:
            temp_file = self._file_path.with_suffix(".tmp")
            data = {
                "history": {
                    k: v.model_dump(mode="json") for k, v in self._history.items()
                },
                "performance": [p.model_dump(mode="json") for p in self._performance],
            }
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            temp_file.replace(self._file_path)
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

    async def save_performance(self, metrics: PerformanceMetrics) -> bool:
        import asyncio

        async with self._lock:
            self._performance.append(metrics)
            await asyncio.to_thread(self._save_to_disk)
        return True

    async def get_all_performance(self) -> list[PerformanceMetrics]:
        async with self._lock:
            return list(self._performance)


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
