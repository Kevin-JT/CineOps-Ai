import uuid
from abc import ABC, abstractmethod

from src.domain.models.user import User


class UserRepository(ABC):
    """
    Abstract base class for User data access.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Creates a new user in the repository.
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email.
        """

    @abstractmethod
    async def get(self, id: uuid.UUID) -> User | None:
        """
        Retrieves a user by their ID.
        """
