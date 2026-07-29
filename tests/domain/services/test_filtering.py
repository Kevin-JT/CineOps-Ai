import pytest

from src.domain.models.media_item import MediaItem
from src.domain.services.filtering import MediaFilterService


@pytest.fixture
def items() -> list[MediaItem]:
    return [
        MediaItem(
            id="1",
            title="Good Movie",
            overview="...",
            media_type="movie",
            rating=8.0,
            genres=["Action", "Sci-Fi"],
        ),
        MediaItem(
            id="2",
            title="Bad Movie",
            overview="...",
            media_type="movie",
            rating=4.0,
            genres=["Comedy"],
        ),
        MediaItem(
            id="3",
            title="Unknown Title",
            overview="...",
            media_type="movie",
            rating=9.0,
            genres=["Drama"],
        ),
        MediaItem(
            id="4",
            title="Okay Anime",
            overview="...",
            media_type="anime",
            rating=7.0,
            genres=["Action", "Fantasy"],
        ),
        MediaItem(id="5", title="", overview="...", media_type="movie", rating=9.0),
    ]


def test_filter_by_min_rating(items: list[MediaItem]) -> None:
    service = MediaFilterService(min_rating=7.5)
    filtered = service.filter_items(items)

    assert len(filtered) == 1
    assert filtered[0].title == "Good Movie"


def test_filter_by_required_genres(items: list[MediaItem]) -> None:
    service = MediaFilterService(required_genres=["Action"])
    filtered = service.filter_items(items)

    assert len(filtered) == 2
    assert {i.title for i in filtered} == {"Good Movie", "Okay Anime"}


def test_filter_invalid_items(items: list[MediaItem]) -> None:
    service = MediaFilterService()
    filtered = service.filter_items(items)

    # Should exclude item "3" (Unknown Title) and "5" (empty title)
    assert len(filtered) == 3
    assert "Unknown Title" not in {i.title for i in filtered}
    assert "" not in {i.title for i in filtered}
