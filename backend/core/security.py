"""
Security utilities — API key verification for staff-only endpoints
(Control Room) and input sanitization helpers to reduce prompt-injection
risk before user input reaches Gemini.
"""
import re

from fastapi import Header

from core.config import get_settings
from core.errors import AppError

settings = get_settings()


async def verify_staff_api_key(x_api_key: str = Header(...)) -> str:
    """
    Protects Control Room endpoints — only staff/dashboard clients with
    the correct key can access aggregated state, incidents, and reasoning
    traces. Fan-facing endpoints (chat, navigation, voice) stay public.
    """
    if x_api_key != settings.API_SECRET_KEY:
        raise AppError.unauthorized("Invalid or missing API key")
    return x_api_key


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """
    Basic prompt-injection and abuse mitigation before text reaches Gemini:
    strips control characters, enforces a length cap, and removes common
    instruction-override patterns fans might paste in.
    """
    if not text:
        return ""

    # Strip control/non-printable characters
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", text)

    # Truncate to prevent abuse / token overload
    cleaned = cleaned[:max_length]

    # Neutralize common override attempts (defense-in-depth, not foolproof)
    injection_patterns = [
        r"ignore (all )?previous instructions",
        r"you are now",
        r"system prompt",
        r"disregard (all )?rules",
    ]
    for pattern in injection_patterns:
        cleaned = re.sub(pattern, "[filtered]", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()