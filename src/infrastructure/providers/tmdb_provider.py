import logging
from typing import Any

import httpx

from src.core.exceptions import ProviderError
from src.core.retry import async_retry
from src.domain.interfaces import MediaProvider
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class TMDbProvider(MediaProvider):
    """
    Provider for The Movie Database (TMDb) API.
    Fetches trending movies.
    """

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_key: str,
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

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def fetch_trending(self) -> list[MediaItem]:
        """
        Fetches the current trending movies from TMDb.
        """
        if not self._api_key:
            logger.warning("TMDb API key is missing. Cannot fetch trending movies.")
            raise ProviderError("TMDb API key not configured")

        cache_key = "tmdb_trending"
        if self._cache_provider:
            cached_data = await self._cache_provider.get(cache_key)
            if cached_data:
                logger.info("Serving TMDb trending movies from cache.")
                import json

                items_data = json.loads(cached_data)
                return [MediaItem(**item) for item in items_data]

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "accept": "application/json",
        }

        async def _make_request() -> httpx.Response:
            return await self._client.get(
                f"{self.BASE_URL}/trending/movie/day",
                headers=headers,
                timeout=self._timeout,
            )

        if self._circuit_breaker:
            response = await self._circuit_breaker.call(_make_request)
        else:
            response = await _make_request()

        response.raise_for_status()
        data = response.json()

        results: list[dict[str, Any]] = data.get("results", [])

        items = []
        for item in results:
            # Map TMDb fields to MediaItem
            media = MediaItem(
                id=str(item.get("id")),
                title=item.get("title") or item.get("name", "Unknown Title"),
                overview=item.get("overview", ""),
                media_type="movie",
                release_date=item.get("release_date") or item.get("first_air_date"),
                rating=float(item.get("vote_average", 0.0)),
                popularity=float(item.get("popularity", 0.0)),
            )
            items.append(media)

        logger.info(f"Successfully fetched {len(items)} trending movies from TMDb.")

        if self._cache_provider:
            import json

            serialized = json.dumps([item.model_dump() for item in items])
            await self._cache_provider.set(
                cache_key, serialized, ttl_seconds=self._cache_ttl_seconds
            )

        return items
