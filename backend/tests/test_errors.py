"""
Tests for the AppError hierarchy — factory methods must return the
correct status code + error code pairing, since routes rely on these
being consistent (see core/error_handlers.py).
"""
from core.errors import AppError, ErrorCode


def test_not_found_returns_404():
    err = AppError.not_found("Zone")
    assert err.status_code == 404
    assert err.code == ErrorCode.NOT_FOUND
    assert "Zone" in err.message


def test_validation_error_returns_422():
    err = AppError.validation_error("zone_id is required")
    assert err.status_code == 422
    assert err.code == ErrorCode.VALIDATION_ERROR


def test_upstream_error_returns_502_with_service_name():
    err = AppError.upstream_error("Gemini", "timeout after 10s")
    assert err.status_code == 502
    assert err.code == ErrorCode.UPSTREAM_ERROR
    assert "Gemini" in err.message
    assert "timeout after 10s" in err.message


def test_upstream_error_without_detail_omits_colon():
    err = AppError.upstream_error("LiveKit")
    assert err.message == "LiveKit is temporarily unavailable"


def test_unauthorized_defaults_to_401():
    err = AppError.unauthorized()
    assert err.status_code == 401
    assert err.code == ErrorCode.UNAUTHORIZED


def test_rate_limited_returns_429():
    err = AppError.rate_limited()
    assert err.status_code == 429
    assert err.code == ErrorCode.RATE_LIMITED


def test_internal_defaults_to_500():
    err = AppError.internal()
    assert err.status_code == 500
    assert err.code == ErrorCode.INTERNAL_ERROR


def test_app_error_is_an_exception():
    err = AppError.not_found("Incident")
    assert isinstance(err, Exception)
    assert str(err) == "Incident not found"
