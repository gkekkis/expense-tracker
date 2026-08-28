from __future__ import annotations

from app.api.core.cors import get_cors_allow_origins


def test_cors_origin_parser_trims_and_ignores_empty_values(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", " http://localhost:3000/ , , http://127.0.0.1:3000 ")

    assert get_cors_allow_origins() == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_cors_preflight_allows_configured_origin(client):
    resp = client.options(
        "/api/v1/health/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )

    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert resp.headers["access-control-allow-credentials"] == "true"
    assert "authorization" in resp.headers["access-control-allow-headers"].lower()


def test_cors_preflight_rejects_unconfigured_origin(client):
    resp = client.options(
        "/api/v1/health/", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"}
    )

    assert resp.status_code == 400
    assert "access-control-allow-origin" not in resp.headers


def test_cors_simple_request_sets_header_for_configured_origin(client):
    resp = client.get("/api/v1/health/", headers={"Origin": "http://127.0.0.1:3000"})

    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
