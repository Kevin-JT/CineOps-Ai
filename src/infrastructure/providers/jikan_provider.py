import logging
from typing import Any

import httpx

from src.core.exceptions import ProviderError
from src.core.retry import async_retry
from src.domain.interfaces import MediaProvider
from src.domain.models.media_item import MediaItem

logger = logging.getLogger(__name__)


class JikanProvider(MediaProvider):
    """
    Provider for the Jikan (MyAnimeList) API.
    Fetches top trending anime.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def fetch_trending(self) -> list[MediaItem]:
        """
        Fetches the current top anime from Jikan.

        Returns:
            A list of MediaItem objects representing top anime.

        Raises:
            ProviderError: If the API request fails.
        """
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(f"{self._base_url}/top/anime")
            response.raise_for_status()
            data = response.json()

            results: list[dict[str, Any]] = data.get("data", [])

            items = []
            for item in results:
                # Extract year/date if available
                aired = item.get("aired", {})
                release_date = None
                if isinstance(aired, dict) and "from" in aired:
                    date_str = aired.get("from")
                    if date_str:
                        # Jikan returns ISO 8601 strings, we can just grab the date part
                        release_date = str(date_str).split("T")[0]

                media = MediaItem(
                    id=str(item.get("mal_id")),
                    title=item.get("title_english")
                    or item.get("title", "Unknown Title"),
                    overview=item.get("synopsis") or "",
                    media_type="anime",
                    release_date=release_date,
                    rating=float(item.get("score") or 0.0),
                    popularity=float(item.get("members") or 0.0),
                )
                items.append(media)

            logger.info(f"Successfully fetched {len(items)} top anime from Jikan.")
            return items
