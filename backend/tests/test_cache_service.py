"""
Tests for the in-memory TTL cache service (efficiency-critical component).
"""
from services.cache_service import CacheService


def test_set_and_get_returns_value():
    cache = CacheService()
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_get_missing_key_returns_none():
    cache = CacheService()
    assert cache.get("nonexistent") is None


def test_clear_removes_all_entries():
    cache = CacheService()
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_overwriting_key_updates_value():
    cache = CacheService()
    cache.set("key1", "original")
    cache.set("key1", "updated")
    assert cache.get("key1") == "updated"
