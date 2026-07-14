"""
Simple in-memory LRU cache with TTL. Keeps things fast without needing
Redis set up on day one — can swap to Redis later without changing
the interface used elsewhere in the codebase.
"""
from cachetools import TTLCache
from core.config import get_settings
import threading

settings = get_settings()


class CacheService:
    def __init__(self):
        self._cache = TTLCache(maxsize=500, ttl=settings.CACHE_TTL_SECONDS)
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value) -> None:
        with self._lock:
            self._cache[key] = value

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


cache_service = CacheService()