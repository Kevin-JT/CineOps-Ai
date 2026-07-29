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
        Checks all items concurrently for performance optimization.
        """
        import asyncio

        async def _is_duplicate(item: MediaItem) -> bool:
            # We can run these two checks concurrently as well, but sequential is fine per item
            # Running both concurrently per item for maximum performance
            is_blacklisted_task = asyncio.create_task(
                self.blacklist_repo.is_blacklisted(item.id)
            )
            exists_task = asyncio.create_task(self.history_repo.exists(item.id))

            # If blacklisted, it's a duplicate
            if await is_blacklisted_task:
                return True

            # If exists in history, it's a duplicate
            return bool(await exists_task)

        # Run checks for all items concurrently
        results = await asyncio.gather(*[_is_duplicate(item) for item in items])

        unique_items = [item for item, is_dup in zip(items, results) if not is_dup]
        return unique_items
