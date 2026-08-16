import logging
from typing import Any

import httpx

from src.core.exceptions import ProviderError
from src.core.retry import async_retry
from src.domain.interfaces import SourceProvider
from src.domain.models.youtube import YouTubeSource

logger = logging.getLogger(__name__)


class YouTubeProvider(SourceProvider):
    """
    Infrastructure provider for YouTube Data API (v3).
    Fetches high-quality source candidates for media recommendations.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(
        self,
        api_key: str | None,
        client: httpx.AsyncClient,
        circuit_breaker: Any = None,
        cache_provider: Any = None,
        cache_ttl_seconds: int = 3600,
        timeout: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._client = client
        self._circuit_breaker = circuit_breaker
        self._cache_provider = cache_provider
        self._cache_ttl_seconds = cache_ttl_seconds
        self._timeout = timeout

    async def search_source(
        self,
        media_title: str,
        media_type: str,
        query_keywords: list[str] | None = None,
    ) -> YouTubeSource | None:
        """
        Searches YouTube Data API for relevant video clip candidates and selects the top source.
        Returns None gracefully if disabled, unconfigured, or on error.
        """
        if not self._api_key:
            logger.warning(
                "YouTube API key is missing. Skipping YouTube source discovery."
            )
            return None

        cache_key = f"yt_source:{media_title.lower()}:{media_type.lower()}"
        if self._cache_provider:
            cached_data = await self._cache_provider.get(cache_key)
            if cached_data:
                logger.info("Serving YouTube source from cache.")
                return YouTubeSource.model_validate_json(cached_data)

        # Construct search query
        query_parts = [media_title, media_type, "scene"]
        if query_keywords and query_keywords[0]:
            # Use first keyword or hook if concise
            first_kw = query_keywords[0].strip()
            if len(first_kw) < 40:
                query_parts.append(first_kw)
        query = " ".join(query_parts)

        try:
            items = await self._fetch_search_results(query)
            if not items:
                logger.info(f"No YouTube candidates found for query '{query}'.")
                return None

            best_candidate = self._rank_candidates(items, media_title)
            if not best_candidate:
                return None

            if self._cache_provider:
                await self._cache_provider.set(
                    cache_key,
                    best_candidate.model_dump_json(),
                    ttl_seconds=self._cache_ttl_seconds,
                )

            return best_candidate

        except Exception as e:  # noqa: BLE001
            logger.warning(f"YouTube source discovery failed gracefully: {e}")
            return None

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def _fetch_search_results(self, query: str) -> list[dict[str, Any]]:
        url = f"{self.BASE_URL}/search"
        params: dict[str, str | int] = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": 5,
            "key": self._api_key or "",
        }

        async def _make_request() -> httpx.Response:
            return await self._client.get(url, params=params, timeout=self._timeout)

        if self._circuit_breaker:
            response = await self._circuit_breaker.call(_make_request)
        else:
            response = await _make_request()

        response.raise_for_status()
        data = response.json()
        items: list[dict[str, Any]] = data.get("items", [])
        return items

    def _rank_candidates(
        self, items: list[dict[str, Any]], media_title: str
    ) -> YouTubeSource | None:
        scored_candidates: list[tuple[float, YouTubeSource]] = []

        media_title_lower = media_title.lower()
        positive_signals = ["scene", "clip", "hd", "4k", "moment", "best"]
        negative_signals = [
            "reaction",
            "review",
            "analysis",
            "trailer",
            "full movie",
            "teaser",
            "spoiler",
        ]

        for item in items:
            id_info = item.get("id", {})
            video_id = id_info.get("videoId") if isinstance(id_info, dict) else None
            if not video_id:
                continue

            snippet = item.get("snippet", {})
            title = snippet.get("title", "")
            channel_name = snippet.get("channelTitle", "")
            published_at = snippet.get("publishedAt")
            thumbnails = snippet.get("thumbnails", {})
            high_thumb = (
                thumbnails.get("high", {}) if isinstance(thumbnails, dict) else {}
            )
            thumbnail_url = high_thumb.get("url")

            title_lower = title.lower()

            score = 70.0
            if media_title_lower in title_lower:
                score += 15.0

            for pos in positive_signals:
                if pos in title_lower:
                    score += 3.0

            for neg in negative_signals:
                if neg in title_lower:
                    score -= 25.0

            score = max(0.0, min(100.0, score))

            source = YouTubeSource(
                video_id=video_id,
                title=title,
                channel_name=channel_name,
                url=f"https://www.youtube.com/watch?v={video_id}",
                thumbnail_url=thumbnail_url,
                duration=None,
                published_at=published_at,
                view_count=None,
                relevance_score=round(score, 1),
                quality_score=round(score, 1),
                selection_reason=f"Matched top scene candidate from channel '{channel_name}'",
                timestamp_verified=False,
                start_timestamp=None,
                end_timestamp=None,
            )
            scored_candidates.append((score, source))

        if not scored_candidates:
            return None

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_score, top_source = scored_candidates[0]

        if top_score < 30.0:
            return None

        return top_source
