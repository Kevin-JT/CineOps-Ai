from src.domain.models.media_item import MediaItem


class MediaFilterService:
    """
    Service responsible for filtering media items based on business rules.
    """

    def __init__(
        self, min_rating: float = 0.0, required_genres: list[str] | None = None
    ) -> None:
        self.min_rating = min_rating
        self.required_genres = required_genres or []

    def filter_items(self, items: list[MediaItem]) -> list[MediaItem]:
        """
        Filters a list of media items based on configured criteria.

        Args:
            items: The list of items to filter.

        Returns:
            A filtered list of items meeting the business criteria.
        """
        filtered = []
        for item in items:
            if not self._is_valid(item):
                continue
            if item.rating < self.min_rating:
                continue
            if self.required_genres and not any(
                g in item.genres for g in self.required_genres
            ):
                continue
            filtered.append(item)
        return filtered

    def _is_valid(self, item: MediaItem) -> bool:
        """
        Validates whether a media item has the minimum required data.
        """
        if not item.id or not item.title:
            return False
        # Treat items with "Unknown Title" as invalid per our provider fallbacks
        return item.title != "Unknown Title"
