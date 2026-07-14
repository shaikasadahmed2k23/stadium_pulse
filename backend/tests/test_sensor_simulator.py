"""
Tests for the sensor/crowd data simulator service.
"""
from features.crowd.sensor_simulator import SensorSimulator


def test_snapshot_returns_all_zones_by_default():
    sim = SensorSimulator()
    snapshot = sim.get_current_snapshot()
    assert len(snapshot) == 6


def test_snapshot_filters_by_zone_ids():
    sim = SensorSimulator()
    snapshot = sim.get_current_snapshot(zone_ids=["gate_2"])
    assert len(snapshot) == 1
    assert snapshot[0]["zone_id"] == "gate_2"


def test_occupancy_never_negative_or_over_capacity():
    sim = SensorSimulator()
    for _ in range(20):
        snapshot = sim.get_current_snapshot()
        for zone in snapshot:
            assert zone["current_occupancy"] >= 0
            assert zone["current_occupancy"] <= zone["max_capacity"]


def test_occupancy_percentage_calculated_correctly():
    sim = SensorSimulator()
    snapshot = sim.get_current_snapshot()
    for zone in snapshot:
        expected_pct = round((zone["current_occupancy"] / zone["max_capacity"]) * 100, 1)
        assert zone["occupancy_percentage"] == expected_pct


def test_trigger_surge_spikes_occupancy():
    sim = SensorSimulator()
    sim.trigger_surge("gate_1")
    snapshot = sim.get_current_snapshot(zone_ids=["gate_1"])
    assert snapshot[0]["occupancy_percentage"] >= 90


def test_trigger_surge_ignores_invalid_zone():
    sim = SensorSimulator()
    sim.trigger_surge("invalid_zone_id")
    snapshot = sim.get_current_snapshot()
    assert len(snapshot) == 6
