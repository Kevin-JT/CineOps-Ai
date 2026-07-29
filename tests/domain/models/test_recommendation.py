from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation


def test_recommendation_creation() -> None:
    item = MediaItem(
        id="123",
        title="Test Movie",
        overview="Overview",
        media_type="movie",
    )

    rec = Recommendation(
        id="rec_1",
        items=[item],
        target_audience="General",
        reasoning="Because it's good",
        viral_score=85.5,
    )

    assert rec.id == "rec_1"
    assert len(rec.items) == 1
    assert rec.items[0].id == "123"
    assert rec.target_audience == "General"
    assert rec.reasoning == "Because it's good"
    assert rec.viral_score == 85.5
    assert rec.generated_at is not None
