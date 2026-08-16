from pydantic import BaseModel, ConfigDict, Field


class YouTubeSource(BaseModel):
    """
    Immutable representation of a discovered YouTube source video candidate.
    """

    model_config = ConfigDict(frozen=True)

    video_id: str = Field(..., description="YouTube video ID.")
    title: str = Field(..., description="Title of the YouTube video.")
    channel_name: str = Field(..., description="Name of the YouTube channel.")
    url: str = Field(..., description="Direct watch URL for the YouTube video.")
    thumbnail_url: str | None = Field(default=None, description="Thumbnail image URL.")
    duration: str | None = Field(
        default=None, description="ISO 8601 or formatted video duration."
    )
    published_at: str | None = Field(default=None, description="Publication timestamp.")
    view_count: int | None = Field(default=None, description="Total view count.")
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Computed relevance score (0-100)."
    )
    quality_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Computed quality score (0-100)."
    )
    selection_reason: str = Field(
        default="", description="Explanation of candidate selection."
    )
    timestamp_verified: bool = Field(
        default=False, description="Whether start/end timestamps are verified."
    )
    start_timestamp: str | None = Field(
        default=None, description="Verified scene start timestamp."
    )
    end_timestamp: str | None = Field(
        default=None, description="Verified scene end timestamp."
    )
