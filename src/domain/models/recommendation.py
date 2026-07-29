from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from src.domain.models.media_item import MediaItem

class Recommendation(BaseModel):
    id: str
    items: List[MediaItem]
    target_audience: str
    reasoning: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
