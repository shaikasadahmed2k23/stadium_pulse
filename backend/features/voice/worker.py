"""
Voice Agent Worker (Feature 5).
This runs as a separate LiveKit agent worker process — it joins the
room created by voice/service.py and handles real-time voice conversation
using Gemini Live API (RealtimeModel), which does STT+LLM+TTS in one model.
Run separately from the main API: `python -m features.voice.worker dev`
"""


import json
import logging

from dotenv import load_dotenv

load_dotenv()



from google.genai import types  # noqa: E402
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli  # noqa: E402
from livekit.plugins.google.realtime import RealtimeModel  # noqa: E402

from core.config import get_settings  # noqa: E402

logger = logging.getLogger(__name__)
settings = get_settings()


class StadiumVoiceAgent(Agent):
    def __init__(self, language: str = "en"):
        super().__init__(
            instructions=(
                f"You are a helpful FIFA World Cup 2026 stadium voice assistant. "
                f"Respond in language code '{language}'. Keep responses short and clear "
                f"since this is a spoken conversation. Help fans with directions, "
                f"tickets, amenities, and general stadium questions."
            )
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    participant_metadata = {}
    if ctx.room.local_participant.metadata:
        try:
            participant_metadata = json.loads(ctx.room.local_participant.metadata)
        except Exception:
            logger.warning("Could not parse participant metadata, defaulting to English")
    language = participant_metadata.get("language", "en")

    session: AgentSession = AgentSession(
        llm=RealtimeModel(
            api_key=settings.GEMINI_API_KEY,
            voice="Puck",
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        ),
    )

    await session.start(
        agent=StadiumVoiceAgent(language=language),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            load_threshold=float("inf"),  # free-tier CPU is too limited for load-based gating
        )
    )