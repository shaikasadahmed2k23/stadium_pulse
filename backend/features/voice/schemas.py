"""
Voice Assistant schemas (Feature 5).
"""
from pydantic import BaseModel

from shared.schemas import Language


class VoiceSessionRequest(BaseModel):
    fan_id: str
    language: Language = Language.ENGLISH


class VoiceSessionResponse(BaseModel):
    room_name: str
    livekit_token: str
    livekit_url: str
