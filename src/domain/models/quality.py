from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OpportunityCategory(str, Enum):
    EXCEPTIONAL = "EXCEPTIONAL"  # 90 - 100
    STRONG = "STRONG"  # 75 - 89
    PROMISING = "PROMISING"  # 60 - 74
    AVERAGE = "AVERAGE"  # 45 - 59
    WEAK = "WEAK"  # 0 - 44


class OpportunityScoreBreakdown(BaseModel):
    """
    Detailed score breakdown across the core quality dimensions (0-100 scale each).
    """

    model_config = ConfigDict(frozen=True)

    content_score: float = Field(
        ..., ge=0.0, le=100.0, description="Content potential score."
    )
    short_form_score: float = Field(
        ..., ge=0.0, le=100.0, description="Short-form strategy potential score."
    )
    source_score: float = Field(
        ..., ge=0.0, le=100.0, description="YouTube source quality score."
    )
    historical_score: float = Field(
        ..., ge=0.0, le=100.0, description="Historical performance evidence score."
    )


class OpportunityScore(BaseModel):
    """
    Immutable final quality score and explainability result.
    """

    model_config = ConfigDict(frozen=True)

    final_score: int = Field(
        ..., ge=0, le=100, description="Final opportunity score (0-100)."
    )
    category: OpportunityCategory = Field(..., description="Classification category.")
    breakdown: OpportunityScoreBreakdown = Field(
        ..., description="Category breakdown scores."
    )
    strengths: list[str] = Field(
        default_factory=list, description="Verifiable strong signals."
    )
    weaknesses: list[str] = Field(
        default_factory=list, description="Verifiable weak signals or limitations."
    )
