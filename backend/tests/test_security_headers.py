"""
Tests for SecurityHeadersMiddleware — checklist item requires security
headers to be explicit and verified, not just present in code someone
skims past.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.security_headers import SecurityHeadersMiddleware


@pytest.fixture
def client():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    return TestClient(app)


def test_sets_x_content_type_options(client):
    response = client.get("/ping")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_sets_x_frame_options_deny(client):
    response = client.get("/ping")
    assert response.headers["X-Frame-Options"] == "DENY"


def test_sets_referrer_policy(client):
    response = client.get("/ping")
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_sets_content_security_policy(client):
    response = client.get("/ping")
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


def test_sets_permissions_policy(client):
    response = client.get("/ping")
    assert "geolocation=()" in response.headers["Permissions-Policy"]
