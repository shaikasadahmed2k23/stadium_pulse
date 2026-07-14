"""
Simulates live stadium sensor/footfall data since we don't have real
IoT sensors. Generates realistic-looking zone occupancy with random
walk trends so the dashboard feels genuinely "live" during the demo.
"""
import random

ZONES = [
    {"zone_id": "gate_1", "zone_name": "Gate 1 - North Entrance", "max_capacity": 5000},
    {"zone_id": "gate_2", "zone_name": "Gate 2 - South Entrance", "max_capacity": 5000},
    {"zone_id": "gate_3", "zone_name": "Gate 3 - East Entrance", "max_capacity": 4000},
    {"zone_id": "concourse_a", "zone_name": "Concourse A", "max_capacity": 8000},
    {"zone_id": "concourse_b", "zone_name": "Concourse B", "max_capacity": 8000},
    {"zone_id": "section_101", "zone_name": "Section 101 Concessions", "max_capacity": 2000},
]


class SensorSimulator:
    def __init__(self):
        self._state = {
            z["zone_id"]: {
                **z,
                "current_occupancy": random.randint(int(z["max_capacity"] * 0.3), int(z["max_capacity"] * 0.6)),
                "trend_rate": random.uniform(-50, 100),
            }
            for z in ZONES
        }

    def get_current_snapshot(self, zone_ids: list[str] | None = None) -> list[dict]:
        self._tick()
        zones = self._state.values()
        if zone_ids:
            zones = [z for z in zones if z["zone_id"] in zone_ids]
        return [self._to_output(z) for z in zones]

    def _tick(self) -> None:
        """Advances the simulation by one step — call before every read."""
        for zone in self._state.values():
            change = zone["trend_rate"] + random.uniform(-30, 30)
            zone["current_occupancy"] = max(
                0, min(zone["max_capacity"], int(zone["current_occupancy"] + change))
            )
            # Occasionally shift the trend so it doesn't move in one direction forever
            if random.random() < 0.1:
                zone["trend_rate"] = random.uniform(-50, 100)

    def _to_output(self, zone: dict) -> dict:
        return {
            "zone_id": zone["zone_id"],
            "zone_name": zone["zone_name"],
            "current_occupancy": zone["current_occupancy"],
            "max_capacity": zone["max_capacity"],
            "occupancy_percentage": round((zone["current_occupancy"] / zone["max_capacity"]) * 100, 1),
            "trend_rate": zone["trend_rate"],
        }

    def trigger_surge(self, zone_id: str) -> None:
        """Feature 8 support — manually spike a zone for anomaly detection demo."""
        if zone_id in self._state:
            self._state[zone_id]["current_occupancy"] = int(self._state[zone_id]["max_capacity"] * 0.95)
            self._state[zone_id]["trend_rate"] = 150


sensor_simulator = SensorSimulator()