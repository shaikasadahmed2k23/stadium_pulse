"""
Tests for the stadium navigation graph service — currently untested
directly (only indirectly through Wayfinding Agent tests).
"""
from features.wayfinding.graph import stadium_graph


def test_all_zone_ids_returns_expected_zones():
    zones = stadium_graph.all_zone_ids()
    assert "gate_1" in zones
    assert "section_101" in zones
    assert len(zones) == 6


def test_default_zone_is_valid():
    default = stadium_graph.default_zone()
    assert default in stadium_graph.all_zone_ids()


def test_get_zone_info_returns_valid_structure():
    info = stadium_graph.get_zone_info("gate_1")
    assert "instruction" in info
    assert "base_time_seconds" in info
    assert info["base_time_seconds"] > 0


def test_get_zone_info_falls_back_for_unknown_zone():
    info = stadium_graph.get_zone_info("nonexistent_zone")
    assert info is not None


def test_high_stimulus_zones_returns_correct_set():
    high_stimulus = stadium_graph.high_stimulus_zones()
    assert "gate_1" in high_stimulus
    assert "section_101" not in high_stimulus


def test_direct_route_same_start_and_end():
    route = stadium_graph.find_route("gate_1", "gate_1", avoid_zones=set(), congestion_map={})
    assert route == ["gate_1"]


def test_route_between_connected_zones():
    route = stadium_graph.find_route("gate_1", "concourse_a", avoid_zones=set(), congestion_map={})
    assert route[0] == "gate_1"
    assert route[-1] == "concourse_a"


def test_route_avoids_explicitly_blocked_zone():
    route = stadium_graph.find_route(
        "gate_1", "section_101", avoid_zones={"concourse_a"}, congestion_map={}
    )
    assert route[-1] == "section_101"


def test_route_prefers_avoiding_critical_congestion():
    from shared.schemas import ZoneStatus

    congestion_map = {"concourse_a": ZoneStatus.CRITICAL}
    route = stadium_graph.find_route(
        "gate_3", "concourse_b", avoid_zones=set(), congestion_map=congestion_map
    )
    assert route[-1] == "concourse_b"


def test_no_route_returns_direct_fallback():
    route = stadium_graph.find_route("nonexistent_a", "nonexistent_b", avoid_zones=set(), congestion_map={})
    assert route == ["nonexistent_b"]
