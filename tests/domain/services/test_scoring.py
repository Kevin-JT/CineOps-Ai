from src.domain.models.scoring import ViralScoreFactors
from src.domain.services.scoring import ViralScoringService


def test_calculate_score() -> None:
    service = ViralScoringService()

    factors = ViralScoreFactors(
        popularity=80.0,
        rating=8.5,
        recognition=50.0,
        visual_impact=70.0,
        emotional_impact=60.0,
        social_potential=90.0,
    )

    score = service.calculate_score(factors)

    # Calculation:
    # 80 * 0.30 = 24.0
    # 85 * 0.20 = 17.0
    # 50 * 0.15 = 7.5
    # 70 * 0.15 = 10.5
    # 60 * 0.10 = 6.0
    # 90 * 0.10 = 9.0
    # Total = 74.0

    assert score.score == 74.0
    assert score.factors == factors


def test_calculate_score_minimums() -> None:
    service = ViralScoringService()
    factors = ViralScoreFactors()
    score = service.calculate_score(factors)
    assert score.score == 0.0


def test_calculate_score_maximums() -> None:
    service = ViralScoringService()
    factors = ViralScoreFactors(
        popularity=100.0,
        rating=10.0,
        recognition=100.0,
        visual_impact=100.0,
        emotional_impact=100.0,
        social_potential=100.0,
    )
    score = service.calculate_score(factors)
    assert score.score == 100.0
