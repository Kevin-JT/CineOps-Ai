import pytest

from src.domain.models.media_item import MediaItem
from src.domain.services.ranking import RankingService


@pytest.fixture
def items() -> list[MediaItem]:
    return [
        MediaItem(
            id="1",
            title="A",
            overview="",
            media_type="movie",
            rating=6.0,
            popularity=100.0,
        ),
        MediaItem(
            id="2",
            title="B",
            overview="",
            media_type="movie",
            rating=9.0,
            popularity=50.0,
        ),
        MediaItem(
            id="3",
            title="C",
            overview="",
            media_type="movie",
            rating=8.0,
            popularity=200.0,
        ),
    ]


def test_rank_by_rating(items: list[MediaItem]) -> None:
    ranked = RankingService.rank_by_rating(items)
    assert [i.id for i in ranked] == ["2", "3", "1"]

    ranked_asc = RankingService.rank_by_rating(items, descending=False)
    assert [i.id for i in ranked_asc] == ["1", "3", "2"]


def test_rank_by_popularity(items: list[MediaItem]) -> None:
    ranked = RankingService.rank_by_popularity(items)
    assert [i.id for i in ranked] == ["3", "1", "2"]

    ranked_asc = RankingService.rank_by_popularity(items, descending=False)
    assert [i.id for i in ranked_asc] == ["2", "1", "3"]
