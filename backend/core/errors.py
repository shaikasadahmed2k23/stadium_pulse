"""
Centralized application error hierarchy.

Before this, every route repeated the same `try/except Exception ->
HTTPException(500, f"X failed: {e}")` pattern. That flattens every failure
(bad input, a downed Gemini API, an unauthorized request) into an identical
500, and duplicates the same logging line five times across the codebase.

AppError + the handlers registered in main.py collapse that into one place:
routes raise a typed error via the factory methods below, and the global
handler logs it once and shapes the JSON response once. Anything that is
NOT raised as an AppError is treated as an actual bug (see the catch-all
`Exception` handler in main.py) and gets logged with a full stack trace.
"""
from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UPSTREAM_ERROR = "upstream_error"   # Gemini / LiveKit / Supabase failures
    UNAUTHORIZED = "unauthorized"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"


class AppError(Exception):
    """
    Base application exception. Carries an HTTP status code, a
    machine-readable error code (stable for frontend error handling), and a
    user-safe message. Don't raise this directly — use the factory
    classmethods so error codes/status pairs stay consistent everywhere.
    """

    def __init__(self, status_code: int, code: ErrorCode, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)

    @classmethod
    def not_found(cls, resource: str) -> "AppError":
        return cls(404, ErrorCode.NOT_FOUND, f"{resource} not found")

    @classmethod
    def validation_error(cls, message: str) -> "AppError":
        return cls(422, ErrorCode.VALIDATION_ERROR, message)

    @classmethod
    def upstream_error(cls, service: str, detail: str = "") -> "AppError":
        """Use when a downstream dependency (Gemini, LiveKit, Supabase)
        fails — 502 signals it's not this API's fault, distinct from a 500
        which means our own code broke."""
        message = f"{service} is temporarily unavailable"
        if detail:
            message += f": {detail}"
        return cls(502, ErrorCode.UPSTREAM_ERROR, message)

    @classmethod
    def unauthorized(cls, message: str = "Invalid or missing credentials") -> "AppError":
        return cls(401, ErrorCode.UNAUTHORIZED, message)

    @classmethod
    def rate_limited(cls, message: str = "Too many requests, please slow down") -> "AppError":
        return cls(429, ErrorCode.RATE_LIMITED, message)

    @classmethod
    def internal(cls, message: str = "Something went wrong") -> "AppError":
        return cls(500, ErrorCode.INTERNAL_ERROR, message)
