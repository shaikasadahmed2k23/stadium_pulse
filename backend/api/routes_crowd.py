"""
Crowd Intelligence API routes (Feature 1).
"""
import logging

from fastapi import APIRouter, HTTPException, Query

from agents.crowd_intelligence_agent import CrowdIntelligenceAgent
from models.schemas import CrowdPredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/crowd", tags=["Crowd Intelligence"])
crowd_agent = CrowdIntelligenceAgent()


@router.get("/status", response_model=CrowdPredictionResponse)
async def get_crowd_status(zone_ids: list[str] | None = Query(default=None)):
    """Returns current occupancy + predicted congestion for all or specific zones."""
    try:
        return await crowd_agent.process(zone_ids)
    except Exception as exc:
        logger.error("Crowd status fetch failed: %s", str(exc))
        raise HTTPException(status_code=500, detail="Failed to retrieve crowd status") from exc