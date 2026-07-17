"""
Central configuration management for StadiumPulse backend.
Loads all settings from environment variables with sensible defaults.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "StadiumPulse API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Security
    API_SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Voice (LiveKit)
    LIVEKIT_API_KEY: str = ""
    LIVEKIT_API_SECRET: str = ""
    LIVEKIT_URL: str = ""

    # Cache
    CACHE_TTL_SECONDS: int = 300

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — avoids re-reading .env on every call."""
    return Settings()  # type: ignore[call-arg]  # fields are populated from .env at runtime