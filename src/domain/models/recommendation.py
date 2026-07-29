from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.media_item import MediaItem


class Recommendation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    items: list[MediaItem]
    target_audience: str
    reasoning: str
    confidence_score: float = 0.0
    viral_score: float = 0.0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
