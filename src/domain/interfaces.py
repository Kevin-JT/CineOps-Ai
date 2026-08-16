from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation

if TYPE_CHECKING:
    from src.domain.models.performance import PerformanceMetrics
    from src.domain.models.youtube import YouTubeSource


class AIProvider(ABC):
    @abstractmethod
    async def generate_recommendations(self, prompt: str) -> str:
        pass


class MediaProvider(ABC):
    @abstractmethod
    async def fetch_trending(self) -> list[MediaItem]:
        pass


class HistoryRepository(ABC):
    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        pass

    @abstractmethod
    async def save(self, item: MediaItem) -> bool:
        pass

    @abstractmethod
    async def save_performance(self, metrics: "PerformanceMetrics") -> bool:
        pass

    @abstractmethod
    async def get_all_performance(self) -> list["PerformanceMetrics"]:
        pass


class BlacklistRepository(ABC):
    @abstractmethod
    async def is_blacklisted(self, item_id: str) -> bool:
        pass


class NotificationProvider(ABC):
    @abstractmethod
    async def send_message(self, message: str) -> bool:
        pass


class ExportProvider(ABC):
    @abstractmethod
    async def export_recommendation(self, recommendation: "Recommendation") -> None:
        pass


class CacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        pass


class SourceProvider(ABC):
    @abstractmethod
    async def search_source(
        self,
        media_title: str,
        media_type: str,
        query_keywords: list[str] | None = None,
    ) -> "YouTubeSource | None":
        pass


class TranscriptEntry(BaseModel):
    text: str
    start: float
    duration: float


class TranscriptProvider(ABC):
    @abstractmethod
    async def get_transcript(self, video_id: str) -> list[TranscriptEntry] | None:
        pass
