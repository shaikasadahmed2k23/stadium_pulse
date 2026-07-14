"""
Voice Agent Worker (Feature 5).
This runs as a separate LiveKit agent worker process — it joins the
room created by voice/service.py, listens to the fan's speech, transcribes
it, routes through the Fan Assistant Agent for a reply, then speaks
the response back. This mirrors the Dr. Paws pipeline structure.

Run separately from the main API: `python -m features.voice.worker`
"""
import json
import logging
import uuid

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, silero

from features.fan_assistant.schemas import ChatRequest
from features.fan_assistant.service import FanAssistantAgent
from shared.schemas import Language

logger = logging.getLogger(__name__)
fan_assistant = FanAssistantAgent()


class StadiumVoiceAgent(Agent):
    """
    Wraps the Fan Assistant Agent's text logic with speech-to-text and
    text-to-speech, so voice queries get the same intent detection and
    FAQ/navigation routing as the text chat interface.
    """

    def __init__(self, language: str = "en"):
        super().__init__(
            instructions=(
                f"You are a helpful FIFA World Cup 2026 stadium voice assistant. "
                f"Respond in language code '{language}'. Keep responses short and clear "
                f"since this is a spoken conversation."
            )
        )
        self.language = language
        self.session_id = str(uuid.uuid4())

    async def on_user_speech_committed(self, text: str) -> str:
        """Routes transcribed speech through the same Fan Assistant logic as text chat."""
        request = ChatRequest(
            message=text,
            language=Language(self.language),
            session_id=self.session_id,
        )
        response = await fan_assistant.process(request)
        return response.reply


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    participant_metadata = {}
    if ctx.room.local_participant.metadata:
        try:
            participant_metadata = json.loads(ctx.room.local_participant.metadata)
        except Exception:
            logger.warning("Could not parse participant metadata, defaulting to English")

    language = participant_metadata.get("language", "en")

    session = AgentSession(
        stt=openai.STT(),
        llm=openai.LLM(),  # response generation delegated to StadiumVoiceAgent logic
        tts=openai.TTS(),
        vad=silero.VAD.load(),
    )

    await session.start(
        agent=StadiumVoiceAgent(language=language),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
