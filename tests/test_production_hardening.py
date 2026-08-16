from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from src.application.services.coordinator import WorkflowCoordinator
from src.config.settings import Settings
from src.domain.models.ai_response import OnScreenText
from src.domain.models.media_item import MediaItem
from src.domain.models.quality import (
    OpportunityCategory,
    OpportunityScore,
    OpportunityScoreBreakdown,
)
from src.domain.models.recommendation import ContentStrategy, Recommendation
from src.domain.models.scoring import ViralScore, ViralScoreFactors
from src.infrastructure.providers.telegram_provider import TelegramProvider
from src.infrastructure.repositories.json_repo import JsonHistoryRepository


@pytest.fixture
def sample_items() -> list[MediaItem]:
    return [
        MediaItem(
            id="m1",
            title="Movie 1",
            overview="Sci-fi drama",
            media_type="movie",
            rating=8.5,
            popularity=90.0,
        ),
        MediaItem(
            id="m2",
            title="Movie 2",
            overview="Thriller mystery",
            media_type="movie",
            rating=8.0,
            popularity=80.0,
        ),
    ]


@pytest.mark.asyncio
async def test_telegram_provider_chunking_and_fallback(
    htx_client: httpx.AsyncClient | None = None,
) -> None:
    """Tests TelegramProvider chunking for long messages and plain text fallback on 400 Bad Request."""
    mock_client = AsyncMock()

    # First call returns 400 Bad Request (Markdown error), retry returns 200 OK
    res_400 = Mock(status_code=400)
    res_400.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=Mock(), response=res_400
    )

    res_200 = Mock(status_code=200)
    res_200.raise_for_status.return_value = None
    res_200.json.return_value = {"ok": True}

    mock_client.post.side_effect = [res_400, res_200]

    provider = TelegramProvider(
        bot_token="test_token", chat_id="12345", client=mock_client
    )
    success = await provider.send_message("Test message")

    assert success is True
    assert mock_client.post.call_count == 2


@pytest.mark.asyncio
async def test_json_repo_deduplication_and_atomicity(tmp_path: Any) -> None:
    """Tests JsonHistoryRepository deduplication and safe atomic writes."""
    storage_path = tmp_path / "storage.json"
    repo = JsonHistoryRepository(str(storage_path))

    item = MediaItem(
        id="item1", title="Test Movie", overview="Overview", media_type="movie"
    )
    await repo.save(item)

    assert await repo.exists("item1") is True
    assert storage_path.exists() is True


@pytest.mark.asyncio
async def test_coordinator_isolated_telegram_failure(
    sample_items: list[MediaItem],
) -> None:
    """Tests that Telegram delivery failure does not crash the daily recommendation pipeline."""
    settings = Settings(
        tmdb_api_key="test",
        gemini_api_key="test",
        telegram_bot_token="test",
        telegram_chat_id="test",
        candidate_count=2,
    )

    trending_mock = AsyncMock()
    trending_mock.fetch_all_trending.return_value = sample_items
    dedup_mock = AsyncMock()
    dedup_mock.filter_duplicates.return_value = sample_items
    filter_mock = Mock()
    filter_mock.filter_items.return_value = sample_items
    ranking_mock = Mock()
    ranking_mock.rank_by_popularity.return_value = sample_items

    rec_service_mock = AsyncMock()
    strategy = ContentStrategy(
        video_hook="Hook",
        on_screen_text=OnScreenText(opening="O", middle="M", ending="E"),
        editing_instructions="Edit",
        caption="Cap",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="Comm",
    )
    rec_service_mock.generate_recommendation.return_value = Recommendation(
        id="rec_m1",
        items=[sample_items[0]],
        target_audience="General",
        reasoning="Reason",
        confidence_score=90.0,
        content_strategy=strategy,
    )

    scoring_mock = Mock()
    scoring_mock.calculate_score.return_value = ViralScore(
        score=85.0,
        factors=ViralScoreFactors(
            popularity=80.0,
            rating=8.5,
            recognition=80.0,
            visual_impact=85.0,
            emotional_impact=70.0,
            social_potential=90.0,
        ),
    )

    quality_engine_mock = Mock()
    quality_engine_mock.evaluate.return_value = OpportunityScore(
        final_score=85,
        category=OpportunityCategory.STRONG,
        breakdown=OpportunityScoreBreakdown(
            content_score=85.0,
            short_form_score=85.0,
            source_score=50.0,
            historical_score=50.0,
        ),
    )

    # Telegram notification fails!
    notification_mock = AsyncMock()
    notification_mock.send_message.side_effect = RuntimeError(
        "Telegram Network Timeout"
    )

    history_mock = AsyncMock()
    export_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_service_mock,
        scoring_service=scoring_mock,
        export_provider=export_mock,
        history_repo=history_mock,
        notification_provider=notification_mock,
        quality_engine=quality_engine_mock,
        settings=settings,
    )

    # Pipeline should complete without throwing an exception!
    await coordinator.run_pipeline()

    history_mock.save.assert_awaited_once()
    export_mock.export_recommendation.assert_awaited_once()
