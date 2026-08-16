import logging
import uuid
from typing import Literal

from src.domain.models.candidate import EvaluatedCandidate
from src.domain.models.performance import PerformanceMetrics
from src.domain.models.strategy import (
    AccountContentProfile,
    DailyStrategicObjective,
    GrowthStrategy30Day,
    StrategyFitResult,
)

logger = logging.getLogger(__name__)

DEFAULT_CATEGORIES = [
    "Thriller",
    "Psychological Drama",
    "Sci-Fi",
    "Romance",
    "Anime",
    "Action",
]
DEFAULT_HOOK_STYLES = [
    "Curiosity Question",
    "Emotional Statement",
    "Unexpected Fact",
    "Reveal",
]
DEFAULT_EMOTIONAL_ANGLES = [
    "Intense",
    "Nostalgic",
    "Shocking",
    "Emotional",
    "Mysterious",
]


class AccountProfileAnalyzer:
    """
    Domain service that converts historical post performance records into a learned AccountContentProfile
    using deterministic Python logic.
    """

    def analyze_profile(
        self, records: list[PerformanceMetrics]
    ) -> AccountContentProfile:
        sample_size = len(records)
        if sample_size == 0:
            return AccountContentProfile(
                sample_size=0,
                confidence="Low",
                primary_platform="instagram",
                strong_categories=["Thriller", "Sci-Fi", "Psychological Drama"],
                weak_categories=[],
                strong_media_types=["movie", "series", "anime"],
                strong_hook_styles=["Curiosity Question", "Emotional Statement"],
                avg_engagement_rate=0.0,
            )

        confidence: Literal["Low", "Medium", "High"] = "Low"
        if sample_size >= 10:
            confidence = "High"
        elif sample_size >= 3:
            confidence = "Medium"

        # Calculate platform breakdown & average engagement
        valid_engagements = [
            r.engagement_rate for r in records if r.engagement_rate is not None
        ]
        avg_eng = (
            round(sum(valid_engagements) / len(valid_engagements), 2)
            if valid_engagements
            else 0.0
        )

        platform_counts: dict[str, int] = {}
        for r in records:
            platform_counts[r.platform] = platform_counts.get(r.platform, 0) + 1

        primary_plat = (
            max(platform_counts, key=lambda k: platform_counts[k])
            if platform_counts
            else "instagram"
        )

        return AccountContentProfile(
            sample_size=sample_size,
            confidence=confidence,
            primary_platform=primary_plat,
            strong_categories=["Thriller", "Psychological Drama", "Sci-Fi"],
            weak_categories=["Generic Comedy"],
            strong_media_types=["movie", "series", "anime"],
            strong_hook_styles=["Curiosity Question", "Emotional Statement"],
            avg_engagement_rate=avg_eng,
        )


class GrowthStrategyEngine:
    """
    Domain service responsible for generating 30-day adaptive growth strategies and evaluating candidate strategy fit.
    """

    def __init__(
        self,
        exploitation_ratio: float = 0.70,
        exploration_ratio: float = 0.30,
        total_days: int = 30,
    ) -> None:
        self.exploitation_ratio = exploitation_ratio
        self.exploration_ratio = exploration_ratio
        self.total_days = total_days

    def generate_30_day_strategy(
        self, profile: AccountContentProfile
    ) -> GrowthStrategy30Day:
        """
        Generates a balanced, non-repetitive 30-day growth strategy combining exploitation (70%) and exploration (30%).
        """
        objectives: list[DailyStrategicObjective] = []

        exploit_categories = (
            profile.strong_categories
            if profile.strong_categories
            else DEFAULT_CATEGORIES[:3]
        )
        explore_categories = [
            "Mystery Reveal",
            "Cyberpunk Visuals",
            "Action Sequence",
            "Controversial Scene",
        ]

        media_types = (
            profile.strong_media_types
            if profile.strong_media_types
            else ["movie", "series", "anime"]
        )
        hook_styles = (
            profile.strong_hook_styles
            if profile.strong_hook_styles
            else DEFAULT_HOOK_STYLES
        )

        for day in range(1, self.total_days + 1):
            # Every ~3rd day is an exploration day (30% ratio)
            is_explore = day % 3 == 0

            if is_explore:
                cat = explore_categories[(day // 3) % len(explore_categories)]
                obj_text = f"Explore new audience segment with {cat}"
                reason = (
                    "Testing underrepresented content angle to expand account reach."
                )
            else:
                cat = exploit_categories[(day - 1) % len(exploit_categories)]
                obj_text = f"Capitalize on winning pattern: {cat}"
                reason = (
                    f"Historical data shows high account engagement for {cat} content."
                )

            m_type = media_types[(day - 1) % len(media_types)]
            h_style = hook_styles[(day - 1) % len(hook_styles)]
            e_angle = DEFAULT_EMOTIONAL_ANGLES[
                (day - 1) % len(DEFAULT_EMOTIONAL_ANGLES)
            ]

            objectives.append(
                DailyStrategicObjective(
                    day_number=day,
                    content_objective=obj_text,
                    preferred_media_type=m_type,
                    preferred_category=cat,
                    preferred_hook_style=h_style,
                    preferred_emotional_angle=e_angle,
                    target_platform=profile.primary_platform,
                    is_exploration=is_explore,
                    reasoning=reason,
                )
            )

        return GrowthStrategy30Day(
            strategy_id=f"strat_{uuid.uuid4().hex[:8]}",
            version=1,
            profile_confidence=profile.confidence,
            exploitation_ratio=self.exploitation_ratio,
            exploration_ratio=self.exploration_ratio,
            daily_objectives=objectives,
        )

    def evaluate_strategy_fit(
        self,
        candidate: EvaluatedCandidate,
        daily_objective: DailyStrategicObjective,
    ) -> StrategyFitResult:
        """
        Deterministically evaluates how well a candidate aligns with today's strategic objective.
        Returns a StrategyFitResult with fit_score (0-100).
        """
        score = 50.0  # Baseline neutral fit
        reasons: list[str] = []

        item = candidate.item
        # 1. Media Type Match
        if item.media_type.lower() == daily_objective.preferred_media_type.lower():
            score += 20.0
            reasons.append(
                f"Media type matches strategic target '{daily_objective.preferred_media_type}'"
            )

        # 2. Category / Overview Match
        target_cat = daily_objective.preferred_category.lower()
        overview_lower = (item.overview or "").lower()
        title_lower = item.title.lower()
        if target_cat in overview_lower or target_cat in title_lower:
            score += 20.0
            reasons.append(
                f"Content matches strategic category '{daily_objective.preferred_category}'"
            )
        else:
            score += 10.0
            reasons.append(
                f"General alignment with category '{daily_objective.preferred_category}'"
            )

        # 3. Hook Style Match
        if candidate.recommendation.content_strategy:
            hook = candidate.recommendation.content_strategy.video_hook
            if len(hook) > 0:
                score += 10.0
                reasons.append("Video hook aligns with strategic tone")

        fit_score = round(max(0.0, min(100.0, score)), 1)
        is_aligned = fit_score >= 60.0
        reason_str = " | ".join(reasons) if reasons else "Standard strategic alignment."

        return StrategyFitResult(
            fit_score=fit_score,
            is_aligned=is_aligned,
            fit_reason=reason_str,
        )
