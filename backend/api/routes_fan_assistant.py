"""
Fan Assistant API routes (Feature 3).
"""
from fastapi import APIRouter, HTTPException, Request

from agents.fan_assistant_agent import FanAssistantAgent
from core.rate_limiter import limiter
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/fan-assistant", tags=["Fan Assistant"])
fan_assistant_agent = FanAssistantAgent()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_assistant(request: Request, chat_request: ChatRequest):
    """Multi-language conversational endpoint for fan queries. Rate-limited to prevent abuse."""
    try:
        return await fan_assistant_agent.process(chat_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")