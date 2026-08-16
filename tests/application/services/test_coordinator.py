from unittest.mock import AsyncMock, Mock

import pytest

from src.application.services.coordinator import WorkflowCoordinator
from src.domain.models.ai_response import OnScreenText
from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import ContentStrategy, Recommendation
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

    strategy = ContentStrategy(
        video_hook="Unforgettable moment",
        on_screen_text=OnScreenText(
            opening="Opening text", middle="Middle text", ending="Ending text"
        ),
        editing_instructions="Cut fast on beats.",
        caption="Must watch cinema!",
        hashtags=["#movie", "#cinema", "#film", "#scene", "#viral"],
        first_comment="What did you think?",
    )

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
        content_strategy=strategy,
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

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "CINEOPS CONTENT OPPORTUNITY" in sent_msg
    assert "Unforgettable moment" in sent_msg
    assert "Opening text" in sent_msg
    assert "Must watch cinema!" in sent_msg
    assert "#movie #cinema #film #scene #viral" in sent_msg


@pytest.mark.asyncio
async def test_workflow_coordinator_with_youtube_source() -> None:
    from src.domain.models.youtube import YouTubeSource

    yt_source = YouTubeSource(
        video_id="yt_123",
        title="Movie Best Scene",
        channel_name="CinemaClips",
        url="https://www.youtube.com/watch?v=yt_123",
        relevance_score=85.0,
    )

    source_mock = AsyncMock()
    source_mock.search_source.return_value = yt_source

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

    strategy = ContentStrategy(
        video_hook="Hook",
        on_screen_text=OnScreenText(opening="O", middle="M", ending="E"),
        editing_instructions="Edit",
        caption="Cap",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="Comm",
    )

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
        content_strategy=strategy,
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
        source_provider=source_mock,
    )

    await coordinator.run_pipeline()

    assert source_mock.search_source.called
    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "YOUTUBE SOURCE" in sent_msg
    assert "Movie Best Scene" in sent_msg
    assert "https://www.youtube.com/watch?v=yt_123" in sent_msg


@pytest.mark.asyncio
async def test_workflow_coordinator_with_performance_analyzer() -> None:
    from src.domain.models.performance import PerformanceMetrics
    from src.domain.services.performance_analyzer import PerformanceAnalyzer

    perf_analyzer = PerformanceAnalyzer(min_samples=3)

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

    strategy = ContentStrategy(
        video_hook="Hook",
        on_screen_text=OnScreenText(opening="O", middle="M", ending="E"),
        editing_instructions="Edit",
        caption="Cap",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="Comm",
    )

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
        content_strategy=strategy,
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

    history_mock = AsyncMock()
    history_mock.get_all_performance.return_value = [
        PerformanceMetrics(
            recommendation_id="r1", platform="instagram", views=1000, likes=100
        ),
        PerformanceMetrics(
            recommendation_id="r2", platform="instagram", views=2000, likes=200
        ),
        PerformanceMetrics(
            recommendation_id="r3", platform="youtube", views=5000, likes=500
        ),
    ]

    notification_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_mock,
        scoring_service=scoring_mock,
        export_provider=AsyncMock(),
        history_repo=history_mock,
        notification_provider=notification_mock,
        performance_analyzer=perf_analyzer,
    )

    await coordinator.run_pipeline()

    assert rec_mock.generate_recommendation.called
    kwargs = rec_mock.generate_recommendation.call_args[1]
    assert kwargs.get("performance_summary") is not None
    assert "PERFORMANCE INSIGHTS:" in kwargs.get("performance_summary")

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "LEARNING INSIGHT" in sent_msg


@pytest.mark.asyncio
async def test_workflow_coordinator_with_quality_engine() -> None:
    from src.domain.services.quality_engine import RecommendationQualityEngine

    quality_engine = RecommendationQualityEngine()

    trending_mock = AsyncMock()
    trending_mock.fetch_all_trending.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.5,
            popularity=80.0,
        )
    ]
    dedup_mock = AsyncMock()
    dedup_mock.filter_duplicates.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.5,
            popularity=80.0,
        )
    ]
    filter_mock = Mock()
    filter_mock.filter_items.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.5,
            popularity=80.0,
        )
    ]
    ranking_mock = Mock()
    ranking_mock.rank_by_popularity.return_value = [
        MediaItem(
            id="1",
            title="Movie",
            overview="",
            media_type="movie",
            rating=8.5,
            popularity=80.0,
        )
    ]

    strategy = ContentStrategy(
        video_hook="Hook",
        on_screen_text=OnScreenText(opening="O", middle="M", ending="E"),
        editing_instructions="Edit",
        caption="Cap",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="Comm",
    )

    rec_mock = AsyncMock()
    rec_mock.generate_recommendation.return_value = Recommendation(
        id="rec_1",
        items=[
            MediaItem(
                id="1",
                title="Movie",
                overview="",
                media_type="movie",
                rating=8.5,
                popularity=80.0,
            )
        ],
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

    notification_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_mock,
        scoring_service=scoring_mock,
        export_provider=AsyncMock(),
        history_repo=AsyncMock(),
        notification_provider=notification_mock,
        quality_engine=quality_engine,
    )

    await coordinator.run_pipeline()

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "OPPORTUNITY SCORE" in sent_msg
    assert "SCORE BREAKDOWN" in sent_msg
    assert "Content Potential:" in sent_msg


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
