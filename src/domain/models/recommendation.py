from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.models.media_item import MediaItem


class Recommendation(BaseModel):
    id: str
    items: list[MediaItem]
    target_audience: str
    reasoning: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
