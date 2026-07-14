"""
Shared pytest fixtures — mocks Gemini calls so tests run fast, free,
and deterministically without needing a real API key or network call.
"""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_gemini_calls():
    """
    Every test automatically gets Gemini calls mocked — prevents real
    API calls during CI runs and keeps tests fast and predictable.
    """
    with patch("shared.base_agent.BaseAgent._call_gemini", new_callable=AsyncMock) as mock:
        mock.return_value = "mocked gemini response"
        yield mock


@pytest.fixture
def reset_incident_store():
    from features.control_room.incident_store import incident_store
    incident_store.clear()
    yield
    incident_store.clear()