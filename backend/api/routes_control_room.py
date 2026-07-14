"""
Control Room API routes (Feature 4 + 6 + 8).
Staff-facing endpoints — aggregated state, reasoning trace, and
incident reporting.
"""
from fastapi import APIRouter, Depends
from agents.decision_orchestrator import DecisionOrchestrator
from agents.anomaly_detector import AnomalyDetector
from core.errors import AppError
from models.schemas import ControlRoomState, IncidentAlert, IncidentType
from services.reasoning_logger import ReasoningLogger
from core.security import verify_staff_api_key
from pydantic import BaseModel

router = APIRouter(prefix="/api/control-room", tags=["Control Room"])
orchestrator = DecisionOrchestrator()
anomaly_detector = AnomalyDetector()


class ManualIncidentRequest(BaseModel):
    zone_id: str
    incident_type: IncidentType
    description: str
    severity: str = "medium"


@router.get("/state", response_model=ControlRoomState)
async def get_control_room_state(_: str = Depends(verify_staff_api_key)):
    """Aggregated view: zones, active recommendations, active incidents."""
    return await orchestrator.process()


@router.get("/reasoning-trace")
async def get_reasoning_trace(limit: int = 20, _: str = Depends(verify_staff_api_key)):
    """Feature 6 — recent reasoning entries across all agents, for dashboard transparency panel."""
    return {"entries": ReasoningLogger.get_recent(limit)}


@router.post("/scan-anomalies", response_model=list[IncidentAlert])
async def scan_for_anomalies(_: str = Depends(verify_staff_api_key)):
    """Feature 8 — triggers a proactive anomaly detection scan."""
    try:
        return await anomaly_detector.process()
    except Exception as e:
        raise AppError.upstream_error("Anomaly detector", str(e)) from e


@router.post("/incidents/report", response_model=IncidentAlert)
async def report_incident_manually(request: ManualIncidentRequest, _: str = Depends(verify_staff_api_key)):
    """Allows staff to manually raise an incident (e.g. lost child, medical)."""
    return anomaly_detector.manually_report_incident(
        zone_id=request.zone_id,
        incident_type=request.incident_type,
        description=request.description,
        severity=request.severity,
    )




