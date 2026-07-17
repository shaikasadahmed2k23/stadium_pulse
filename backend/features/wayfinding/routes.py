"""
Wayfinding API routes (Feature 2 + 7).
"""
from fastapi import APIRouter, Depends, Request

from core.rate_limiter import rate_limit
from features.wayfinding.schemas import NavigationRequest, NavigationResponse
from features.wayfinding.service import WayfindingAgent

router = APIRouter(prefix="/api/wayfinding", tags=["Wayfinding"])
wayfinding_agent = WayfindingAgent()


@router.post("/navigate", response_model=NavigationResponse)
async def get_navigation_route(
    request: Request,
    nav_request: NavigationRequest,
    _: None = Depends(rate_limit(times=30, per_seconds=60)),
):
    """
    Returns a congestion-aware route based on natural language query.
    Token-bucket rate-limited. No try/except needed -- routing is pure
    in-process logic with no external dependency, so any failure here is
    an actual bug and should hit the global unhandled-exception handler
    rather than being masked as a generic 500.
    """
    return await wayfinding_agent.process(nav_request)
