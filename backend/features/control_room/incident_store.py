"""
In-memory incident store. Holds active incidents raised either manually
(staff-reported) or automatically (Anomaly Detector — Feature 8).
Swap for a Supabase table if time allows post-MVP.
"""
import threading

from features.control_room.schemas import IncidentAlert


class IncidentStore:
    def __init__(self):
        self._incidents: dict[str, IncidentAlert] = {}
        self._lock = threading.Lock()

    def add(self, incident: IncidentAlert) -> None:
        with self._lock:
            self._incidents[incident.incident_id] = incident

    def has_active_incident(self, zone_id: str, incident_type) -> bool:
        """Checks if an incident of this type is already active for this zone —
        prevents duplicate incidents being raised every polling cycle for the
        same ongoing situation."""
        with self._lock:
            return any(
                inc.zone == zone_id and inc.incident_type == incident_type
                for inc in self._incidents.values()
            )

    def get_active(self) -> list[IncidentAlert]:
        with self._lock:
            return list(self._incidents.values())

    def resolve(self, incident_id: str) -> bool:
        with self._lock:
            return self._incidents.pop(incident_id, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._incidents.clear()


incident_store = IncidentStore()
