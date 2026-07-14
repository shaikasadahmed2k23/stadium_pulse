"""
Decision Orchestrator Agent (Feature 4 + 6).
The "control room brain" — aggregates signals from Crowd Intelligence
and active incidents, then generates prioritized, explainable
recommendations for staff. Every recommendation carries its reasoning
factors so the dashboard can show *why*, not just *what*.
"""
from agents.base_agent import BaseAgent
from agents.crowd_intelligence_agent import CrowdIntelligenceAgent
from models.schemas import (
    DecisionRecommendation,
    ReasoningFactor,
    ControlRoomState,
    ZoneStatus,
    IncidentAlert,
)
from services.incident_store import incident_store
import uuid
from datetime import datetime


class DecisionOrchestrator(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="DecisionOrchestrator")
        self.crowd_agent = CrowdIntelligenceAgent()

    async def process(self, _: None = None) -> ControlRoomState:
        crowd_data = await self.crowd_agent.process()
        active_incidents = incident_store.get_active()

        recommendations: list[DecisionRecommendation] = []

        # Congestion-based recommendations
        for zone in crowd_data.zones:
            if zone.status in (ZoneStatus.ELEVATED, ZoneStatus.CRITICAL):
                rec = await self._build_congestion_recommendation(zone, crowd_data.zones)
                recommendations.append(rec)

        # Incident-based recommendations
        for incident in active_incidents:
            rec = self._build_incident_recommendation(incident)
            recommendations.append(rec)

        return ControlRoomState(
            zones=crowd_data.zones,
            active_recommendations=recommendations,
            active_incidents=active_incidents,
        )

    async def _build_congestion_recommendation(self, zone, all_zones) -> DecisionRecommendation:
        # Find a nearby zone with spare capacity to suggest as redirect target
        alternative = min(
            (z for z in all_zones if z.zone_id != zone.zone_id),
            key=lambda z: z.occupancy_percentage,
            default=None,
        )

        confidence = min(0.95, 0.5 + (zone.occupancy_percentage / 200))
        priority = "critical" if zone.status == ZoneStatus.CRITICAL else "high"

        action = (
            f"Redirect fans from {zone.zone_name} to {alternative.zone_name}"
            if alternative else f"Deploy additional staff to {zone.zone_name}"
        )

        factors = [
            ReasoningFactor(factor="occupancy_percentage", weight=0.8, value=f"{zone.occupancy_percentage}%"),
            ReasoningFactor(factor="predicted_10min", weight=0.6, value=str(zone.predicted_occupancy_10min)),
            ReasoningFactor(
                factor="alternative_capacity",
                weight=0.5,
                value=f"{alternative.zone_name} at {alternative.occupancy_percentage}%" if alternative else "none available",
            ),
        ]

        self.log_reasoning(decision=action, factors=[f.model_dump() for f in factors])

        return DecisionRecommendation(
            recommendation_id=str(uuid.uuid4()),
            action=action,
            affected_zones=[zone.zone_id] + ([alternative.zone_id] if alternative else []),
            confidence_score=round(confidence, 2),
            reasoning_factors=factors,
            priority=priority,
            timestamp=datetime.utcnow(),
        )

    def _build_incident_recommendation(self, incident: IncidentAlert) -> DecisionRecommendation:
        factors = [
            ReasoningFactor(factor="incident_type", weight=1.0, value=incident.incident_type.value),
            ReasoningFactor(factor="auto_detected", weight=0.7, value=str(incident.auto_detected)),
            ReasoningFactor(factor="severity", weight=0.9, value=incident.severity),
        ]

        self.log_reasoning(decision=incident.suggested_action, factors=[f.model_dump() for f in factors])

        return DecisionRecommendation(
            recommendation_id=str(uuid.uuid4()),
            action=incident.suggested_action,
            affected_zones=[incident.zone],
            confidence_score=0.9 if incident.auto_detected else 0.75,
            reasoning_factors=factors,
            priority=incident.severity,
            timestamp=datetime.utcnow(),
        )