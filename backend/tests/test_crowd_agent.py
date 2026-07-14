"""
Tests for Crowd Intelligence Agent (Feature 1).
"""
import pytest

from features.crowd.service import CrowdIntelligenceAgent
from shared.schemas import ZoneStatus


@pytest.mark.asyncio
async def test_returns_all_zones_by_default():
    agent = CrowdIntelligenceAgent()
    result = await agent.process()
    assert len(result.zones) == 6  # matches ZONES in sensor_simulator


@pytest.mark.asyncio
async def test_filters_by_zone_ids():
    agent = CrowdIntelligenceAgent()
    result = await agent.process(zone_ids=["gate_1"])
    assert len(result.zones) == 1
    assert result.zones[0].zone_id == "gate_1"


@pytest.mark.asyncio
async def test_classifies_critical_status_correctly():
    agent = CrowdIntelligenceAgent()
    assert agent._classify_status(95) == ZoneStatus.CRITICAL
    assert agent._classify_status(75) == ZoneStatus.ELEVATED
    assert agent._classify_status(40) == ZoneStatus.NORMAL


@pytest.mark.asyncio
async def test_overall_status_reflects_worst_zone():
    agent = CrowdIntelligenceAgent()
    result = await agent.process()
    zone_statuses = [z.status for z in result.zones]
    if ZoneStatus.CRITICAL in zone_statuses:
        assert result.overall_status == ZoneStatus.CRITICAL
    elif ZoneStatus.ELEVATED in zone_statuses:
        assert result.overall_status == ZoneStatus.ELEVATED
    else:
        assert result.overall_status == ZoneStatus.NORMAL


@pytest.mark.asyncio
async def test_prediction_never_exceeds_max_capacity():
    agent = CrowdIntelligenceAgent()
    result = await agent.process()
    for zone in result.zones:
        if zone.predicted_occupancy_10min is not None:
            assert zone.predicted_occupancy_10min <= zone.max_capacity
            assert zone.predicted_occupancy_10min >= 0