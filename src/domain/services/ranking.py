from src.domain.models.media_item import MediaItem


class RankingService:
    """
    Service responsible for sorting and ranking media items.
    """

    @staticmethod
    def rank_by_rating(
        items: list[MediaItem], descending: bool = True
    ) -> list[MediaItem]:
        """
        Sorts items by their rating.
        """
        return sorted(items, key=lambda x: x.rating, reverse=descending)

    @staticmethod
    def rank_by_popularity(
        items: list[MediaItem], descending: bool = True
    ) -> list[MediaItem]:
        """
        Sorts items by their popularity.
        """
        return sorted(items, key=lambda x: x.popularity, reverse=descending)
