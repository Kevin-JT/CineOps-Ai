from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PerformanceMetrics(BaseModel):
    """
    Domain model representing post performance metrics for a published recommendation.
    """

    model_config = ConfigDict(frozen=True)

    recommendation_id: str = Field(
        ..., description="ID of the recommendation or media item."
    )
    platform: Literal["instagram", "youtube", "tiktok", "twitter", "other"] = Field(
        ..., description="Social media platform."
    )
    published_at: datetime | None = Field(
        default=None, description="Publication timestamp."
    )
    views: int = Field(..., ge=0, description="Total view count.")
    likes: int | None = Field(default=None, ge=0, description="Total likes count.")
    comments: int | None = Field(
        default=None, ge=0, description="Total comments count."
    )
    shares: int | None = Field(default=None, ge=0, description="Total shares count.")
    saves: int | None = Field(default=None, ge=0, description="Total saves count.")
    retention_rate: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Retention rate percentage (0-100)."
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Record creation timestamp.",
    )

    @property
    def engagement_rate(self) -> float | None:
        """
        Calculates engagement rate percentage: (likes + comments + shares + saves) / views * 100.
        Returns None if views == 0 or no metrics exist.
        """
        if self.views <= 0:
            return None

        metrics = [self.likes, self.comments, self.shares, self.saves]
        valid_metrics = [m for m in metrics if m is not None]
        if not valid_metrics:
            return None

        total_engagement = sum(valid_metrics)
        return round((total_engagement / self.views) * 100.0, 2)

    @property
    def comment_rate(self) -> float | None:
        if self.views <= 0 or self.comments is None:
            return None
        return round((self.comments / self.views) * 100.0, 2)

    @property
    def share_rate(self) -> float | None:
        if self.views <= 0 or self.shares is None:
            return None
        return round((self.shares / self.views) * 100.0, 2)

    @property
    def like_rate(self) -> float | None:
        if self.views <= 0 or self.likes is None:
            return None
        return round((self.likes / self.views) * 100.0, 2)
