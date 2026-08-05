from collections.abc import Generator
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.exceptions import CineOpsError
from src.domain.models.user import User
from src.presentation.api.app import create_app
from src.presentation.api.dependencies import get_auth_service


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    return AsyncMock()


from unittest.mock import AsyncMock, MagicMock


def test_register_success(client: TestClient, mock_auth_service: AsyncMock) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.register.return_value = User(
        email="test@test.com", hashed_password="pwd"
    )
    mock_auth_service.create_access_token = MagicMock(return_value="access")
    mock_auth_service.create_refresh_token = MagicMock(return_value="refresh")

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["access_token"] == "access"
        assert data["refresh_token"] == "refresh"
    finally:
        app.dependency_overrides.clear()


def test_register_conflict(client: TestClient, mock_auth_service: AsyncMock) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.register.side_effect = CineOpsError("conflict")

    try:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 409
    finally:
        app.dependency_overrides.clear()


def test_login_success(client: TestClient, mock_auth_service: AsyncMock) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.authenticate.return_value = User(
        email="test@test.com", hashed_password="pwd"
    )
    mock_auth_service.create_access_token = MagicMock(return_value="access")
    mock_auth_service.create_refresh_token = MagicMock(return_value="refresh")

    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access"
        assert data["refresh_token"] == "refresh"
    finally:
        app.dependency_overrides.clear()


def test_login_unauthorized(client: TestClient, mock_auth_service: AsyncMock) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.authenticate.return_value = None

    try:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": "password123"},
        )
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_refresh_token_success(
    client: TestClient, mock_auth_service: AsyncMock
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.refresh_access_token.return_value = "new_access"

    try:
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "old_refresh"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access"
        assert data["refresh_token"] == "old_refresh"
    finally:
        app.dependency_overrides.clear()


def test_refresh_token_unauthorized(
    client: TestClient, mock_auth_service: AsyncMock
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    mock_auth_service.refresh_access_token.side_effect = CineOpsError("invalid")

    try:
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "old_refresh"}
        )
        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
