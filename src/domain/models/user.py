import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class User:
    """
    Domain entity representing an authenticated user.
    """

    email: str
    hashed_password: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
