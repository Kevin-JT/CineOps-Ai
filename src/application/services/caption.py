import logging

from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class CaptionGenerationService:
    """
    Service responsible for generating a highly engaging social media caption for a given media item.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

    async def generate_caption(self, item: MediaItem) -> str:
        """
        Generates a caption using the AI provider.
        """
        logger.info(f"Generating caption for '{item.title}'...")
        prompt = (
            f"You are an expert social media manager for the CineOps account.\n"
            f"Write a highly engaging, viral-optimized caption for the {item.media_type} '{item.title}'.\n"
            f"Overview: {item.overview}\n"
            f"Rating: {item.rating}\n\n"
            f"Do not include hashtags. Respond ONLY with the raw text of the caption."
        )
        caption = await self.ai_provider.generate_recommendations(prompt)
        return caption.strip()
