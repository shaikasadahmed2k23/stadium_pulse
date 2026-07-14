"""
Pydantic schemas — request/response models used across all API routes.
Keeping these centralized avoids duplication and keeps type safety consistent.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


# ---------- Shared Enums ----------

class ZoneStatus(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"


class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    PORTUGUESE = "pt"
    ARABIC = "ar"
    HINDI = "hi"


class IncidentType(str, Enum):
    CROWD_SURGE = "crowd_surge"
    LOST_PERSON = "lost_person"
    MEDICAL = "medical"
    SECURITY = "security"


# ---------- Crowd Intelligence (Feature 1) ----------

class ZoneData(BaseModel):
    zone_id: str
    zone_name: str
    current_occupancy: int
    max_capacity: int
    occupancy_percentage: float
    status: ZoneStatus
    predicted_occupancy_10min: Optional[int] = None
    timestamp: datetime


class CrowdPredictionResponse(BaseModel):
    zones: list[ZoneData]
    highest_risk_zone: Optional[str] = None
    overall_status: ZoneStatus


# ---------- Wayfinding (Feature 2) ----------

class NavigationRequest(BaseModel):
    query: str = Field(..., description="Natural language navigation query")
    current_zone: str
    language: Language = Language.ENGLISH
    avoid_zones: list[str] = Field(default_factory=list)
    low_sensory_mode: bool = False  # Feature 7


class NavigationStep(BaseModel):
    instruction: str
    zone: str
    estimated_time_seconds: int
    congestion_level: ZoneStatus


class NavigationResponse(BaseModel):
    route: list[NavigationStep]
    total_estimated_time_seconds: int
    route_avoids_congestion: bool


# ---------- Fan Assistant (Feature 3) ----------

class ChatRequest(BaseModel):
    message: str
    language: Language = Language.ENGLISH
    session_id: str
    fan_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    detected_intent: Optional[str] = None
    routed_to_wayfinding: bool = False
    session_id: str


# ---------- Voice Assistant (Feature 5) ----------

class VoiceSessionRequest(BaseModel):
    fan_id: str
    language: Language = Language.ENGLISH


class VoiceSessionResponse(BaseModel):
    room_name: str
    livekit_token: str
    livekit_url: str


# ---------- Decision Orchestrator (Feature 4 + 6) ----------

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
    active_incidents: list["IncidentAlert"]


# ---------- Anomaly Detection (Feature 8) ----------

class IncidentAlert(BaseModel):
    incident_id: str
    incident_type: IncidentType
    zone: str
    description: str
    auto_detected: bool
    suggested_action: str
    severity: Literal["low", "medium", "high", "critical"]
    timestamp: datetime


ControlRoomState.model_rebuild()