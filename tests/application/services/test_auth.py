from unittest.mock import AsyncMock

import pytest

from src.application.services.auth import AuthService
from src.core.exceptions import CineOpsError
from src.domain.models.user import User


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def auth_service(mock_repo: AsyncMock) -> AuthService:
    return AuthService(repository=mock_repo)

def test_password_hashing(auth_service: AuthService) -> None:
    pwd = "my_super_secret_password"
    hashed = auth_service.get_password_hash(pwd)
    assert hashed != pwd
    assert auth_service.verify_password(pwd, hashed) is True
    assert auth_service.verify_password("wrong", hashed) is False

@pytest.mark.asyncio
async def test_register_success(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = User(email="test@test.com", hashed_password="hashed")

    user = await auth_service.register("test@test.com", "password")
    assert user.email == "test@test.com"
    mock_repo.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_register_conflict(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = User(email="test@test.com", hashed_password="hashed")
    with pytest.raises(CineOpsError, match="already exists"):
        await auth_service.register("test@test.com", "password")

@pytest.mark.asyncio
async def test_authenticate_success(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    pwd = "password123"
    hashed = auth_service.get_password_hash(pwd)
    mock_repo.get_by_email.return_value = User(email="test@test.com", hashed_password=hashed)

    user = await auth_service.authenticate("test@test.com", pwd)
    assert user is not None
    assert user.email == "test@test.com"

@pytest.mark.asyncio
async def test_authenticate_fail(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = None
    assert await auth_service.authenticate("test@test.com", "pass") is None

    hashed = auth_service.get_password_hash("password123")
    mock_repo.get_by_email.return_value = User(email="test@test.com", hashed_password=hashed)
    assert await auth_service.authenticate("test@test.com", "wrong") is None

def test_tokens(auth_service: AuthService) -> None:
    access = auth_service.create_access_token("test@test.com")
    refresh = auth_service.create_refresh_token("test@test.com")
    
    a_payload = auth_service.decode_token(access)
    assert a_payload["sub"] == "test@test.com"
    assert a_payload["type"] == "access"

    r_payload = auth_service.decode_token(refresh)
    assert r_payload["sub"] == "test@test.com"
    assert r_payload["type"] == "refresh"

def test_decode_invalid_token(auth_service: AuthService) -> None:
    with pytest.raises(CineOpsError):
        auth_service.decode_token("invalid.token.here")

@pytest.mark.asyncio
async def test_get_user_from_token(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    access = auth_service.create_access_token("test@test.com")
    mock_repo.get_by_email.return_value = User(email="test@test.com", hashed_password="pwd")
    user = await auth_service.get_user_from_token(access)
    assert user is not None
    assert user.email == "test@test.com"

@pytest.mark.asyncio
async def test_get_user_from_token_invalid_type(auth_service: AuthService) -> None:
    refresh = auth_service.create_refresh_token("test@test.com")
    with pytest.raises(CineOpsError, match="Invalid token type"):
        await auth_service.get_user_from_token(refresh)

@pytest.mark.asyncio
async def test_refresh_access_token(auth_service: AuthService, mock_repo: AsyncMock) -> None:
    refresh = auth_service.create_refresh_token("test@test.com")
    mock_repo.get_by_email.return_value = User(email="test@test.com", hashed_password="pwd")
    new_access = await auth_service.refresh_access_token(refresh)
    assert new_access is not None
    assert auth_service.decode_token(new_access)["type"] == "access"

@pytest.mark.asyncio
async def test_refresh_access_token_invalid(auth_service: AuthService) -> None:
    access = auth_service.create_access_token("test@test.com")
    with pytest.raises(CineOpsError, match="Invalid token type"):
        await auth_service.refresh_access_token(access)
