"""
Crowd Intelligence schemas (Feature 1).
"""

from pydantic import BaseModel

from shared.schemas import ZoneData, ZoneStatus


class CrowdPredictionResponse(BaseModel):
    zones: list[ZoneData]
    highest_risk_zone: str | None = None
    overall_status: ZoneStatus
