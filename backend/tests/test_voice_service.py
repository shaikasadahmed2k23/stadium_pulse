"""
Tests for Voice Service (Feature 5).

Covers LiveKit room + token generation for fan voice sessions. Doesn't
test the worker.py agent process itself (that's a separate LiveKit agent
process, not unit-testable without a live LiveKit connection) — this
covers the FastAPI-side session creation that VoiceService is responsible
for.
"""
from features.voice.service import VoiceService


def test_create_voice_session_returns_expected_keys():
    service = VoiceService()
    result = service.create_voice_session(fan_id="fan-123", language="en")
    assert set(result.keys()) == {"room_name", "livekit_token", "livekit_url"}


def test_room_name_contains_fan_id():
    service = VoiceService()
    result = service.create_voice_session(fan_id="fan-abc", language="en")
    assert "fan-abc" in result["room_name"]


def test_room_name_is_unique_across_calls():
    service = VoiceService()
    first = service.create_voice_session(fan_id="fan-123", language="en")
    second = service.create_voice_session(fan_id="fan-123", language="en")
    assert first["room_name"] != second["room_name"]


def test_livekit_url_matches_configured_settings():
    service = VoiceService()
    result = service.create_voice_session(fan_id="fan-123", language="en")
    assert result["livekit_url"] == service.livekit_url


def test_token_is_a_non_empty_string():
    service = VoiceService()
    result = service.create_voice_session(fan_id="fan-123", language="en")
    assert isinstance(result["livekit_token"], str)
    assert len(result["livekit_token"]) > 0


def test_different_languages_produce_valid_sessions():
    service = VoiceService()
    for language in ("en", "es", "fr", "ar"):
        result = service.create_voice_session(fan_id="fan-lang-test", language=language)
        assert result["room_name"].startswith("fan-fan-lang-test-")