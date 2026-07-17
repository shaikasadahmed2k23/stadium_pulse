"""
Token-bucket rate limiter.

Replaces the earlier fixed-window limiter (slowapi's default strategy),
which allows a client to burst up to ~2x its stated limit across a
window boundary -- e.g. 20 requests in the last second of one minute,
then another 20 in the first second of the next. A token bucket allows
one legitimate burst up to capacity, then throttles smoothly at the
steady refill rate instead of resetting hard on a clock boundary. See
docs/decisions.md ADR-003 for the full trade-off writeup.
"""
import threading
import time

from fastapi import Request

from core.errors import AppError


class TokenBucket:
    """
    A single client's bucket for a single rate-limited route. Capacity
    tokens are available immediately (the allowed burst); tokens refill
    continuously at `refill_rate` tokens/second rather than resetting
    all-at-once, which is what makes this smoother than a fixed-window
    counter.
    """

    __slots__ = ("capacity", "refill_rate", "tokens", "last_refill", "lock")

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def consume(self, amount: float = 1.0) -> bool:
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False


class TokenBucketLimiter:
    """
    Owns one TokenBucket per (client, route) pair, created lazily on
    first request. Buckets are never explicitly evicted -- acceptable at
    hackathon/demo scale (bounded number of distinct clients hitting a
    handful of routes). A production version serving many thousands of
    unique clients would need TTL-based eviction to bound memory growth;
    tracked as a known follow-up, not a correctness issue at this scale.
    """

    def __init__(self):
        self._buckets: dict[tuple[str, str], TokenBucket] = {}
        self._buckets_lock = threading.Lock()

    def _get_bucket(self, key: tuple[str, str], capacity: float, refill_rate: float) -> TokenBucket:
        with self._buckets_lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = TokenBucket(capacity=capacity, refill_rate=refill_rate)
                self._buckets[key] = bucket
            return bucket

    def check(self, client_id: str, route_key: str, times: int, per_seconds: int) -> None:
        """Raises AppError.rate_limited() if this client has exhausted
        their token bucket for this route; otherwise consumes one token."""
        refill_rate = times / per_seconds
        bucket = self._get_bucket((client_id, route_key), capacity=times, refill_rate=refill_rate)
        if not bucket.consume():
            raise AppError.rate_limited(
                f"Rate limit exceeded: max {times} requests per {per_seconds}s. Please slow down."
            )

    def reset(self) -> None:
        """Test-only helper to clear all buckets between test cases."""
        with self._buckets_lock:
            self._buckets.clear()


_limiter = TokenBucketLimiter()


def rate_limit(times: int, per_seconds: int = 60):
    """
    FastAPI dependency factory. Usage on a route:

        @router.post("/chat")
        async def chat(request: Request, ..., _=Depends(rate_limit(20, 60))):
            ...

    Bucket capacity == `times` (the allowed burst), refill rate ==
    times/per_seconds tokens per second (the sustained steady-state rate).
    """

    def _dependency(request: Request) -> None:
        client_id = request.client.host if request.client else "unknown"
        route_key = request.url.path
        _limiter.check(client_id, route_key, times, per_seconds)

    return _dependency
