from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.media_item import MediaItem

class AIProvider(ABC):
    @abstractmethod
    async def generate_recommendations(self, prompt: str) -> str: pass

class MediaProvider(ABC):
    @abstractmethod
    async def fetch_trending(self) -> List[MediaItem]: pass

class Repository(ABC):
    @abstractmethod
    async def save(self, item: MediaItem) -> bool: pass
