"""
Crowd Intelligence API routes (Feature 1).
"""
from fastapi import APIRouter, Query

from features.crowd.schemas import CrowdPredictionResponse
from features.crowd.service import CrowdIntelligenceAgent

router = APIRouter(prefix="/api/crowd", tags=["Crowd Intelligence"])
crowd_agent = CrowdIntelligenceAgent()


@router.get("/status", response_model=CrowdPredictionResponse)
async def get_crowd_status(zone_ids: list[str] | None = Query(default=None)):
    """
    Returns current occupancy + predicted congestion for all or specific
    zones. Unexpected failures fall through to the global exception handler
    in core/error_handlers.py -- no try/except needed here since this
    endpoint has no downstream failure mode worth distinguishing from a
    generic internal error.
    """
    return await crowd_agent.process(zone_ids)
