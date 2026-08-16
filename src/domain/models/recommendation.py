from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.ai_response import OnScreenText
from src.domain.models.clip import ClipIntelligenceResult
from src.domain.models.media_item import MediaItem
from src.domain.models.quality import OpportunityScore
from src.domain.models.youtube import YouTubeSource


class ContentStrategy(BaseModel):
    """
    Short-form video content strategy details for Reel/Short creation.
    """

    model_config = ConfigDict(frozen=True)

    video_hook: str
    on_screen_text: OnScreenText
    editing_instructions: str
    caption: str
    hashtags: list[str]
    first_comment: str


class Recommendation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    items: list[MediaItem]
    target_audience: str
    reasoning: str
    confidence_score: float = 0.0
    viral_score: float = 0.0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_strategy: ContentStrategy | None = None
    youtube_source: YouTubeSource | None = None
    opportunity_score: OpportunityScore | None = None
    clip_intelligence: ClipIntelligenceResult | None = None


import uuid


@dataclass
class RecommendationLog:
    """Domain model for persisting AI generation logs."""

    prompt: str
    response: str
    model: str
    response_time: float
    status: str
    id: uuid.UUID | None = None
    created_at: datetime | None = None
