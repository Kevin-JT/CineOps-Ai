import uuid
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.domain.models.user import User as DomainUser
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import User as DBUser


class SQLAlchemyUserRepository(UserRepository):
    """
    SQLAlchemy implementation of the UserRepository.
    """

    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ) -> None:
        self._session_factory = session_factory

    def _to_domain(self, db_model: DBUser) -> DomainUser:
        return DomainUser(
            id=db_model.id,
            email=db_model.email,
            hashed_password=db_model.hashed_password,
            created_at=db_model.created_at,
        )

    def _to_model(self, domain_model: DomainUser) -> DBUser:
        return DBUser(
            id=domain_model.id,
            email=domain_model.email,
            hashed_password=domain_model.hashed_password,
            created_at=domain_model.created_at,
        )

    async def create(self, user: DomainUser) -> DomainUser:
        db_user = self._to_model(user)
        async with self._session_factory() as session:
            session.add(db_user)
            await session.commit()
            return self._to_domain(db_user)

    async def get_by_email(self, email: str) -> DomainUser | None:
        async with self._session_factory() as session:
            stmt = select(DBUser).where(DBUser.email == email)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            if db_user:
                return self._to_domain(db_user)
            return None

    async def get(self, id: uuid.UUID) -> DomainUser | None:
        async with self._session_factory() as session:
            db_user = await session.get(DBUser, id)
            if db_user:
                return self._to_domain(db_user)
            return None
