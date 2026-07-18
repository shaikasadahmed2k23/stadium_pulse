"""
Integration tests for the Fan Assistant HTTP route.
"""

from fastapi.testclient import TestClient


def test_chat_returns_fan_assistant_response(client: TestClient):
    payload = {
        "message": "Where is the nearest restroom?",
        "language": "en",
        "session_id": "session-123",
    }

    response = client.post("/api/fan-assistant/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session-123"
    assert isinstance(data["reply"], str)
    assert data["detected_intent"] is not None
    assert isinstance(data["routed_to_wayfinding"], bool)


def test_chat_validation_error_missing_message(client: TestClient):
    payload = {
        "language": "en",
        "session_id": "session-123",
    }
    response = client.post("/api/fan-assistant/chat", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]
