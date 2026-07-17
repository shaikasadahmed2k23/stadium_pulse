"""
Thin wrapper around the Gemini API. Centralizing this means we only
configure retries, timeouts, and caching in one place.
"""
import hashlib
import logging

import google.generativeai as genai

from core.config import get_settings
from services.cache_service import cache_service

logger = logging.getLogger(__name__)
settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiClient:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generates a response from Gemini. Checks cache first for
        efficiency — many fan queries repeat (e.g. "where is gate 3").
        """
        cache_key = self._make_cache_key(prompt, system_instruction)
        cached = cache_service.get(cache_key)
        if cached:
            logger.info("Cache hit — skipping Gemini call")
            return cached

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(full_prompt)
            result = response.text

            cache_service.set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise

    @staticmethod
    def _make_cache_key(prompt: str, system_instruction: str) -> str:
        raw = f"{system_instruction}::{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()