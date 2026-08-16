import httpx
import pytest
import respx

from src.domain.models.youtube import YouTubeSource
from src.infrastructure.providers.youtube_provider import YouTubeProvider


@pytest.fixture
def provider() -> YouTubeProvider:
    return YouTubeProvider(
        api_key="test_yt_key",
        client=httpx.AsyncClient(),
        timeout=1.0,
    )


@pytest.mark.asyncio
async def test_youtube_search_missing_key() -> None:
    provider = YouTubeProvider(api_key=None, client=httpx.AsyncClient())
    result = await provider.search_source("Interstellar", "movie")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_youtube_search_success(provider: YouTubeProvider) -> None:
    url = f"{provider.BASE_URL}/search"

    mock_response = {
        "items": [
            {
                "id": {"videoId": "abc12345"},
                "snippet": {
                    "title": "Interstellar Docking Scene 4K HD",
                    "channelTitle": "CinemaClips",
                    "publishedAt": "2020-01-01T00:00:00Z",
                    "thumbnails": {
                        "high": {
                            "url": "https://img.youtube.com/vi/abc12345/hqdefault.jpg"
                        }
                    },
                },
            },
            {
                "id": {"videoId": "def67890"},
                "snippet": {
                    "title": "Interstellar Movie Review & Reaction",
                    "channelTitle": "MovieReviewer",
                    "publishedAt": "2021-01-01T00:00:00Z",
                },
            },
        ]
    }

    respx.get(url).mock(return_value=httpx.Response(200, json=mock_response))

    source = await provider.search_source("Interstellar", "movie", ["Docking scene"])

    assert source is not None
    assert isinstance(source, YouTubeSource)
    assert source.video_id == "abc12345"
    assert source.title == "Interstellar Docking Scene 4K HD"
    assert source.channel_name == "CinemaClips"
    assert source.url == "https://www.youtube.com/watch?v=abc12345"
    assert source.thumbnail_url == "https://img.youtube.com/vi/abc12345/hqdefault.jpg"
    assert source.timestamp_verified is False
    assert source.start_timestamp is None
    assert source.relevance_score > 70.0


@pytest.mark.asyncio
@respx.mock
async def test_youtube_search_empty_results(provider: YouTubeProvider) -> None:
    url = f"{provider.BASE_URL}/search"
    respx.get(url).mock(return_value=httpx.Response(200, json={"items": []}))

    source = await provider.search_source("UnknownMovieTitle123", "movie")
    assert source is None


@pytest.mark.asyncio
@respx.mock
async def test_youtube_search_api_error(provider: YouTubeProvider) -> None:
    url = f"{provider.BASE_URL}/search"
    respx.get(url).mock(
        return_value=httpx.Response(500, json={"error": "Server Error"})
    )

    # Should degrade gracefully to None rather than raising an exception
    source = await provider.search_source("Interstellar", "movie")
    assert source is None
