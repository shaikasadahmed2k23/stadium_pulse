"""
Baseline security response headers.

FastAPI/Starlette don't set these by default. They're cheap to add and
meaningfully reduce attack surface (clickjacking, MIME-sniffing, XSS via
inline injection) on both the public Fan App endpoints and the staff-only
Control Room dashboard.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        # NOTE: 'unsafe-inline' on style-src is a deliberate, documented
        # trade-off — the Next.js/Tailwind frontend injects styles at
        # runtime. Tighten to a nonce-based CSP before shipping this past
        # a hackathon demo (tracked in docs/decisions.md).
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "connect-src 'self' https://*.supabase.co wss://*.livekit.cloud; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )

        return response
