from src.domain.models.scoring import ViralScore, ViralScoreFactors


class ViralScoringService:
    """
    Service responsible for calculating the viral score of a media item
    based on the weighted factors defined in the architecture.
    """

    # Weights defined by business rules (must sum to 1.0)
    WEIGHT_POPULARITY = 0.30
    WEIGHT_RATING = 0.20
    WEIGHT_RECOGNITION = 0.15
    WEIGHT_VISUAL = 0.15
    WEIGHT_EMOTIONAL = 0.10
    WEIGHT_SOCIAL = 0.10

    def calculate_score(self, factors: ViralScoreFactors) -> ViralScore:
        """
        Calculates the final viral score.

        Args:
            factors: The components of the viral score.

        Returns:
            A ViralScore object with the computed final score.
        """
        # Normalize rating from 0-10 scale to 0-100 scale
        normalized_rating = factors.rating * 10.0

        score = (
            (factors.popularity * self.WEIGHT_POPULARITY)
            + (normalized_rating * self.WEIGHT_RATING)
            + (factors.recognition * self.WEIGHT_RECOGNITION)
            + (factors.visual_impact * self.WEIGHT_VISUAL)
            + (factors.emotional_impact * self.WEIGHT_EMOTIONAL)
            + (factors.social_potential * self.WEIGHT_SOCIAL)
        )

        return ViralScore(score=round(score, 2), factors=factors)
