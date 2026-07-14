"""
Fan Assistant API routes (Feature 3).
"""
from fastapi import APIRouter, Request

from core.errors import AppError
from core.rate_limiter import limiter
from features.fan_assistant.schemas import ChatRequest, ChatResponse
from features.fan_assistant.service import FanAssistantAgent

router = APIRouter(prefix="/api/fan-assistant", tags=["Fan Assistant"])
fan_assistant_agent = FanAssistantAgent()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_assistant(request: Request, chat_request: ChatRequest):
    """Multi-language conversational endpoint for fan queries. Rate-limited to prevent abuse."""
    try:
        return await fan_assistant_agent.process(chat_request)
    except Exception as e:
        # This endpoint's main failure mode is Gemini being unavailable --
        # tag it as an upstream error (502) rather than a generic 500 so
        # the frontend can show "assistant is temporarily down" instead of
        # a hard error state.
        raise AppError.upstream_error("Gemini", str(e)) from e
