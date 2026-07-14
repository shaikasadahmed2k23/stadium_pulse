"""
Wayfinding API routes (Feature 2 + 7).
"""
from fastapi import APIRouter, Request

from core.rate_limiter import limiter
from features.wayfinding.schemas import NavigationRequest, NavigationResponse
from features.wayfinding.service import WayfindingAgent

router = APIRouter(prefix="/api/wayfinding", tags=["Wayfinding"])
wayfinding_agent = WayfindingAgent()


@router.post("/navigate", response_model=NavigationResponse)
@limiter.limit("30/minute")
async def get_navigation_route(request: Request, nav_request: NavigationRequest):
    """
    Returns a congestion-aware route based on natural language query.
    Rate-limited. No try/except needed -- routing is pure in-process logic
    with no external dependency, so any failure here is an actual bug and
    should hit the global unhandled-exception handler rather than being
    masked as a generic 500.
    """
    return await wayfinding_agent.process(nav_request)
