"""
Base agent class — shared foundation for all StadiumPulse agents.
Handles Gemini client setup, reasoning logging, and common utilities
so individual agents stay focused on their own logic.
"""
from abc import ABC, abstractmethod
from typing import Any
import logging
from services.gemini_client import GeminiClient
from services.reasoning_logger import ReasoningLogger

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Every agent (Crowd, Wayfinding, Fan Assistant, Decision Orchestrator,
    Anomaly Detector) inherits from this. Keeps Gemini calls, error handling,
    and reasoning capture consistent across the system.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.gemini = GeminiClient()
        self.reasoning_logger = ReasoningLogger(agent_name=agent_name)
        logger.info(f"[{self.agent_name}] Agent initialized")

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Every agent must implement its own process method."""
        raise NotImplementedError

    async def _call_gemini(self, prompt: str, system_instruction: str = "", fallback: str = "") -> str:
        """
        Centralized Gemini call so retries, error handling, and logging
        are consistent everywhere instead of duplicated per agent. On
        failure (e.g. quota exceeded), returns a fallback instead of
        propagating — a single LLM hiccup should never crash the
        live WebSocket feed or take down the whole agent pipeline.
        """
        try:
            response = await self.gemini.generate(
                prompt=prompt,
                system_instruction=system_instruction,
            )
            return response
        except Exception as e:
            logger.error(f"[{self.agent_name}] Gemini call failed: {str(e)}")
            return fallback or "Unable to generate response at this time."
    def log_reasoning(self, decision: str, factors: list[dict]) -> None:
        """Feature 6 — every agent logs *why* it made a decision."""
        self.reasoning_logger.log(decision=decision, factors=factors)