"""
Voice Assistant API routes (Feature 5).
"""
from fastapi import APIRouter, HTTPException
from services.voice_service import voice_service
from models.schemas import VoiceSessionRequest, VoiceSessionResponse

router = APIRouter(prefix="/api/voice", tags=["Voice Assistant"])


@router.post("/session", response_model=VoiceSessionResponse)
async def create_voice_session(request: VoiceSessionRequest):
    """Creates a LiveKit room + token for the fan to start a voice conversation."""
    try:
        session = voice_service.create_voice_session(
            fan_id=request.fan_id,
            language=request.language.value,
        )
        return VoiceSessionResponse(**session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice session creation failed: {str(e)}")