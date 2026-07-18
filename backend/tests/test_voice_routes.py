"""
Integration tests for the Voice Assistant HTTP route.
"""

from fastapi.testclient import TestClient


def test_create_voice_session_returns_room_and_token(client: TestClient):
    payload = {"fan_id": "fan-123", "language": "en"}
    response = client.post("/api/voice/session", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["room_name"].startswith("fan-fan-123-")
    assert isinstance(data["livekit_token"], str)
    assert data["livekit_url"] == "http://localhost"


def test_create_voice_session_validation_error_missing_fan_id(client: TestClient):
    payload = {"language": "en"}
    response = client.post("/api/voice/session", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]
