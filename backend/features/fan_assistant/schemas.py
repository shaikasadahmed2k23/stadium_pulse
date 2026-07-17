"""
Fan Assistant schemas (Feature 3).
"""

from pydantic import BaseModel

from shared.schemas import Language


class ChatRequest(BaseModel):
    message: str
    language: Language = Language.ENGLISH
    session_id: str
    fan_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    detected_intent: str | None = None
    routed_to_wayfinding: bool = False
    session_id: str
