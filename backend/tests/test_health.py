"""Health endpoint, security headers, and error-handling smoke tests."""
from __future__ import annotations

import pytest


def test_health_all_components(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["components"]["database"] == "ok"
    assert body["components"]["redis"] in {"ok", "unavailable"}  # optional in dev
    assert body["status"] in {"ok", "degraded"}
    assert body["environment"] == "development"


def test_health_degraded_when_redis_down(client, monkeypatch, request):
    monkeypatch.setenv("REDIS_URL", "redis://invalid-host:99/0")
    from app.core.config import get_settings

    get_settings.cache_clear()
    request.addfinalizer(get_settings.cache_clear)

    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["components"]["database"] == "ok"
    assert body["components"]["redis"] == "unavailable"


def test_security_headers_present(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "no-store" in response.headers["Cache-Control"]


def test_openapi_schema_is_served(client):
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"].startswith("ROOT 404")


def test_unknown_api_route_returns_404(client):
    assert client.get("/api/does-not-exist").status_code == 404


def test_unhandled_errors_do_not_leak_stack_traces(client, monkeypatch):
    def boom():
        raise RuntimeError("secret-internal-detail")

    monkeypatch.setattr(
        "app.api.routes.health._check_database", lambda db: boom()
    )
    #: raise_server_exceptions=False -> behave like a real HTTP client and
    #: return the server's 500 response instead of re-raising in the test.
    from fastapi.testclient import TestClient as _TC

    from app.main import app as _app

    raw_client = _TC(_app, raise_server_exceptions=False)
    response = raw_client.get("/api/health")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}
    assert "secret-internal-detail" not in response.text
