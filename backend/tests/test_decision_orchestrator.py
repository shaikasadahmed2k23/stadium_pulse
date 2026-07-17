"""
Tests for Decision Orchestrator (Feature 4 + 6).
"""
import pytest

from features.control_room.orchestrator_service import DecisionOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_returns_zones_and_recommendations():
    orchestrator = DecisionOrchestrator()
    result = await orchestrator.process()
    assert len(result.zones) == 6
    assert isinstance(result.active_recommendations, list)


@pytest.mark.asyncio
async def test_recommendations_include_reasoning_factors():
    """Feature 6 — every recommendation must be explainable, not a black box."""
    orchestrator = DecisionOrchestrator()
    result = await orchestrator.process()
    for rec in result.active_recommendations:
        assert len(rec.reasoning_factors) > 0
        assert 0 <= rec.confidence_score <= 1
        assert rec.priority in ("low", "medium", "high", "critical")


@pytest.mark.asyncio
async def test_critical_zones_produce_critical_priority():
    orchestrator = DecisionOrchestrator()
    result = await orchestrator.process()
    for rec in result.active_recommendations:
        zone_ids_in_rec = rec.affected_zones
        for zone in result.zones:
            if zone.zone_id in zone_ids_in_rec and zone.status.value == "critical":
                assert rec.priority == "critical"