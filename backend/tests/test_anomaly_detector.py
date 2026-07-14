"""
Tests for Anomaly Detector (Feature 8).
"""
import pytest
from agents.anomaly_detector import AnomalyDetector
from models.schemas import IncidentType


@pytest.mark.asyncio
async def test_manual_incident_report_creates_valid_incident(reset_incident_store):
    detector = AnomalyDetector()
    incident = detector.manually_report_incident(
        zone_id="concourse_a",
        incident_type=IncidentType.LOST_PERSON,
        description="Child reported missing near Concourse A",
        severity="high",
    )
    assert incident.auto_detected is False
    assert incident.zone == "concourse_a"
    assert incident.severity == "high"
    assert "Guest Services" in incident.suggested_action


@pytest.mark.asyncio
async def test_surge_detection_requires_previous_reading():
    detector = AnomalyDetector()
    # First call has no previous_occupancy baseline yet, so surge check should be False
    assert detector._is_sudden_surge("gate_1", 80) is False


@pytest.mark.asyncio
async def test_surge_detection_flags_large_jump():
    detector = AnomalyDetector()
    detector._previous_occupancy["gate_1"] = 40
    assert detector._is_sudden_surge("gate_1", 70) is True  # 30% jump


@pytest.mark.asyncio
async def test_surge_detection_ignores_small_change():
    detector = AnomalyDetector()
    detector._previous_occupancy["gate_1"] = 40
    assert detector._is_sudden_surge("gate_1", 50) is False  # only 10% jump