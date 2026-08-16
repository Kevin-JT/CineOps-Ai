from unittest.mock import AsyncMock, Mock

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


@pytest.fixture
def sample_items() -> list[MediaItem]:
    return [
        MediaItem(
            id="1",
            title="Item A",
            overview="",
            media_type="movie",
            rating=9.0,
            popularity=95.0,
        ),
        MediaItem(
            id="2",
            title="Item B",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=85.0,
        ),
        MediaItem(
            id="3",
            title="Item C",
            overview="",
            media_type="movie",
            rating=7.0,
            popularity=75.0,
        ),
    ]


@pytest.mark.asyncio
async def test_multi_candidate_selection_ranking(sample_items: list[MediaItem]) -> None:
    settings = Settings(
        tmdb_api_key="test",
        gemini_api_key="test",
        telegram_bot_token="test",
        telegram_chat_id="test",
        candidate_count=3,
        min_opportunity_score=60,
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

    # Return different recommendations based on item
    async def mock_gen(
        items: list[MediaItem], performance_summary: str | None = None
    ) -> Recommendation:
        item_id = items[0].id
        conf = 95.0 if item_id == "1" else 80.0
        return Recommendation(
            id=f"rec_{item_id}",
            items=items,
            target_audience="General",
            reasoning="Reason",
            confidence_score=conf,
            content_strategy=strategy,
        )

    rec_service_mock.generate_recommendation.side_effect = mock_gen

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

    def mock_eval(
        recommendation: Recommendation,
        selected_item: MediaItem,
        youtube_source: None = None,
        performance_result: None = None,
    ) -> OpportunityScore:
        scores = {"1": 91, "2": 84, "3": 77}
        final_s = scores[selected_item.id]
        cat = (
            OpportunityCategory.EXCEPTIONAL
            if final_s >= 90
            else OpportunityCategory.STRONG
        )
        return OpportunityScore(
            final_score=final_s,
            category=cat,
            breakdown=OpportunityScoreBreakdown(
                content_score=float(final_s),
                short_form_score=float(final_s),
                source_score=50.0,
                historical_score=50.0,
            ),
            strengths=["High rating"],
            weaknesses=[],
        )

    quality_engine_mock.evaluate.side_effect = mock_eval

    notification_mock = AsyncMock()
    history_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_service_mock,
        scoring_service=scoring_mock,
        export_provider=AsyncMock(),
        history_repo=history_mock,
        notification_provider=notification_mock,
        quality_engine=quality_engine_mock,
        settings=settings,
    )

    await coordinator.run_pipeline()

    # Item A ("1") should be selected as winner (score 91)
    history_mock.save.assert_awaited_once()
    saved_item = history_mock.save.call_args[0][0]
    assert saved_item.id == "1"

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "SELECTED FROM 3 CANDIDATES" in sent_msg
    assert "Item A" in sent_msg
    assert "91/100" in sent_msg
    assert "TOP ALTERNATIVES" in sent_msg
    assert "2. Item B — 84/100" in sent_msg
    assert "3. Item C — 77/100" in sent_msg


@pytest.mark.asyncio
async def test_failure_isolation(sample_items: list[MediaItem]) -> None:
    settings = Settings(
        tmdb_api_key="test",
        gemini_api_key="test",
        telegram_bot_token="test",
        telegram_chat_id="test",
        candidate_count=3,
        min_opportunity_score=60,
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

    # Item 1 fails, Items 2 and 3 succeed
    async def mock_gen(
        items: list[MediaItem], performance_summary: str | None = None
    ) -> Recommendation:
        item_id = items[0].id
        if item_id == "1":
            raise RuntimeError("Gemini Timeout for Item 1")
        return Recommendation(
            id=f"rec_{item_id}",
            items=items,
            target_audience="General",
            reasoning="Reason",
            confidence_score=85.0,
            content_strategy=strategy,
        )

    rec_service_mock.generate_recommendation.side_effect = mock_gen

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

    def mock_eval(
        recommendation: Recommendation,
        selected_item: MediaItem,
        youtube_source: None = None,
        performance_result: None = None,
    ) -> OpportunityScore:
        final_s = 85 if selected_item.id == "2" else 75
        return OpportunityScore(
            final_score=final_s,
            category=OpportunityCategory.STRONG,
            breakdown=OpportunityScoreBreakdown(
                content_score=float(final_s),
                short_form_score=float(final_s),
                source_score=50.0,
                historical_score=50.0,
            ),
            strengths=["High rating"],
            weaknesses=[],
        )

    quality_engine_mock.evaluate.side_effect = mock_eval

    notification_mock = AsyncMock()
    history_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_service_mock,
        scoring_service=scoring_mock,
        export_provider=AsyncMock(),
        history_repo=history_mock,
        notification_provider=notification_mock,
        quality_engine=quality_engine_mock,
        settings=settings,
    )

    await coordinator.run_pipeline()

    # Item B ("2") should be selected as winner despite Item A failing
    history_mock.save.assert_awaited_once()
    saved_item = history_mock.save.call_args[0][0]
    assert saved_item.id == "2"

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "SELECTED FROM 2 CANDIDATES" in sent_msg
    assert "Item B" in sent_msg


@pytest.mark.asyncio
async def test_min_opportunity_score_threshold_warning(
    sample_items: list[MediaItem],
) -> None:
    settings = Settings(
        tmdb_api_key="test",
        gemini_api_key="test",
        telegram_bot_token="test",
        telegram_chat_id="test",
        candidate_count=2,
        min_opportunity_score=80,  # Threshold set high to 80
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
        id="rec_low",
        items=[sample_items[0]],
        target_audience="General",
        reasoning="Reason",
        confidence_score=50.0,
        content_strategy=strategy,
    )

    scoring_mock = Mock()
    scoring_mock.calculate_score.return_value = ViralScore(
        score=50.0,
        factors=ViralScoreFactors(
            popularity=50.0,
            rating=5.0,
            recognition=50.0,
            visual_impact=50.0,
            emotional_impact=50.0,
            social_potential=50.0,
        ),
    )

    quality_engine_mock = Mock()
    quality_engine_mock.evaluate.return_value = OpportunityScore(
        final_score=55,  # 55 is below threshold 80!
        category=OpportunityCategory.AVERAGE,
        breakdown=OpportunityScoreBreakdown(
            content_score=55.0,
            short_form_score=55.0,
            source_score=50.0,
            historical_score=50.0,
        ),
        strengths=[],
        weaknesses=["Below threshold"],
    )

    notification_mock = AsyncMock()

    coordinator = WorkflowCoordinator(
        trending_service=trending_mock,
        deduplication_service=dedup_mock,
        filter_service=filter_mock,
        ranking_service=ranking_mock,
        recommendation_service=rec_service_mock,
        scoring_service=scoring_mock,
        export_provider=AsyncMock(),
        history_repo=AsyncMock(),
        notification_provider=notification_mock,
        quality_engine=quality_engine_mock,
        settings=settings,
    )

    await coordinator.run_pipeline()

    sent_msg = notification_mock.send_message.call_args[0][0]
    assert "Best candidate scored 55/100" in sent_msg
    assert "below minimum target of 80/100" in sent_msg
