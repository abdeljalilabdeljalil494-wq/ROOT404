"""Smoke tests for the FastAPI application entrypoint and health endpoint."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] in {"development", "production"}


def test_openapi_schema_is_served() -> None:
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"].startswith("ROOT 404")


def test_unknown_api_route_returns_404() -> None:
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
