from src.domain.models.ai_response import OnScreenText
from src.domain.models.candidate import EvaluatedCandidate
from src.domain.models.media_item import MediaItem
from src.domain.models.performance import PerformanceMetrics
from src.domain.models.quality import (
    OpportunityCategory,
    OpportunityScore,
    OpportunityScoreBreakdown,
)
from src.domain.models.recommendation import ContentStrategy, Recommendation
from src.domain.services.strategy_engine import (
    AccountProfileAnalyzer,
    GrowthStrategyEngine,
)


def make_candidate(
    title: str = "Interstellar", media_type: str = "movie", score: int = 90
) -> EvaluatedCandidate:
    item = MediaItem(
        id="m1",
        title=title,
        overview="Thriller in space",
        media_type=media_type,
        rating=8.5,
        popularity=80.0,
    )
    strategy = ContentStrategy(
        video_hook="No, it's necessary.",
        on_screen_text=OnScreenText(opening="O", middle="M", ending="E"),
        editing_instructions="Cut fast",
        caption="Epic sci-fi",
        hashtags=["#a", "#b", "#c", "#d", "#e"],
        first_comment="Great scene!",
    )
    rec = Recommendation(
        id="rec_m1",
        items=[item],
        target_audience="General",
        reasoning="Why now",
        confidence_score=90.0,
        content_strategy=strategy,
    )
    opp = OpportunityScore(
        final_score=score,
        category=OpportunityCategory.EXCEPTIONAL,
        breakdown=OpportunityScoreBreakdown(
            content_score=float(score),
            short_form_score=float(score),
            source_score=50.0,
            historical_score=50.0,
        ),
    )
    return EvaluatedCandidate(item=item, recommendation=rec, opportunity_score=opp)


def test_account_profile_analyzer_empty_history() -> None:
    analyzer = AccountProfileAnalyzer()
    profile = analyzer.analyze_profile([])

    assert profile.sample_size == 0
    assert profile.confidence == "Low"
    assert "Thriller" in profile.strong_categories


def test_account_profile_analyzer_medium_and_high_confidence() -> None:
    analyzer = AccountProfileAnalyzer()
    records = [
        PerformanceMetrics(
            recommendation_id=f"r{i}", platform="instagram", views=1000, likes=100
        )
        for i in range(12)
    ]

    profile = analyzer.analyze_profile(records)
    assert profile.sample_size == 12
    assert profile.confidence == "High"
    assert profile.avg_engagement_rate > 0.0


def test_growth_strategy_engine_30_day_generation() -> None:
    engine = GrowthStrategyEngine(total_days=30)
    analyzer = AccountProfileAnalyzer()
    profile = analyzer.analyze_profile([])

    strategy = engine.generate_30_day_strategy(profile)

    assert len(strategy.daily_objectives) == 30
    assert strategy.get_day_objective(1).day_number == 1
    assert strategy.get_day_objective(35).day_number == 5  # Wraps around day 5

    exploration_days = [obj for obj in strategy.daily_objectives if obj.is_exploration]
    exploitation_days = [
        obj for obj in strategy.daily_objectives if not obj.is_exploration
    ]

    assert len(exploration_days) > 0
    assert len(exploitation_days) > len(exploration_days)


def test_strategy_fit_evaluation() -> None:
    engine = GrowthStrategyEngine()
    cand = make_candidate(title="Dark Knight", media_type="movie", score=88)

    analyzer = AccountProfileAnalyzer()
    profile = analyzer.analyze_profile([])
    strategy_30d = engine.generate_30_day_strategy(profile)
    obj = strategy_30d.get_day_objective(1)

    fit_res = engine.evaluate_strategy_fit(cand, obj)

    assert 0.0 <= fit_res.fit_score <= 100.0
    assert isinstance(fit_res.is_aligned, bool)
    assert len(fit_res.fit_reason) > 0
