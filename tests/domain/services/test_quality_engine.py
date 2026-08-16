from src.domain.models.ai_response import OnScreenText
from src.domain.models.media_item import MediaItem
from src.domain.models.quality import OpportunityCategory
from src.domain.models.recommendation import ContentStrategy, Recommendation
from src.domain.models.youtube import YouTubeSource
from src.domain.services.performance_analyzer import PerformanceInsightResult
from src.domain.services.quality_engine import RecommendationQualityEngine


def make_item(popularity: float = 80.0, rating: float = 8.5) -> MediaItem:
    return MediaItem(
        id="m1",
        title="Interstellar",
        overview="Space travel",
        media_type="movie",
        rating=rating,
        popularity=popularity,
    )


def make_strategy() -> ContentStrategy:
    return ContentStrategy(
        video_hook="Some apologies arrive years too late.",
        on_screen_text=OnScreenText(
            opening="Opening text", middle="Middle text", ending="Ending text"
        ),
        editing_instructions="Cut fast on beat.",
        caption="Must watch!",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="What do you think?",
    )


def make_recommendation(confidence: float = 95.0) -> Recommendation:
    return Recommendation(
        id="rec_m1",
        items=[make_item()],
        target_audience="Sci-Fi fans",
        reasoning="Great visual effects",
        confidence_score=confidence,
        content_strategy=make_strategy(),
    )


def test_quality_engine_exceptional() -> None:
    engine = RecommendationQualityEngine()
    item = make_item(popularity=95.0, rating=9.0)
    rec = make_recommendation(confidence=98.0)
    yt = YouTubeSource(
        video_id="v1",
        title="Interstellar Docking Scene",
        channel_name="Clips",
        url="https://youtube.com/watch?v=v1",
        relevance_score=90.0,
        quality_score=85.0,
        timestamp_verified=True,
    )
    perf = PerformanceInsightResult(
        sample_size=10,
        confidence="Medium",
        has_enough_data=True,
        insights=["Avg engagement 15%"],
    )

    opp = engine.evaluate(rec, item, youtube_source=yt, performance_result=perf)

    assert 85 <= opp.final_score <= 100
    assert opp.category in (OpportunityCategory.EXCEPTIONAL, OpportunityCategory.STRONG)
    assert opp.breakdown.content_score > 80.0
    assert opp.breakdown.source_score > 80.0
    assert any("High media rating" in s for s in opp.strengths)


def test_quality_engine_anti_inflation_high_ai_confidence_alone() -> None:
    engine = RecommendationQualityEngine()
    # Average media item with low popularity & average rating
    item = make_item(popularity=20.0, rating=5.0)
    # AI confidence = 100
    rec = make_recommendation(confidence=100.0)
    yt = None  # Missing YouTube source

    opp = engine.evaluate(rec, item, youtube_source=yt, performance_result=None)

    # Must NOT produce an Exceptional score (90+)!
    assert opp.final_score < 75
    assert opp.category != OpportunityCategory.EXCEPTIONAL
    assert any(
        "Direct YouTube clip candidate not available" in w for w in opp.weaknesses
    )


def test_quality_engine_neutral_history_for_new_account() -> None:
    engine = RecommendationQualityEngine()
    item = make_item(popularity=70.0, rating=8.0)
    rec = make_recommendation(confidence=90.0)

    opp = engine.evaluate(rec, item, youtube_source=None, performance_result=None)

    # Should have a sensible baseline without crashing or heavily penalizing
    assert 50 <= opp.final_score <= 80
    assert any("Limited account history" in w for w in opp.weaknesses)


def test_quality_engine_weak_item() -> None:
    engine = RecommendationQualityEngine()
    item = make_item(popularity=10.0, rating=3.0)
    rec = Recommendation(
        id="rec_weak",
        items=[item],
        target_audience="General",
        reasoning="Low appeal",
        confidence_score=40.0,
        content_strategy=None,
    )

    opp = engine.evaluate(rec, item, youtube_source=None, performance_result=None)

    assert opp.final_score < 60
    assert opp.category in (OpportunityCategory.AVERAGE, OpportunityCategory.WEAK)
    assert any(
        "Moderate media rating" in w or "Moderate short-form" in w
        for w in opp.weaknesses
    )
