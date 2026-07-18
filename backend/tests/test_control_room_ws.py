"""
Integration tests for the Control Room WebSocket feed.
"""

from fastapi.testclient import TestClient


def test_control_room_websocket_pushes_state(client: TestClient):
    with client.websocket_connect("/ws/control-room") as websocket:
        message = websocket.receive_json()
        assert "zones" in message
        assert isinstance(message["zones"], list)
        assert "active_recommendations" in message
        assert "active_incidents" in message
        websocket.close()