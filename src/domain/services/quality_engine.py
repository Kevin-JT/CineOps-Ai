import logging
from dataclasses import dataclass

from src.domain.models.media_item import MediaItem
from src.domain.models.quality import (
    OpportunityCategory,
    OpportunityScore,
    OpportunityScoreBreakdown,
)
from src.domain.models.recommendation import Recommendation
from src.domain.models.youtube import YouTubeSource
from src.domain.services.performance_analyzer import PerformanceInsightResult

logger = logging.getLogger(__name__)


@dataclass
class QualityEngineWeights:
    content_weight: float = 0.30
    short_form_weight: float = 0.35
    source_weight: float = 0.20
    historical_weight: float = 0.15


class RecommendationQualityEngine:
    """
    Domain service responsible for deterministic evaluation and ranking of content opportunities.
    Combines content potential, short-form strategy quality, YouTube source metrics, and historical performance.
    """

    def __init__(self, weights: QualityEngineWeights | None = None) -> None:
        self.weights = weights or QualityEngineWeights()

    def evaluate(
        self,
        recommendation: Recommendation,
        selected_item: MediaItem,
        youtube_source: YouTubeSource | None = None,
        performance_result: PerformanceInsightResult | None = None,
    ) -> OpportunityScore:
        """
        Evaluates a recommendation across four normalized dimensions (0-100) and produces an explainable OpportunityScore.
        """
        # 1. Content Potential Score (0-100)
        content_score = self._calculate_content_score(selected_item)

        # 2. Short-Form Potential Score (0-100)
        short_form_score = self._calculate_short_form_score(recommendation)

        # 3. Source Quality Score (0-100)
        source_score = self._calculate_source_score(youtube_source)

        # 4. Historical Evidence Score (0-100)
        historical_score, is_neutral_history = self._calculate_historical_score(
            performance_result, default_score=(content_score + short_form_score) / 2.0
        )

        # Calculate weighted final score
        raw_final = (
            (content_score * self.weights.content_weight)
            + (short_form_score * self.weights.short_form_weight)
            + (source_score * self.weights.source_weight)
            + (historical_score * self.weights.historical_weight)
        )

        final_score = round(max(0.0, min(100.0, raw_final)))

        # Classify into category
        category = self._classify_category(final_score)

        # Generate verifiable strengths and weaknesses
        strengths, weaknesses = self._generate_explanations(
            content_score=content_score,
            short_form_score=short_form_score,
            source_score=source_score,
            historical_score=historical_score,
            is_neutral_history=is_neutral_history,
            recommendation=recommendation,
            selected_item=selected_item,
            youtube_source=youtube_source,
            performance_result=performance_result,
        )

        breakdown = OpportunityScoreBreakdown(
            content_score=round(content_score, 1),
            short_form_score=round(short_form_score, 1),
            source_score=round(source_score, 1),
            historical_score=round(historical_score, 1),
        )

        return OpportunityScore(
            final_score=final_score,
            category=category,
            breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
        )

    def _calculate_content_score(self, item: MediaItem) -> float:
        pop = min(item.popularity, 100.0)
        rat = min(item.rating * 10.0, 100.0)
        score = (pop * 0.40) + (rat * 0.60)
        return max(0.0, min(100.0, score))

    def _calculate_short_form_score(self, rec: Recommendation) -> float:
        # AI confidence is capped to max 25% weight of short-form potential so it doesn't dominate!
        ai_conf_contrib = min(rec.confidence_score, 100.0) * 0.25

        strategy_contrib = 0.0
        if rec.content_strategy:
            st = rec.content_strategy
            if st.video_hook and len(st.video_hook) < 70:
                strategy_contrib += 35.0
            elif st.video_hook:
                strategy_contrib += 20.0

            if st.on_screen_text and st.on_screen_text.opening:
                strategy_contrib += 20.0

            if st.editing_instructions:
                strategy_contrib += 10.0

            if len(st.hashtags) == 5:
                strategy_contrib += 10.0
        else:
            strategy_contrib = 30.0

        total = ai_conf_contrib + strategy_contrib
        return max(0.0, min(100.0, total))

    def _calculate_source_score(self, yt: YouTubeSource | None) -> float:
        if not yt:
            # Baseline neutral score for missing source
            return 45.0

        score = (yt.relevance_score * 0.60) + (yt.quality_score * 0.30)
        if yt.timestamp_verified:
            score += 10.0

        return max(0.0, min(100.0, score))

    def _calculate_historical_score(
        self,
        performance_result: PerformanceInsightResult | None,
        default_score: float,
    ) -> tuple[float, bool]:
        if not performance_result or not performance_result.has_enough_data:
            # Return baseline so new accounts are not penalized!
            return max(0.0, min(100.0, default_score)), True

        score = 75.0
        if performance_result.confidence == "Medium":
            score += 5.0
        elif performance_result.confidence == "High":
            score += 10.0

        return max(0.0, min(100.0, score)), False

    def _classify_category(self, score: int) -> OpportunityCategory:
        if score >= 90:
            return OpportunityCategory.EXCEPTIONAL
        if score >= 75:
            return OpportunityCategory.STRONG
        if score >= 60:
            return OpportunityCategory.PROMISING
        if score >= 45:
            return OpportunityCategory.AVERAGE
        return OpportunityCategory.WEAK

    def _generate_explanations(
        self,
        content_score: float,
        short_form_score: float,
        source_score: float,
        historical_score: float,
        is_neutral_history: bool,
        recommendation: Recommendation,
        selected_item: MediaItem,
        youtube_source: YouTubeSource | None,
        performance_result: PerformanceInsightResult | None,
    ) -> tuple[list[str], list[str]]:
        strengths: list[str] = []
        weaknesses: list[str] = []

        if content_score >= 80.0:
            strengths.append(
                f"High media rating ({selected_item.rating}/10) and audience popularity"
            )
        elif content_score < 60.0:
            weaknesses.append("Moderate media rating or popularity score")

        if short_form_score >= 80.0:
            strengths.append("Strong video hook and complete editing strategy")
        elif short_form_score < 65.0:
            weaknesses.append("Moderate short-form content strategy impact")

        if youtube_source:
            if youtube_source.relevance_score >= 75.0:
                strengths.append(
                    f"High-relevance YouTube clip candidate ({int(youtube_source.relevance_score)}/100)"
                )
            if not youtube_source.timestamp_verified:
                weaknesses.append("Clip timestamp not verified")
        else:
            weaknesses.append("Direct YouTube clip candidate not available")

        if is_neutral_history:
            weaknesses.append("Limited account history (new account neutral baseline)")
        elif historical_score >= 80.0:
            strengths.append("Historical account engagement supports format success")

        return strengths, weaknesses
