"""
Voice service (Feature 5) — generates LiveKit room tokens for fans to
start a real-time voice session with the Fan Assistant. Reuses the same
LiveKit pattern as Dr. Paws, adapted for multi-language stadium queries.
"""
import logging
import uuid

from livekit import api

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceService:
    def __init__(self):
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.livekit_url = settings.LIVEKIT_URL

    def create_voice_session(self, fan_id: str, language: str) -> dict:
        """
        Creates a unique room + access token for a fan's voice session.
        The agent worker (features/voice/worker.py) joins this same room
        to handle the actual conversation.
        """
        room_name = f"fan-{fan_id}-{uuid.uuid4().hex[:8]}"

        token = (
            api.AccessToken(self.api_key, self.api_secret)
            .with_identity(fan_id)
            .with_name(f"Fan-{fan_id}")
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .with_metadata(f'{{"language": "{language}"}}')
            .to_jwt()
        )

        logger.info(f"Voice session created for fan {fan_id} in room {room_name}")

        return {
            "room_name": room_name,
            "livekit_token": token,
            "livekit_url": self.livekit_url,
        }


voice_service = VoiceService()
