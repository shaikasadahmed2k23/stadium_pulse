"""
Crowd Intelligence Agent (Feature 1).
Simulates live zone occupancy data and predicts near-term congestion
using simple trend extrapolation + Gemini for natural-language risk summaries.
"""
from datetime import UTC, datetime


from features.crowd.schemas import CrowdPredictionResponse
from features.crowd.sensor_simulator import SensorOutput, sensor_simulator
from shared.base_agent import BaseAgent
from shared.schemas import ZoneData, ZoneStatus


class CrowdIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="CrowdIntelligenceAgent")

    async def process(self, zone_ids: list[str] | None = None) -> CrowdPredictionResponse:
        raw_zones = sensor_simulator.get_current_snapshot(zone_ids)

        zones: list[ZoneData] = []
        for raw in raw_zones:
            predicted = self._predict_next_occupancy(raw)
            status = self._classify_status(raw["occupancy_percentage"])

            zone = ZoneData(
                zone_id=raw["zone_id"],
                zone_name=raw["zone_name"],
                current_occupancy=raw["current_occupancy"],
                max_capacity=raw["max_capacity"],
                occupancy_percentage=raw["occupancy_percentage"],
                status=status,
                predicted_occupancy_10min=predicted,
                timestamp=datetime.now(UTC),
            )
            zones.append(zone)

        highest_risk = max(zones, key=lambda z: z.occupancy_percentage, default=None)
        overall_status = self._overall_status(zones)

        self.log_reasoning(
            decision=f"Overall stadium status: {overall_status.value}",
            factors=[
                {"factor": "highest_risk_zone", "weight": 1.0, "value": highest_risk.zone_name if highest_risk else "none"},
                {"factor": "zones_evaluated", "weight": 0.5, "value": str(len(zones))},
            ],
        )

        return CrowdPredictionResponse(
            zones=zones,
            highest_risk_zone=highest_risk.zone_id if highest_risk else None,
            overall_status=overall_status,
        )

    def _predict_next_occupancy(self, raw: SensorOutput) -> int:    
        """Simple linear trend extrapolation — no heavy ML needed for a solid demo."""
        trend_rate = raw.get("trend_rate", 0)
        current = raw["current_occupancy"]
        predicted = int(current + (trend_rate * 10))
        return max(0, min(predicted, raw["max_capacity"]))

    def _classify_status(self, occupancy_pct: float) -> ZoneStatus:
        if occupancy_pct >= 90:
            return ZoneStatus.CRITICAL
        elif occupancy_pct >= 70:
            return ZoneStatus.ELEVATED
        return ZoneStatus.NORMAL

    def _overall_status(self, zones: list[ZoneData]) -> ZoneStatus:
        if any(z.status == ZoneStatus.CRITICAL for z in zones):
            return ZoneStatus.CRITICAL
        if any(z.status == ZoneStatus.ELEVATED for z in zones):
            return ZoneStatus.ELEVATED
        return ZoneStatus.NORMAL
