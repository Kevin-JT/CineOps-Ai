from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ClipVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class ClipSegment(BaseModel):
    """
    Immutable representation of an analyzed clip segment.
    """

    model_config = ConfigDict(frozen=True)

    source_video_id: str = Field(..., description="YouTube video ID.")
    source_url: str = Field(..., description="YouTube video URL.")
    scene_description: str = Field(
        ..., description="Description of the scene or moment."
    )
    match_reason: str = Field(
        ...,
        description="Explanation of why this clip matches the content strategy.",
    )
    clip_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Clip quality score (0-100)."
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Clip verification confidence (0-100).",
    )
    verification_status: ClipVerificationStatus = Field(
        default=ClipVerificationStatus.UNVERIFIED, description="Verification status."
    )
    timestamp_verified: bool = Field(
        default=False,
        description="Whether start and end timestamps are backed by verified timing evidence.",
    )
    start_timestamp: str | None = Field(
        default=None, description="Start timestamp string (e.g., '03:12')."
    )
    end_timestamp: str | None = Field(
        default=None, description="End timestamp string (e.g., '03:31')."
    )
    duration_seconds: int | None = Field(
        default=None, description="Clip duration in seconds."
    )


class ClipIntelligenceResult(BaseModel):
    """
    Immutable container for clip intelligence analysis results.
    """

    model_config = ConfigDict(frozen=True)

    best_clip: ClipSegment = Field(
        ..., description="The highest scoring selected clip segment."
    )
    alternative_clips: list[ClipSegment] = Field(
        default_factory=list, description="Alternative evaluated clip segments."
    )
    transcript_available: bool = Field(
        default=False,
        description="Whether source transcript timing evidence was available.",
    )
