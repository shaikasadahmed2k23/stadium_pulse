"""
Fan Assistant Agent (Feature 3).
Multi-language conversational assistant for FAQs, tickets, and general
stadium queries. Detects when a request is actually a navigation query
and routes it to the Wayfinding Agent instead of trying to answer it
directly — keeps each agent focused on what it does best.
"""
import re

from core.security import sanitize_user_input
from features.fan_assistant.faq_data import faq_knowledge
from features.fan_assistant.schemas import ChatRequest, ChatResponse
from shared.base_agent import BaseAgent


class FanAssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="FanAssistantAgent")

    async def process(self, request: ChatRequest) -> ChatResponse:
        request.message = sanitize_user_input(request.message)
        intent = await self._detect_intent(request.message, request.language.value)

        if intent == "navigation":
            reply = await self._navigation_redirect_message(request.language.value)
            self.log_reasoning(
                decision="Routed to Wayfinding Agent",
                factors=[{"factor": "detected_intent", "weight": 1.0, "value": "navigation"}],
            )
            return ChatResponse(
                reply=reply,
                detected_intent=intent,
                routed_to_wayfinding=True,
                session_id=request.session_id,
            )

        # Otherwise, answer using FAQ knowledge + Gemini for natural phrasing
        context = faq_knowledge.get_relevant_context(request.message)
        reply = await self._generate_answer(request.message, context, request.language.value)

        self.log_reasoning(
            decision=f"Answered FAQ intent: {intent}",
            factors=[{"factor": "detected_intent", "weight": 1.0, "value": intent}],
        )

        return ChatResponse(
            reply=reply,
            detected_intent=intent,
            routed_to_wayfinding=False,
            session_id=request.session_id,
        )

    async def _detect_intent(self, message: str, language: str) -> str:
        system_instruction = (
            "Classify the fan's message into exactly one category: "
            "'navigation' (asking how to get somewhere, directions, nearest gate/exit/restroom), "
            "'ticket' (ticket/seat/entry issues), "
            "'general' (anything else, FAQs, amenities, schedules). "
            "Respond with ONLY the category word, nothing else."
        )
        response = await self._call_gemini(prompt=message, system_instruction=system_instruction)
        cleaned = re.sub(r"[^a-z]", "", response.strip().lower())
        return cleaned if cleaned in ("navigation", "ticket", "general") else "general"

    async def _navigation_redirect_message(self, language: str) -> str:
        system_instruction = (
            f"Respond in language code '{language}'. Tell the fan briefly and warmly "
            "that you're pulling up navigation help for their request, in one short sentence."
        )
        return await self._call_gemini(prompt="Generate the redirect message.", system_instruction=system_instruction)

    async def _generate_answer(self, message: str, context: str, language: str) -> str:
        system_instruction = (
            f"You are a friendly FIFA World Cup 2026 stadium assistant. Respond in language "
            f"code '{language}'. Use this context if relevant: {context}. "
            "Keep answers short, warm, and helpful — 2-3 sentences max."
        )
        return await self._call_gemini(prompt=message, system_instruction=system_instruction)
