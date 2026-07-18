"""
Truly cross-feature types only. If a schema is used by two or more
features, it lives here instead of being duplicated or forcing one
feature to import from another feature's schemas.py. Everything else
belongs in its owning feature's schemas.py.
"""
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ZoneStatus(StrEnum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"


class Language(StrEnum):

    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    PORTUGUESE = "pt"
    ARABIC = "ar"
    HINDI = "hi"


class ZoneData(BaseModel):
    """Owned conceptually by the crowd feature, but referenced by
    control_room's ControlRoomState.zones — hence shared, not duplicated."""

    zone_id: str
    zone_name: str
    current_occupancy: int
    max_capacity: int
    occupancy_percentage: float
    status: ZoneStatus
    predicted_occupancy_10min: int | None = None
    timestamp: datetime
