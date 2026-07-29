from abc import ABC, abstractmethod

from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation


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
