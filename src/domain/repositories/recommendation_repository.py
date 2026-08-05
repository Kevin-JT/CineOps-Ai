import uuid
from abc import ABC, abstractmethod
from collections.abc import Sequence


class RecommendationRepository[T](ABC):
    """
    Abstract repository interface for Recommendation storage.
    Uses Generic[T] to maintain Clean Architecture and avoid coupling
    the domain layer to infrastructure-specific ORM models.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new recommendation record."""

    @abstractmethod
    async def get(self, id: uuid.UUID) -> T | None:
        """Retrieve a recommendation by its UUID."""

    @abstractmethod
    async def get_all(self) -> Sequence[T]:
        """Retrieve all recommendations."""

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> bool:
        """Delete a recommendation by its UUID. Returns True if deleted."""
