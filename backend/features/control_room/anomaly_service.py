"""
Anomaly Detector Agent (Feature 8).
Continuously watches crowd data for abnormal patterns (sudden surges,
sustained critical occupancy) and auto-raises incidents — demonstrating
the system catching problems before staff notice them, directly
answering the brief's "zero room for execution errors" requirement.
"""
import uuid
from datetime import datetime

from features.control_room.incident_store import incident_store
from features.control_room.schemas import IncidentAlert, IncidentType
from features.crowd.service import CrowdIntelligenceAgent
from shared.base_agent import BaseAgent
from shared.schemas import ZoneStatus


class AnomalyDetector(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="AnomalyDetector")
        self.crowd_agent = CrowdIntelligenceAgent()
        self._previous_occupancy: dict[str, float] = {}
        self._action_cache: dict[str, str] = {}  # zone_id -> cached suggested action

    async def process(self, _: None = None) -> list[IncidentAlert]:
        crowd_data = await self.crowd_agent.process()
        new_incidents: list[IncidentAlert] = []

        for zone in crowd_data.zones:
            surge_detected = self._is_sudden_surge(zone.zone_id, zone.occupancy_percentage)
            sustained_critical = zone.status == ZoneStatus.CRITICAL

            if (surge_detected or sustained_critical) and not incident_store.has_active_incident(
                zone.zone_id, IncidentType.CROWD_SURGE
            ):
                incident = await self._create_incident(zone, surge_detected)
                incident_store.add(incident)
                new_incidents.append(incident)

                self.log_reasoning(
                    decision=f"Auto-raised incident: {incident.incident_type.value} at {zone.zone_name}",
                    factors=[
                        {"factor": "surge_detected", "weight": 0.9, "value": str(surge_detected)},
                        {"factor": "occupancy_percentage", "weight": 0.8, "value": f"{zone.occupancy_percentage}%"},
                    ],
                )

            self._previous_occupancy[zone.zone_id] = zone.occupancy_percentage
        for zone in crowd_data.zones:
            if zone.status != ZoneStatus.CRITICAL:
                self._resolve_stale_incidents(zone.zone_id)

        return new_incidents

    def _is_sudden_surge(self, zone_id: str, current_pct: float) -> bool:
        """A jump of 25%+ occupancy within one polling cycle counts as a surge."""
        previous = self._previous_occupancy.get(zone_id)
        if previous is None:
            return False
        return (current_pct - previous) >= 25

    def _resolve_stale_incidents(self, zone_id: str) -> None:
        """Clears incidents for a zone once it's no longer critical, so the
        dashboard doesn't accumulate stale alerts indefinitely."""
        active = incident_store.get_active()
        for incident in active:
            if incident.zone == zone_id and incident.incident_type == IncidentType.CROWD_SURGE:
                incident_store.resolve(incident.incident_id)

    async def _create_incident(self, zone, surge_detected: bool) -> IncidentAlert:
        incident_type = IncidentType.CROWD_SURGE
        severity = "critical" if zone.status == ZoneStatus.CRITICAL else "high"

        description = (
            f"Sudden crowd surge detected at {zone.zone_name} — occupancy jumped sharply."
            if surge_detected
            else f"{zone.zone_name} has sustained critical occupancy ({zone.occupancy_percentage}%)."
        )
        suggested_action = await self._get_cached_or_generate_action(zone)

        return IncidentAlert(
            incident_id=str(uuid.uuid4()),
            incident_type=incident_type,
            zone=zone.zone_id,
            description=description,
            auto_detected=True,
            suggested_action=suggested_action,
            severity=severity,
            timestamp=datetime.utcnow(),
        )

    async def _get_cached_or_generate_action(self, zone) -> str:
        """
        Avoids hitting Gemini on every 5-second poll for the same ongoing
        incident — only regenerates when the zone's status actually changes.
        This keeps us well within free-tier rate limits during a live demo.
        """
        cache_key = f"{zone.zone_id}:{zone.status.value}"
        if cache_key in self._action_cache:
            return self._action_cache[cache_key]

        action = await self._generate_action(zone.zone_name, zone.occupancy_percentage)
        self._action_cache[cache_key] = action
        return action

    async def _generate_action(self, zone_name: str, occupancy_pct: float) -> str:
        system_instruction = (
            "You are a stadium operations advisor. In one short, direct sentence, "
            "suggest a concrete staff action for a crowd safety incident. "
            "Be specific and actionable, no fluff."
        )
        prompt = f"Zone: {zone_name}, current occupancy: {occupancy_pct}%. Suggest one action."
        fallback = f"Deploy additional staff to {zone_name} and monitor closely."
        return await self._call_gemini(prompt=prompt, system_instruction=system_instruction, fallback=fallback)

    def manually_report_incident(
        self, zone_id: str, incident_type: IncidentType, description: str, severity: str
    ) -> IncidentAlert:
        """Allows staff to manually report incidents too (e.g. lost child, medical)."""
        incident = IncidentAlert(
            incident_id=str(uuid.uuid4()),
            incident_type=incident_type,
            zone=zone_id,
            description=description,
            auto_detected=False,
            suggested_action=self._default_action_for_type(incident_type),
            severity=severity,
            timestamp=datetime.utcnow(),
        )
        incident_store.add(incident)
        return incident

    def _default_action_for_type(self, incident_type: IncidentType) -> str:
        defaults = {
            IncidentType.LOST_PERSON: "Alert nearest Guest Services desk and broadcast description to staff.",
            IncidentType.MEDICAL: "Dispatch nearest medical team immediately.",
            IncidentType.SECURITY: "Notify security team and monitor via nearest camera feed.",
            IncidentType.CROWD_SURGE: "Deploy additional staff and consider redirecting fans.",
        }
        return defaults.get(incident_type, "Notify on-site staff for manual assessment.")
