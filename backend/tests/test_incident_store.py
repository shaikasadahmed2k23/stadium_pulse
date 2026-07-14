"""
Tests for the in-memory incident store service.
"""
import uuid
from datetime import datetime

from features.control_room.incident_store import IncidentStore
from features.control_room.schemas import IncidentAlert, IncidentType


def make_incident(incident_id: str | None = None) -> IncidentAlert:
    return IncidentAlert(
        incident_id=incident_id or str(uuid.uuid4()),
        incident_type=IncidentType.CROWD_SURGE,
        zone="gate_1",
        description="Test incident",
        auto_detected=True,
        suggested_action="Test action",
        severity="high",
        timestamp=datetime.utcnow(),
    )


def test_add_and_retrieve_incident():
    store = IncidentStore()
    incident = make_incident()
    store.add(incident)
    active = store.get_active()
    assert len(active) == 1
    assert active[0].incident_id == incident.incident_id


def test_resolve_removes_incident():
    store = IncidentStore()
    incident = make_incident()
    store.add(incident)
    resolved = store.resolve(incident.incident_id)
    assert resolved is True
    assert len(store.get_active()) == 0


def test_resolve_nonexistent_incident_returns_false():
    store = IncidentStore()
    result = store.resolve("nonexistent-id")
    assert result is False


def test_clear_removes_all_incidents():
    store = IncidentStore()
    store.add(make_incident())
    store.add(make_incident())
    store.clear()
    assert len(store.get_active()) == 0
