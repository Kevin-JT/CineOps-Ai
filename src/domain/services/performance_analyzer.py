import logging
from dataclasses import dataclass, field

from src.domain.models.performance import PerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceInsightResult:
    """
    Data structure containing deterministic performance analysis insights.
    """

    sample_size: int
    confidence: str  # "Low", "Medium", "High"
    has_enough_data: bool
    insights: list[str] = field(default_factory=list)
    formatted_summary: str = ""
    short_insight: str = ""


class PerformanceAnalyzer:
    """
    Domain service responsible for deterministic statistical analysis of historical content performance.
    Exposes confidence based on sample size and minimum data thresholds to prevent unwarranted AI conclusions.
    """

    def __init__(self, min_samples: int = 3) -> None:
        self.min_samples = min_samples

    def analyze_performance(
        self, records: list[PerformanceMetrics]
    ) -> PerformanceInsightResult:
        """
        Analyzes historical performance records and produces deterministic summary insights.
        """
        sample_size = len(records)

        if sample_size < self.min_samples:
            return PerformanceInsightResult(
                sample_size=sample_size,
                confidence="Low",
                has_enough_data=False,
                insights=[
                    f"Not enough performance data yet ({sample_size}/{self.min_samples} required posts)."
                ],
                formatted_summary="",
                short_insight="",
            )

        # Assign confidence based on sample size
        if sample_size < 5:
            confidence = "Low"
        elif sample_size <= 15:
            confidence = "Medium"
        else:
            confidence = "High"

        # Calculate average engagement rates
        valid_engagements = [
            r.engagement_rate for r in records if r.engagement_rate is not None
        ]
        avg_engagement = (
            sum(valid_engagements) / len(valid_engagements)
            if valid_engagements
            else 0.0
        )

        max_record = max(records, key=lambda r: r.views)

        # Platform breakdown
        platforms: dict[str, list[float]] = {}
        for r in records:
            if r.engagement_rate is not None:
                platforms.setdefault(r.platform, []).append(r.engagement_rate)

        platform_names = {
            "youtube": "YouTube",
            "instagram": "Instagram",
            "tiktok": "TikTok",
            "twitter": "Twitter",
            "other": "Other",
        }

        platform_summaries = []
        for plat, rates in platforms.items():
            if rates:
                avg_plat = sum(rates) / len(rates)
                display_name = platform_names.get(plat, plat.capitalize())
                platform_summaries.append(
                    f"{display_name}: avg {avg_plat:.1f}% engagement"
                )

        insights = [
            f"Posts analyzed: {sample_size} (Confidence: {confidence})",
            f"Average engagement rate across posts: {avg_engagement:.1f}%",
            f"Top performing post: {max_record.views:,} views on {max_record.platform}",
        ]
        if platform_summaries:
            insights.append("Platform breakdown: " + ", ".join(platform_summaries))

        formatted_summary = "PERFORMANCE INSIGHTS:\n" + "\n".join(
            f"- {item}" for item in insights
        )

        short_insight = (
            f"Based on {sample_size} previous posts ({confidence} confidence): "
            f"Average engagement is {avg_engagement:.1f}% across platforms."
        )

        return PerformanceInsightResult(
            sample_size=sample_size,
            confidence=confidence,
            has_enough_data=True,
            insights=insights,
            formatted_summary=formatted_summary,
            short_insight=short_insight,
        )
