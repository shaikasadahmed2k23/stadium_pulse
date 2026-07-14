"""
Wayfinding API routes (Feature 2 + 7).
"""
from fastapi import APIRouter, HTTPException, Request

from agents.wayfinding_agent import WayfindingAgent
from core.rate_limiter import limiter
from models.schemas import NavigationRequest, NavigationResponse

router = APIRouter(prefix="/api/wayfinding", tags=["Wayfinding"])
wayfinding_agent = WayfindingAgent()


@router.post("/navigate", response_model=NavigationResponse)
@limiter.limit("30/minute")
async def get_navigation_route(request: Request, nav_request: NavigationRequest):
    """Returns a congestion-aware route based on natural language query. Rate-limited."""
    try:
        return await wayfinding_agent.process(nav_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")