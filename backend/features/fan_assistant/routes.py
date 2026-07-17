"""
Fan Assistant API routes (Feature 3).
"""
from fastapi import APIRouter, Depends, Request

from core.errors import AppError
from core.rate_limiter import rate_limit
from features.fan_assistant.schemas import ChatRequest, ChatResponse
from features.fan_assistant.service import FanAssistantAgent

router = APIRouter(prefix="/api/fan-assistant", tags=["Fan Assistant"])
fan_assistant_agent = FanAssistantAgent()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: Request,
    chat_request: ChatRequest,
    _: None = Depends(rate_limit(times=20, per_seconds=60)),
):
    """Multi-language conversational endpoint for fan queries. Token-bucket rate-limited to prevent abuse."""
    try:
        return await fan_assistant_agent.process(chat_request)
    except Exception as e:
        # This endpoint's main failure mode is Gemini being unavailable --
        # tag it as an upstream error (502) rather than a generic 500 so
        # the frontend can show "assistant is temporarily down" instead of
        # a hard error state.
        raise AppError.upstream_error("Gemini", str(e)) from e
