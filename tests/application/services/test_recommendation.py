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


import uuid
from unittest.mock import AsyncMock

from src.domain.models.recommendation import RecommendationLog


@pytest.mark.asyncio
async def test_generate_recommendation_with_repo() -> None:
    ai_response = """
    {
      "selected_id": "1",
      "confidence_score": 90.0,
      "target_audience": "test",
      "reasoning_why_now": "test",
      "reasoning_audience_appeal": "test",
      "caption": "test",
      "hashtags": ["test"]
    }
    """
    provider = MockAIProvider(ai_response)
    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    service = RecommendationService(provider, prompt_builder, repository=mock_repo)

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    await service.generate_recommendation(items)

    mock_repo.create.assert_awaited_once()
    created_log = mock_repo.create.call_args[0][0]
    assert isinstance(created_log, RecommendationLog)
    assert created_log.status == "success"
    assert created_log.response == ai_response


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

    # get
    await service.get_recommendation_log(uid)
    mock_repo.get.assert_awaited_once_with(uid)

    # get all
    await service.get_all_recommendation_logs()
    mock_repo.get_all.assert_awaited_once()

    # delete
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
    ai_response = """
    {
      "selected_id": "1",
      "confidence_score": 99.0,
      "target_audience": "Cache test",
      "reasoning_why_now": "Fast",
      "reasoning_audience_appeal": "Fast",
      "caption": "Cached",
      "hashtags": ["#cache"]
    }
    """
    provider = AsyncMock(spec=AIProvider)
    # The provider should NOT be called on a cache hit
    provider.generate_recommendations.side_effect = Exception("Should not be called")

    prompt_builder = PromptBuilder()
    mock_repo = AsyncMock()
    mock_cache = AsyncMock()
    mock_cache.get.return_value = ai_response

    service = RecommendationService(
        provider, prompt_builder, repository=mock_repo, cache=mock_cache
    )

    items = [MediaItem(id="1", title="A", overview="A", media_type="movie")]
    rec = await service.generate_recommendation(items)

    assert rec.id == "rec_1"
    assert rec.confidence_score == 99.0
    mock_cache.get.assert_awaited_once()
    mock_cache.set.assert_not_called()
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_generate_recommendation_cache_miss() -> None:
    ai_response = """
    {
      "selected_id": "1",
      "confidence_score": 90.0,
      "target_audience": "Miss test",
      "reasoning_why_now": "Slow",
      "reasoning_audience_appeal": "Slow",
      "caption": "Miss",
      "hashtags": ["#miss"]
    }
    """
    provider = MockAIProvider(ai_response)
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
    assert rec.confidence_score == 90.0

    mock_cache.get.assert_awaited_once()
    mock_cache.set.assert_awaited_once()

    # Check TTL is set to 86400
    args, kwargs = mock_cache.set.call_args
    assert kwargs.get("ttl_seconds") == 86400
    assert args[1] == ai_response

    mock_repo.create.assert_awaited_once()
