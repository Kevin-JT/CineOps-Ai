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

    def __init__(self, api_key: str, timeout: float = 10.0) -> None:
        self._api_key = api_key
        self._timeout = timeout

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def fetch_trending(self) -> list[MediaItem]:
        """
        Fetches the current trending movies from TMDb.

        Returns:
            A list of MediaItem objects representing trending movies.

        Raises:
            ProviderError: If the API request fails.
        """
        if not self._api_key:
            logger.warning("TMDb API key is missing. Cannot fetch trending movies.")
            raise ProviderError("TMDb API key not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self.BASE_URL}/trending/movie/day", headers=headers
            )
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
            return items
