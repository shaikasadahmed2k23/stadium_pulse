"""
Integration tests for the Wayfinding HTTP route.
"""

from fastapi.testclient import TestClient


def test_navigate_returns_route_structure(client: TestClient):
    payload = {
        "query": "Take me to section 101",
        "current_zone": "gate_1",
        "language": "en",
    }

    response = client.post("/api/wayfinding/navigate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["route"], list)
    assert isinstance(data["total_estimated_time_seconds"], int)
    assert isinstance(data["route_avoids_congestion"], bool)
    assert all("instruction" in step for step in data["route"])


def test_navigate_validation_error_missing_fields(client: TestClient):
    payload = {"query": "Take me to section 101"}
    response = client.post("/api/wayfinding/navigate", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"]


def test_navigate_rate_limit_dependency(client: TestClient):
    payload = {
        "query": "Take me to section 101",
        "current_zone": "gate_1",
    }

    for _ in range(30):
        response = client.post("/api/wayfinding/navigate", json=payload)
        assert response.status_code == 200

    response = client.post("/api/wayfinding/navigate", json=payload)
    assert response.status_code == 429
