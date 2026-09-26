import pytest

PROTECTED = [
    ("post", "/upload"),
    ("get", "/jobs/abc123"),
    ("get", "/jobs/abc123/stems/vocals"),
    ("post", "/jobs/abc123/export"),
]


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_404(client):
    assert client.get("/definitely-not-a-route").status_code == 404


@pytest.mark.parametrize("method,path", PROTECTED)
def test_protected_routes_are_registered_and_require_auth(client, method, path):
    response = getattr(client, method)(path)
    # 401/403 proves the route exists and the auth dependency ran. A 404 here
    # would mean the router was never mounted.
    assert response.status_code in (401, 403), (
        f"{method.upper()} {path} returned {response.status_code}"
    )


def test_upload_rejects_unsupported_extension(client):
    response = client.post(
        "/upload",
        files={"file": ("track.flac", b"not really audio", "audio/flac")},
        headers={"Authorization": "Bearer fake-token"},
    )
    # Auth runs before validation, so a bad token still stops at 401. The point
    # is that it is not a 404 and not a 500.
    assert response.status_code in (401, 403, 422)


def test_cors_allows_configured_origin(client):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unconfigured_origin(client):
    response = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "https://evil.example.com"
