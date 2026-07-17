"""
Tests for the global exception handlers — verifies AppError and unhandled
exceptions get shaped into the correct JSON response, using a minimal
throwaway FastAPI app so this doesn't depend on the full route graph.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.error_handlers import register_error_handlers
from core.errors import AppError


@pytest.fixture
def app():
    test_app = FastAPI()
    register_error_handlers(test_app)

    @test_app.get("/boom-app-error")
    async def boom_app_error():
        raise AppError.not_found("Widget")

    @test_app.get("/boom-unhandled")
    async def boom_unhandled():
        raise ValueError("something exploded")

    return test_app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


def test_app_error_returns_typed_status_and_code(client):
    response = client.get("/boom-app-error")
    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "not_found"
    assert "Widget" in body["message"]


def test_unhandled_exception_returns_generic_500(client):
    response = client.get("/boom-unhandled")
    assert response.status_code == 500
    body = response.json()
    # Must NOT leak the exception type or message to the client.
    assert body["error"] == "internal_error"
    assert "something exploded" not in body["message"]
