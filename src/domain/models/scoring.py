from pydantic import BaseModel, ConfigDict, Field


class ViralScoreFactors(BaseModel):
    """
    Immutable representation of the factors contributing to a viral score.
    Values should ideally be normalized between 0 and 100.
    """

    model_config = ConfigDict(frozen=True)

    popularity: float = Field(default=0.0, ge=0.0, le=100.0)
    rating: float = Field(default=0.0, ge=0.0, le=10.0)
    recognition: float = Field(default=0.0, ge=0.0, le=100.0)
    visual_impact: float = Field(default=0.0, ge=0.0, le=100.0)
    emotional_impact: float = Field(default=0.0, ge=0.0, le=100.0)
    social_potential: float = Field(default=0.0, ge=0.0, le=100.0)


class ViralScore(BaseModel):
    """
    Immutable representation of a final calculated viral score.
    """

    model_config = ConfigDict(frozen=True)

    score: float = Field(..., ge=0.0, le=100.0)
    factors: ViralScoreFactors
