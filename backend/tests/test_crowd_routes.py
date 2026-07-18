"""
Integration tests for the Crowd Intelligence HTTP route.
"""

from fastapi.testclient import TestClient


def test_get_crowd_status_returns_zone_data(client: TestClient):
    response = client.get("/api/crowd/status")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data["zones"], list)
    assert data["highest_risk_zone"] is None or isinstance(data["highest_risk_zone"], str)
    assert data["overall_status"] in {"normal", "elevated", "critical"}
    assert all("zone_id" in zone for zone in data["zones"])


def test_get_crowd_status_filters_by_zone_id(client: TestClient):
    response = client.get("/api/crowd/status", params={"zone_ids": ["gate_1"]})

    assert response.status_code == 200
    data = response.json()
    assert len(data["zones"]) == 1
    assert data["zones"][0]["zone_id"] == "gate_1"


def test_get_crowd_status_handles_unknown_zone_id(client: TestClient):
    response = client.get("/api/crowd/status", params={"zone_ids": ["unknown_zone"]})

    assert response.status_code == 200
    data = response.json()
    assert data["zones"] == []
    assert data["highest_risk_zone"] is None
    assert data["overall_status"] == "normal"
