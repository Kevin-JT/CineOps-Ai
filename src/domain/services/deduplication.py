from src.domain.interfaces import BlacklistRepository, HistoryRepository
from src.domain.models.media_item import MediaItem


class DeduplicationService:
    """
    Service responsible for removing duplicate or unwanted items
    by checking history and blacklist repositories.
    """

    def __init__(
        self,
        history_repo: HistoryRepository,
        blacklist_repo: BlacklistRepository,
    ) -> None:
        self.history_repo = history_repo
        self.blacklist_repo = blacklist_repo

    async def filter_duplicates(self, items: list[MediaItem]) -> list[MediaItem]:
        """
        Filters out items that have already been recommended or are blacklisted.

        Args:
            items: The list of media items to check.

        Returns:
            A list of new, valid items.
        """
        unique_items = []
        for item in items:
            is_blacklisted = await self.blacklist_repo.is_blacklisted(item.id)
            if is_blacklisted:
                continue

            exists_in_history = await self.history_repo.exists(item.id)
            if exists_in_history:
                continue

            unique_items.append(item)

        return unique_items
