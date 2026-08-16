import uuid
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.application.services.prompt_builder import PromptBuilder
from src.application.services.recommendation import RecommendationService
from src.core.exceptions import CineOpsError
from src.domain.interfaces import AIProvider
from src.domain.models.ai_response import AIRecommendationResponse
from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import RecommendationLog


class MockAIProvider(AIProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate_recommendations(self, prompt: str) -> str:
        return self.response


VALID_AI_RESPONSE = """
{
  "selected_id": "1",
  "confidence_score": 95.5,
  "target_audience": "Sci-Fi fans",
  "reasoning_why_now": "Trending space events.",
  "reasoning_audience_appeal": "Great visual effects.",
  "video_hook": "Some apologies arrive years too late.",
  "on_screen_text": {
    "opening": "Some apologies arrive years too late.",
    "middle": "But that doesn't mean they're worthless.",
    "ending": "Would you forgive him?"
  },
  "editing_instructions": "Fast cuts during the emotional climax. Place text centered.",
  "caption": "Check this out!",
  "hashtags": ["#scifi", "#movie", "#cinema", "#space", "#viral"],
  "first_comment": "Would you forgive someone who apologized this late?"
}
"""


@pytest.mark.asyncio
async def test_generate_recommendation_success() -> None:
    provider = MockAIProvider(VALID_AI_RESPONSE)
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
    assert "#scifi #movie #cinema #space #viral" in rec.reasoning
    assert len(rec.items) == 1
    assert rec.items[0].id == "1"

    # Verify Content Strategy fields
    assert rec.content_strategy is not None
    assert rec.content_strategy.video_hook == "Some apologies arrive years too late."
    assert (
        rec.content_strategy.on_screen_text.opening
        == "Some apologies arrive years too late."
    )
    assert (
        rec.content_strategy.on_screen_text.middle
        == "But that doesn't mean they're worthless."
    )
    assert rec.content_strategy.on_screen_text.ending == "Would you forgive him?"
    assert (
        rec.content_strategy.editing_instructions
        == "Fast cuts during the emotional climax. Place text centered."
    )
    assert rec.content_strategy.caption == "Check this out!"
    assert rec.content_strategy.hashtags == [
        "#scifi",
        "#movie",
        "#cinema",
        "#space",
        "#viral",
    ]
    assert (
        rec.content_strategy.first_comment
        == "Would you forgive someone who apologized this late?"
    )


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


@pytest.mark.asyncio
async def test_generate_recommendation_with_repo() -> None:
    provider = MockAIProvider(VALID_AI_RESPONSE)
    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    service = RecommendationService(provider, prompt_builder, repository=mock_repo)

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    await service.generate_recommendation(items)

    mock_repo.create.assert_awaited_once()
    created_log = mock_repo.create.call_args[0][0]
    assert isinstance(created_log, RecommendationLog)
    assert created_log.status == "success"
    assert created_log.response == VALID_AI_RESPONSE


class MockErrorProvider(AIProvider):
    async def generate_recommendations(self, prompt: str) -> str:
        raise ValueError("Provider Failed")


@pytest.mark.asyncio
async def test_generate_recommendation_provider_error() -> None:
    provider = MockErrorProvider()
    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    service = RecommendationService(provider, prompt_builder, repository=mock_repo)

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    with pytest.raises(ValueError, match="Provider Failed"):
        await service.generate_recommendation(items)

    mock_repo.create.assert_awaited_once()
    created_log = mock_repo.create.call_args[0][0]
    assert created_log.status == "error"
    assert "Provider Failed" in created_log.response


@pytest.mark.asyncio
async def test_service_crud_methods() -> None:
    provider = MockAIProvider("{}")
    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    service = RecommendationService(provider, prompt_builder, repository=mock_repo)

    uid = uuid.uuid4()

    await service.get_recommendation_log(uid)
    mock_repo.get.assert_awaited_once_with(uid)

    await service.get_all_recommendation_logs()
    mock_repo.get_all.assert_awaited_once()

    await service.delete_recommendation_log(uid)
    mock_repo.delete.assert_awaited_once_with(uid)


@pytest.mark.asyncio
async def test_service_crud_missing_repo() -> None:
    provider = MockAIProvider("{}")
    prompt_builder = PromptBuilder()
    service = RecommendationService(provider, prompt_builder, repository=None)

    uid = uuid.uuid4()

    with pytest.raises(CineOpsError, match="not configured"):
        await service.get_recommendation_log(uid)

    with pytest.raises(CineOpsError, match="not configured"):
        await service.get_all_recommendation_logs()

    with pytest.raises(CineOpsError, match="not configured"):
        await service.delete_recommendation_log(uid)


@pytest.mark.asyncio
async def test_generate_recommendation_cache_hit() -> None:
    provider = AsyncMock(spec=AIProvider)
    provider.generate_recommendations.side_effect = Exception("Should not be called")

    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get.return_value = VALID_AI_RESPONSE

    service = RecommendationService(
        provider, prompt_builder, repository=mock_repo, cache=mock_cache
    )

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    rec = await service.generate_recommendation(items)

    assert rec.id == "rec_1"
    assert rec.confidence_score == 95.5
    mock_cache.get.assert_awaited_once()
    mock_cache.set.assert_not_called()
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_generate_recommendation_cache_miss() -> None:
    provider = MockAIProvider(VALID_AI_RESPONSE)
    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get.return_value = None

    service = RecommendationService(
        provider, prompt_builder, repository=mock_repo, cache=mock_cache
    )

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    rec = await service.generate_recommendation(items)

    assert rec.id == "rec_1"
    assert rec.confidence_score == 95.5

    mock_cache.get.assert_awaited_once()
    mock_cache.set.assert_awaited_once()

    args, kwargs = mock_cache.set.call_args
    assert kwargs.get("ttl_seconds") == 86400
    assert args[1] == VALID_AI_RESPONSE

    mock_repo.create.assert_awaited_once()


def test_ai_recommendation_response_validation() -> None:
    # Valid model validation
    resp = AIRecommendationResponse.model_validate_json(VALID_AI_RESPONSE)
    assert resp.selected_id == "1"
    assert resp.video_hook == "Some apologies arrive years too late."
    assert resp.hashtags == ["#scifi", "#movie", "#cinema", "#space", "#viral"]

    # Invalid confidence score (>100)
    data = resp.model_dump()
    data["confidence_score"] = 150.0
    with pytest.raises(ValidationError):
        AIRecommendationResponse(**data)

    # Hashtags count != 5
    data = resp.model_dump()
    data["hashtags"] = ["#a", "#b", "#c"]
    with pytest.raises(ValidationError, match="Exactly 5 hashtags are required"):
        AIRecommendationResponse(**data)

    # Duplicate hashtags
    data = resp.model_dump()
    data["hashtags"] = ["#a", "#b", "#c", "#d", "#A"]
    with pytest.raises(ValidationError, match="Duplicate hashtags are not allowed"):
        AIRecommendationResponse(**data)

    # Empty hashtag
    data = resp.model_dump()
    data["hashtags"] = ["#a", "#b", "#c", "#d", "   "]
    with pytest.raises(ValidationError, match="Hashtags cannot contain empty strings"):
        AIRecommendationResponse(**data)


def test_prompt_builder_requirements() -> None:
    builder = PromptBuilder()
    items = [MediaItem(id="1", title="Test Movie", overview="Test", media_type="movie")]
    prompt = builder.build_recommendation_prompt(items)

    assert "video_hook" in prompt
    assert "on_screen_text" in prompt
    assert "editing_instructions" in prompt
    assert "caption" in prompt
    assert "hashtags" in prompt
    assert "first_comment" in prompt
    assert "DO NOT INVENT TIMESTAMPS" in prompt
    assert "HISTORICAL PERFORMANCE INSIGHTS" not in prompt

    prompt_with_perf = builder.build_recommendation_prompt(
        items, performance_summary="Average engagement: 14.5%"
    )
    assert "HISTORICAL PERFORMANCE INSIGHTS" in prompt_with_perf
    assert "Average engagement: 14.5%" in prompt_with_perf
