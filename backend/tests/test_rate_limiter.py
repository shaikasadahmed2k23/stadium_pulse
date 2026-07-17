"""
Tests for the token-bucket rate limiter -- verifies burst capacity,
throttling once exhausted, refill over time, and that separate clients
don't share a bucket.
"""
import time

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from core.errors import AppError
from core.rate_limiter import TokenBucket, TokenBucketLimiter, rate_limit


class TestTokenBucket:
    def test_allows_requests_up_to_capacity(self):
        bucket = TokenBucket(capacity=3, refill_rate=1)
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is True

    def test_rejects_once_capacity_exhausted(self):
        bucket = TokenBucket(capacity=2, refill_rate=0.001)  # near-zero refill for this test
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False

    def test_refills_over_time(self):
        bucket = TokenBucket(capacity=1, refill_rate=100)  # fast refill: 100 tokens/sec
        assert bucket.consume() is True
        assert bucket.consume() is False  # immediately exhausted
        time.sleep(0.02)  # ~2 tokens worth of refill time at 100/sec
        assert bucket.consume() is True

    def test_never_exceeds_capacity(self):
        bucket = TokenBucket(capacity=2, refill_rate=1000)
        time.sleep(0.05)  # would refill far more than capacity if unbounded
        assert bucket.tokens <= 2
        # after refill logic runs on next consume, tokens is clamped
        bucket.consume(amount=0)  # trigger a refill calc without spending
        assert bucket.tokens <= 2


class TestTokenBucketLimiter:
    def test_separate_clients_get_separate_buckets(self):
        limiter = TokenBucketLimiter()
        # client A exhausts its bucket
        for _ in range(5):
            limiter.check("client-a", "/api/test", times=5, per_seconds=60)
        with pytest.raises(AppError):
            limiter.check("client-a", "/api/test", times=5, per_seconds=60)

        # client B should be unaffected -- separate bucket
        limiter.check("client-b", "/api/test", times=5, per_seconds=60)

    def test_separate_routes_get_separate_buckets(self):
        limiter = TokenBucketLimiter()
        for _ in range(5):
            limiter.check("client-a", "/api/route-one", times=5, per_seconds=60)
        with pytest.raises(AppError):
            limiter.check("client-a", "/api/route-one", times=5, per_seconds=60)

        # same client, different route -- separate bucket
        limiter.check("client-a", "/api/route-two", times=5, per_seconds=60)

    def test_raises_app_error_with_rate_limited_code(self):
        limiter = TokenBucketLimiter()
        limiter.check("client-x", "/api/route", times=1, per_seconds=60)
        with pytest.raises(AppError) as exc_info:
            limiter.check("client-x", "/api/route", times=1, per_seconds=60)
        assert exc_info.value.status_code == 429


@pytest.fixture
def rate_limited_client():
    app = FastAPI()

    @app.get("/limited")
    async def limited_endpoint(request: Request, _: None = Depends(rate_limit(times=2, per_seconds=60))):
        return {"ok": True}

    from core.error_handlers import register_error_handlers

    register_error_handlers(app)
    return TestClient(app)


def test_fastapi_dependency_allows_burst_then_blocks(rate_limited_client):
    assert rate_limited_client.get("/limited").status_code == 200
    assert rate_limited_client.get("/limited").status_code == 200
    response = rate_limited_client.get("/limited")
    assert response.status_code == 429
    assert response.json()["error"] == "rate_limited"
