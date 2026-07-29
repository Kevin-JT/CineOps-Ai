import asyncio
import logging

from src.domain.interfaces import MediaProvider
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class TrendingService:
    """
    Service responsible for aggregating trending media from multiple providers.
    """

    def __init__(self, providers: list[MediaProvider]) -> None:
        self.providers = providers

    async def fetch_all_trending(self) -> list[MediaItem]:
        """
        Fetches trending items from all configured media providers concurrently.

        Returns:
            A combined list of MediaItems.
        """
        logger.info(f"Fetching trending media from {len(self.providers)} providers...")

        tasks = [provider.fetch_trending() for provider in self.providers]

        # Use return_exceptions=True to prevent one failing provider from crashing the whole process
        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_items = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"A provider failed to fetch trending media: {result}")
            elif isinstance(result, list):
                combined_items.extend(result)

        logger.info(
            f"Successfully aggregated {len(combined_items)} total trending items."
        )
        return combined_items
