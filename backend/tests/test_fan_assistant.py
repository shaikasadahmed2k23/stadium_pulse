"""
Tests for Fan Assistant Agent (Feature 3).
"""
import pytest
from unittest.mock import AsyncMock, patch
from agents.fan_assistant_agent import FanAssistantAgent
from models.schemas import ChatRequest, Language


@pytest.mark.asyncio
async def test_navigation_intent_routes_correctly():
    with patch.object(FanAssistantAgent, "_detect_intent", new_callable=AsyncMock) as mock_intent:
        mock_intent.return_value = "navigation"
        agent = FanAssistantAgent()
        request = ChatRequest(message="where is the nearest exit", language=Language.ENGLISH, session_id="test-1")
        result = await agent.process(request)
        assert result.routed_to_wayfinding is True
        assert result.detected_intent == "navigation"


@pytest.mark.asyncio
async def test_general_intent_does_not_route_to_wayfinding():
    with patch.object(FanAssistantAgent, "_detect_intent", new_callable=AsyncMock) as mock_intent:
        mock_intent.return_value = "general"
        agent = FanAssistantAgent()
        request = ChatRequest(message="what time does the match start", language=Language.ENGLISH, session_id="test-2")
        result = await agent.process(request)
        assert result.routed_to_wayfinding is False
        assert result.detected_intent == "general"


@pytest.mark.asyncio
async def test_session_id_is_preserved_in_response():
    with patch.object(FanAssistantAgent, "_detect_intent", new_callable=AsyncMock) as mock_intent:
        mock_intent.return_value = "general"
        agent = FanAssistantAgent()
        request = ChatRequest(message="hello", language=Language.ENGLISH, session_id="unique-session-123")
        result = await agent.process(request)
        assert result.session_id == "unique-session-123"