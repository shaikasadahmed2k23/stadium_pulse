"""
Control Room schemas (Feature 4 + 6 + 8).
"""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from shared.schemas import ZoneData


class IncidentType(str, Enum):
    CROWD_SURGE = "crowd_surge"
    LOST_PERSON = "lost_person"
    MEDICAL = "medical"
    SECURITY = "security"


class IncidentAlert(BaseModel):
    incident_id: str
    incident_type: IncidentType
    zone: str
    description: str
    auto_detected: bool
    suggested_action: str
    severity: Literal["low", "medium", "high", "critical"]
    timestamp: datetime


class ReasoningFactor(BaseModel):
    factor: str
    weight: float
    value: str


class DecisionRecommendation(BaseModel):
    recommendation_id: str
    action: str
    affected_zones: list[str]
    confidence_score: float = Field(..., ge=0, le=1)
    reasoning_factors: list[ReasoningFactor]  # Feature 6 - transparency
    priority: Literal["low", "medium", "high", "critical"]
    timestamp: datetime


class ControlRoomState(BaseModel):
    zones: list[ZoneData]
    active_recommendations: list[DecisionRecommendation]
    active_incidents: list[IncidentAlert]
