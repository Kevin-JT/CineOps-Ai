from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from src.config.settings import get_settings
from src.core.exceptions import CineOpsError
from src.domain.models.user import User
from src.domain.repositories.user_repository import UserRepository


class AuthService:
    """
    Application service handling user authentication and registration.
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository
        self._settings = get_settings()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=self._settings.access_token_expire_minutes
        )
        to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
        return jwt.encode(
            to_encode,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(
            minutes=self._settings.refresh_token_expire_minutes
        )
        to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
        return jwt.encode(
            to_encode,
            self._settings.jwt_secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    async def register(self, email: str, password: str) -> User:
        """
        Registers a new user.
        Raises CineOpsError if email already exists.
        """
        existing = await self._repository.get_by_email(email)
        if existing:
            raise CineOpsError(f"User with email {email} already exists.")

        hashed = self.get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed)
        return await self._repository.create(new_user)

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Authenticates a user by email and password.
        Returns the User if valid, None otherwise.
        """
        user = await self._repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decodes a JWT token. Raises JWTError if invalid or expired.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
            return payload
        except jwt.PyJWTError as e:
            raise CineOpsError("Could not validate credentials") from e

    async def get_user_from_token(self, token: str) -> User | None:
        """
        Retrieves a user from an access token.
        """
        payload = self.decode_token(token)
        if payload.get("type") != "access":
            raise CineOpsError("Invalid token type")
        
        email = payload.get("sub")
        if not email:
            return None
            
        return await self._repository.get_by_email(email)

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Issues a new access token using a valid refresh token.
        """
        payload = self.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise CineOpsError("Invalid token type")
            
        email = payload.get("sub")
        if not email:
            raise CineOpsError("Invalid token subject")
            
        user = await self._repository.get_by_email(email)
        if not user:
            raise CineOpsError("User not found")
            
        return self.create_access_token(user.email)
