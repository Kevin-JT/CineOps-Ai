from collections.abc import Generator
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.presentation.api.app import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_version(client: TestClient) -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}


def test_metrics(client: TestClient) -> None:
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert response.json() == {"status": "not_implemented"}


# We can test the Readiness check via the TestClient as well, which tests the dependency injection.
# Since we didn't mock the container here, it will use the real config settings.
def test_readiness_check(client: TestClient) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "tmdb_configured" in data


from unittest.mock import AsyncMock

from src.presentation.api.dependencies import get_coordinator


def test_workflow_run(client: TestClient) -> None:
    mock_coordinator = AsyncMock()
    app = cast("FastAPI", client.app)
    app.dependency_overrides[get_coordinator] = lambda: mock_coordinator
    try:
        response = client.post(
            "/api/v1/workflow/run", headers={"X-API-Key": "change-me-in-production"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"
    finally:
        app.dependency_overrides.clear()


def test_recommendation_generate_invalid_input(client: TestClient) -> None:
    # Test missing fields
    response = client.post(
        "/api/v1/recommendations/generate",
        json={"items": []},
        headers={"X-API-Key": "change-me-in-production"},
    )
    assert (
        response.status_code == 422
    )  # Unprocessable Entity (Pydantic validation error)


def test_correlation_id_middleware(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert "x-correlation-id" in response.headers


def test_timing_middleware(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert "x-process-time" in response.headers
