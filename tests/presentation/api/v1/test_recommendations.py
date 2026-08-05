import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.domain.models.recommendation import RecommendationLog
from src.presentation.api.app import create_app
from src.presentation.api.dependencies import get_recommendation_service


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def api_headers() -> dict[str, str]:
    return {"X-API-Key": "change-me-in-production"}


def test_get_all_recommendation_logs(
    client: TestClient, mock_service: AsyncMock, api_headers: dict[str, str]
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service

    dt = datetime.now(UTC)
    uid = uuid.uuid4()
    mock_log = RecommendationLog(
        id=uid,
        prompt="p",
        response="{}",
        model="gemini",
        response_time=0.5,
        status="success",
        created_at=dt,
    )
    mock_service.get_all_recommendation_logs.return_value = [mock_log]

    try:
        response = client.get("/api/v1/recommendations", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(uid)
        assert data[0]["prompt"] == "p"
    finally:
        app.dependency_overrides.clear()


def test_get_recommendation_log(
    client: TestClient, mock_service: AsyncMock, api_headers: dict[str, str]
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service

    dt = datetime.now(UTC)
    uid = uuid.uuid4()
    mock_log = RecommendationLog(
        id=uid,
        prompt="p",
        response="{}",
        model="gemini",
        response_time=0.5,
        status="success",
        created_at=dt,
    )
    mock_service.get_recommendation_log.return_value = mock_log

    try:
        response = client.get(f"/api/v1/recommendations/{uid}", headers=api_headers)
        assert response.status_code == 200
        assert response.json()["id"] == str(uid)
    finally:
        app.dependency_overrides.clear()


def test_get_recommendation_log_not_found(
    client: TestClient, mock_service: AsyncMock, api_headers: dict[str, str]
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service

    mock_service.get_recommendation_log.return_value = None

    try:
        response = client.get(
            f"/api/v1/recommendations/{uuid.uuid4()}", headers=api_headers
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_delete_recommendation_log(
    client: TestClient, mock_service: AsyncMock, api_headers: dict[str, str]
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service

    mock_service.delete_recommendation_log.return_value = True

    try:
        response = client.delete(
            f"/api/v1/recommendations/{uuid.uuid4()}", headers=api_headers
        )
        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_delete_recommendation_log_not_found(
    client: TestClient, mock_service: AsyncMock, api_headers: dict[str, str]
) -> None:
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_recommendation_service] = lambda: mock_service

    mock_service.delete_recommendation_log.return_value = False

    try:
        response = client.delete(
            f"/api/v1/recommendations/{uuid.uuid4()}", headers=api_headers
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
