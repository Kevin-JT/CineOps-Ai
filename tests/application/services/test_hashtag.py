import pytest

from src.application.services.hashtag import HashtagGenerationService
from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem


class MockAIProvider(AIProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate_recommendations(self, prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_generate_hashtags_success() -> None:
    provider = MockAIProvider("#movie #viral #trending #mustwatch #cinema")
    service = HashtagGenerationService(provider)

    item = MediaItem(id="1", title="Movie", overview="Overview", media_type="movie")
    hashtags = await service.generate_hashtags(item)

    assert len(hashtags) == 5
    assert hashtags == ["#movie", "#viral", "#trending", "#mustwatch", "#cinema"]


@pytest.mark.asyncio
async def test_generate_hashtags_comma_separated() -> None:
    provider = MockAIProvider("#movie, #viral, #trending")
    service = HashtagGenerationService(provider)

    item = MediaItem(id="1", title="Movie", overview="Overview", media_type="movie")
    hashtags = await service.generate_hashtags(item)

    assert len(hashtags) == 3
    assert hashtags == ["#movie", "#viral", "#trending"]
