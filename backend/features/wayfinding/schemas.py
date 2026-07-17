"""
Wayfinding schemas (Feature 2 + 7).
"""
from pydantic import BaseModel, Field

from shared.schemas import Language, ZoneStatus


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
