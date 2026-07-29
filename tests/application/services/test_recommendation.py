import pytest

from src.application.services.prompt_builder import PromptBuilder
from src.application.services.recommendation import RecommendationService
from src.core.exceptions import CineOpsError
from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem


class MockAIProvider(AIProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate_recommendations(self, prompt: str) -> str:
        return self.response


@pytest.mark.asyncio
async def test_generate_recommendation_success() -> None:
    ai_response = """
    {
      "selected_id": "1",
      "confidence_score": 95.5,
      "target_audience": "Sci-Fi fans",
      "reasoning_why_now": "Trending space events.",
      "reasoning_audience_appeal": "Great visual effects.",
      "caption": "Check this out!",
      "hashtags": ["#scifi", "#movie"]
    }
    """

    provider = MockAIProvider(ai_response)
    prompt_builder = PromptBuilder()
    service = RecommendationService(provider, prompt_builder)

    items = [
        MediaItem(id="1", title="Interstellar", overview="Space", media_type="movie"),
        MediaItem(id="2", title="Dune", overview="Sand", media_type="movie"),
    ]

    rec = await service.generate_recommendation(items)

    assert rec.id == "rec_1"
    assert rec.target_audience == "Sci-Fi fans"
    assert rec.confidence_score == 95.5
    assert "Great visual effects." in rec.reasoning
    assert "Trending space events." in rec.reasoning
    assert "Check this out!" in rec.reasoning
    assert "#scifi #movie" in rec.reasoning
    assert len(rec.items) == 1
    assert rec.items[0].id == "1"


@pytest.mark.asyncio
async def test_generate_recommendation_invalid_json() -> None:
    provider = MockAIProvider("This is not JSON")
    prompt_builder = PromptBuilder()
    service = RecommendationService(provider, prompt_builder)

    items = [
        MediaItem(id="1", title="Interstellar", overview="Space", media_type="movie")
    ]

    with pytest.raises(CineOpsError, match="invalid JSON format"):
        await service.generate_recommendation(items)


@pytest.mark.asyncio
async def test_generate_recommendation_no_items() -> None:
    prompt_builder = PromptBuilder()
    service = RecommendationService(MockAIProvider("{}"), prompt_builder)
    with pytest.raises(ValueError, match="without media items"):
        await service.generate_recommendation([])
