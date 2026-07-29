from pydantic import BaseModel, ConfigDict, Field


class AIRecommendationResponse(BaseModel):
    """
    Strict JSON schema definition for AI provider output validation.
    """

    model_config = ConfigDict(frozen=True)

    selected_id: str = Field(..., description="The exact ID of the chosen media item.")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence level (0-100) of this recommendation's potential.",
    )
    target_audience: str = Field(..., description="The primary target demographic.")
    reasoning_why_now: str = Field(
        ..., description="Explanation of why this item is trending right now."
    )
    reasoning_audience_appeal: str = Field(
        ..., description="Explanation of why the audience will engage with it."
    )
    caption: str = Field(..., description="A viral-optimized social media caption.")
    hashtags: list[str] = Field(
        ..., description="List of highly relevant hashtags, e.g., ['#viral', '#movie']"
    )
