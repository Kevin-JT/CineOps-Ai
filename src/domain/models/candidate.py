from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.media_item import MediaItem
from src.domain.models.quality import OpportunityScore
from src.domain.models.recommendation import Recommendation


class EvaluatedCandidate(BaseModel):
    """
    Immutable domain representation of an independently evaluated recommendation candidate.
    """

    model_config = ConfigDict(frozen=True)

    item: MediaItem = Field(..., description="Target media item.")
    recommendation: Recommendation = Field(
        ..., description="Generated AI recommendation and content strategy."
    )
    opportunity_score: OpportunityScore = Field(
        ..., description="Evaluated quality and opportunity score."
    )
