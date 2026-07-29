import logging

from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class HashtagGenerationService:
    """
    Service responsible for generating optimized hashtags for a given media item.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

    async def generate_hashtags(self, item: MediaItem) -> list[str]:
        """
        Generates a list of hashtags using the AI provider.
        """
        logger.info(f"Generating hashtags for '{item.title}'...")
        prompt = (
            f"You are an expert SEO and social media manager for the CineOps account.\n"
            f"Generate a space-separated list of exactly 5 highly engaging hashtags for the {item.media_type} '{item.title}'.\n"
            f"Overview: {item.overview}\n\n"
            f"Example format: #movie #viral #trending #mustwatch #cinema\n"
            f"Respond ONLY with the raw text containing the hashtags."
        )
        response = await self.ai_provider.generate_recommendations(prompt)

        # Parse space-separated or comma-separated hashtags
        hashtags = [
            h.strip() for h in response.replace(",", " ").split() if h.startswith("#")
        ]
        return hashtags
