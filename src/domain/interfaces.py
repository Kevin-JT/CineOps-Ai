from abc import ABC, abstractmethod

from src.domain.models.media_item import MediaItem


class AIProvider(ABC):
    @abstractmethod
    async def generate_recommendations(self, prompt: str) -> str:
        pass


class MediaProvider(ABC):
    @abstractmethod
    async def fetch_trending(self) -> list[MediaItem]:
        pass


class Repository(ABC):
    @abstractmethod
    async def save(self, item: MediaItem) -> bool:
        pass
