"""
Shared pytest fixtures — mocks Gemini calls so tests run fast, free,
and deterministically without needing a real API key or network call.
"""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Ensure required environment variables exist before any tests are imported.
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")
os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_KEY", "test-supabase-key")
os.environ.setdefault("API_SECRET_KEY", "test-api-key")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "60")
os.environ.setdefault("LIVEKIT_URL", "http://localhost")
os.environ.setdefault("LIVEKIT_API_KEY", "test-livekit-key")
os.environ.setdefault("LIVEKIT_API_SECRET", "test-livekit-secret")
os.environ.setdefault("CACHE_TTL_SECONDS", "300")


@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """Ensure tests use deterministic environment settings."""
    os.environ.update(
        {
            "GEMINI_API_KEY": "test-gemini-key",
            "GEMINI_MODEL": "gemini-2.5-flash",
            "SUPABASE_URL": "http://localhost",
            "SUPABASE_KEY": "test-supabase-key",
            "API_SECRET_KEY": "test-api-key",
            "ALLOWED_ORIGINS": "http://localhost:3000",
            "RATE_LIMIT_PER_MINUTE": "60",
            "LIVEKIT_URL": "http://localhost",
            "LIVEKIT_API_KEY": "test-livekit-key",
            "LIVEKIT_API_SECRET": "test-livekit-secret",
            "CACHE_TTL_SECONDS": "300",
        }
    )
    yield


@pytest.fixture(autouse=True)
def mock_gemini_calls():
    """
    Every test automatically gets Gemini calls mocked — prevents real
    API calls during CI runs and keeps tests fast and predictable.
    """
    with patch("shared.base_agent.BaseAgent._call_gemini", new_callable=AsyncMock) as mock:
        mock.return_value = "mocked gemini response"
        yield mock


@pytest.fixture(scope="session")
def client():
    """FastAPI test client with voice worker subprocess mocked."""
    with patch("main.subprocess.Popen", autospec=True) as mock_popen:
        mock_process = MagicMock()
        mock_process.pid = 1234
        mock_process.poll.return_value = None
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = None
        mock_popen.return_value = mock_process

        from main import app

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture(autouse=True)
def reset_state_between_tests():
    from core.rate_limiter import _limiter
    from features.control_room.incident_store import incident_store

    incident_store.clear()
    _limiter.reset()
    yield
    incident_store.clear()
    _limiter.reset()


@pytest.fixture
def reset_incident_store():
    from features.control_room.incident_store import incident_store

    incident_store.clear()
    yield
    incident_store.clear()