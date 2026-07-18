"""
Integration tests for the Control Room HTTP routes.
"""

from fastapi.testclient import TestClient


def test_control_room_state_requires_api_key(client: TestClient):
    response = client.get("/api/control-room/state")
    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


def test_control_room_state_with_valid_api_key(client: TestClient):
    response = client.get("/api/control-room/state", headers={"x-api-key": "test-api-key"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["zones"], list)
    assert isinstance(data["active_recommendations"], list)
    assert isinstance(data["active_incidents"], list)


def test_report_incident_requires_api_key(client: TestClient):
    payload = {
        "zone_id": "gate_1",
        "incident_type": "medical",
        "description": "Test incident",
        "severity": "high",
    }
    response = client.post("/api/control-room/incidents/report", json=payload)
    assert response.status_code == 401


def test_report_incident_with_valid_api_key(client: TestClient):
    payload = {
        "zone_id": "gate_1",
        "incident_type": "medical",
        "description": "Test incident",
        "severity": "high",
    }
    response = client.post(
        "/api/control-room/incidents/report",
        json=payload,
        headers={"x-api-key": "test-api-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["zone"] == "gate_1"
    assert data["incident_type"] == "medical"
    assert data["auto_detected"] is False


def test_scan_anomalies_with_valid_api_key(client: TestClient):
    response = client.post("/api/control-room/scan-anomalies", headers={"x-api-key": "test-api-key"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
