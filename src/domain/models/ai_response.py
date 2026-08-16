from pydantic import BaseModel, ConfigDict, Field, field_validator


class OnScreenText(BaseModel):
    """
    Structured representation of text to overlay on the video.
    """

    model_config = ConfigDict(frozen=True)

    opening: str = Field(
        ...,
        description="Text shown during the first few seconds of the video to grab attention.",
    )
    middle: str = Field(
        ...,
        description="Text shown during the middle of the video expanding on the premise.",
    )
    ending: str = Field(
        ...,
        description="Closing text or question shown near the end of the video.",
    )


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
    video_hook: str = Field(
        ...,
        description="A short, strong opening hook suitable for the first seconds of the video.",
    )
    on_screen_text: OnScreenText = Field(
        ...,
        description="Structured text overlays for opening, middle, and ending of the video.",
    )
    editing_instructions: str = Field(
        ...,
        description="Practical editing guidance (pacing, visual moments, text placement, ending style, etc. Do NOT include timestamps).",
    )
    caption: str = Field(
        ..., description="A viral-optimized, emotionally engaging social media caption."
    )
    hashtags: list[str] = Field(
        ...,
        description="List of exactly 5 highly relevant hashtags, e.g., ['#anime', '#movie', '#cinema', '#film', '#viral']",
    )
    first_comment: str = Field(
        ...,
        description="A natural first-comment idea designed to encourage genuine discussion.",
    )

    @field_validator("hashtags")
    @classmethod
    def validate_hashtags(cls, v: list[str]) -> list[str]:
        if len(v) != 5:
            raise ValueError(f"Exactly 5 hashtags are required, got {len(v)}.")
        cleaned = [h.strip() for h in v if h.strip()]
        if len(cleaned) != 5:
            raise ValueError("Hashtags cannot contain empty strings.")
        lowercased = [h.lower() for h in cleaned]
        if len(set(lowercased)) != 5:
            raise ValueError("Duplicate hashtags are not allowed.")
        return cleaned
