from unittest.mock import AsyncMock, Mock

import pytest

from src.application.services.coordinator import WorkflowCoordinator
from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation
from src.domain.models.scoring import ViralScore, ViralScoreFactors


@pytest.mark.asyncio
async def test_workflow_coordinator_success() -> None:
    trending_mock = AsyncMock()
    trending_mock.fetch_all_trending.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=50.0,
        )
    ]

    dedup_mock = AsyncMock()
    dedup_mock.filter_duplicates.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=50.0,
        )
    ]

    filter_mock = Mock()
    filter_mock.filter_items.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=50.0,
        )
    ]

    ranking_mock = Mock()
    ranking_mock.rank_by_popularity.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=50.0,
        )
    ]

    rec_mock = AsyncMock()
    rec_mock.generate_recommendation.return_value = Recommendation(
        id="rec_1",
        items=[
            MediaItem(
                id="1",
                title="Movie",
                overview="",
                media_type="movie",
                rating=8.0,
                popularity=50.0,
            )
        ],
        target_audience="General",
        reasoning="Reason",
    )

    scoring_mock = Mock()
    scoring_mock.calculate_score.return_value = ViralScore(
        score=85.0,
        factors=ViralScoreFactors(
            popularity=50.0,
            rating=8.0,
            recognition=80.0,
            visual_impact=85.0,
            emotional_impact=70.0,
            social_potential=90.0,
        ),
    )

    export_mock = AsyncMock()
    history_mock = AsyncMock()
    notification_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_mock,
        scoring_service=scoring_mock,
        export_provider=export_mock,
        history_repo=history_mock,
        notification_provider=notification_mock,
    )

    await coordinator.run_pipeline()

    assert trending_mock.fetch_all_trending.called
    assert dedup_mock.filter_duplicates.called
    assert filter_mock.filter_items.called
    assert ranking_mock.rank_by_popularity.called
    assert rec_mock.generate_recommendation.called
    assert scoring_mock.calculate_score.called
    assert history_mock.save.called
    assert export_mock.export_recommendation.called
    assert notification_mock.send_message.called


@pytest.mark.asyncio
async def test_workflow_coordinator_aborts_early() -> None:
    trending_mock = AsyncMock()
    trending_mock.fetch_all_trending.return_value = []
    dedup_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=Mock(),
        ranking_service=Mock(),
        recommendation_service=AsyncMock(),
        scoring_service=Mock(),
        export_provider=AsyncMock(),
        history_repo=AsyncMock(),
        notification_provider=AsyncMock(),
    )

    await coordinator.run_pipeline()

    # Assert nothing else was called
    dedup_mock.filter_duplicates.assert_not_called()
