import pytest

from src.application.services.caption import CaptionGenerationService
from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem


class MockAIProvider(AIProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate_recommendations(self, prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_generate_caption_success() -> None:
    provider = MockAIProvider("This is a great caption!")
    service = CaptionGenerationService(provider)

    item = MediaItem(id="1", title="Movie", overview="Overview", media_type="movie")
    caption = await service.generate_caption(item)

    assert caption == "This is a great caption!"
