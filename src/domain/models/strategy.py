from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AccountContentProfile(BaseModel):
    """
    Immutable representation of the account's learned performance profile.
    """

    model_config = ConfigDict(frozen=True)

    sample_size: int = Field(
        default=0, ge=0, description="Total post performance records analyzed."
    )
    confidence: Literal["Low", "Medium", "High"] = Field(
        default="Low", description="Statistical confidence level."
    )
    primary_platform: str = Field(
        default="instagram", description="Highest performing platform."
    )
    strong_categories: list[str] = Field(
        default_factory=list,
        description="Historically high-performing categories/genres.",
    )
    weak_categories: list[str] = Field(
        default_factory=list, description="Historically lower-performing categories."
    )
    strong_media_types: list[str] = Field(
        default_factory=list,
        description="Strongest media types (movie, series, anime).",
    )
    strong_hook_styles: list[str] = Field(
        default_factory=list, description="Preferred video hook styles."
    )
    avg_engagement_rate: float = Field(
        default=0.0, ge=0.0, description="Average engagement rate percentage."
    )
    analyzed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Analysis timestamp."
    )


class DailyStrategicObjective(BaseModel):
    """
    Immutable strategic objective for a specific day in the growth calendar.
    """

    model_config = ConfigDict(frozen=True)

    day_number: int = Field(..., ge=1, le=30, description="Day number (1-30).")
    content_objective: str = Field(..., description="High-level goal for the post.")
    preferred_media_type: str = Field(
        default="movie", description="Target media type (movie, tv, anime)."
    )
    preferred_category: str = Field(..., description="Target category/genre.")
    preferred_hook_style: str = Field(..., description="Target video hook style.")
    preferred_emotional_angle: str = Field(
        ..., description="Target emotional tone/angle."
    )
    target_platform: str = Field(
        default="instagram", description="Target publishing platform."
    )
    is_exploration: bool = Field(
        default=False,
        description="Whether this day tests an exploratory pattern vs exploiting winning patterns.",
    )
    reasoning: str = Field(
        ..., description="Strategic justification for this objective."
    )


class GrowthStrategy30Day(BaseModel):
    """
    Immutable container for the 30-day growth strategy plan.
    """

    model_config = ConfigDict(frozen=True)

    strategy_id: str = Field(..., description="Unique strategy plan ID.")
    version: int = Field(default=1, description="Strategy version number.")
    profile_confidence: Literal["Low", "Medium", "High"] = Field(
        default="Low", description="Profile confidence used to construct this plan."
    )
    exploitation_ratio: float = Field(
        default=0.70, description="Ratio of exploitation days."
    )
    exploration_ratio: float = Field(
        default=0.30, description="Ratio of exploration days."
    )
    daily_objectives: list[DailyStrategicObjective] = Field(
        ..., description="List of 30 daily strategic objectives."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Plan creation timestamp.",
    )

    def get_day_objective(self, day: int) -> DailyStrategicObjective:
        """Retrieves objective for specified day number (1-30, wrapping around if >30)."""
        clamped_day = ((day - 1) % len(self.daily_objectives)) + 1
        for obj in self.daily_objectives:
            if obj.day_number == clamped_day:
                return obj
        return self.daily_objectives[0]


class StrategyFitResult(BaseModel):
    """
    Immutable evaluation of how well a candidate aligns with today's strategic objective.
    """

    model_config = ConfigDict(frozen=True)

    fit_score: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Deterministic strategy fit score (0-100).",
    )
    is_aligned: bool = Field(
        default=True,
        description="Whether candidate satisfies core strategic parameters.",
    )
    fit_reason: str = Field(..., description="Explanation of strategy fit evaluation.")
