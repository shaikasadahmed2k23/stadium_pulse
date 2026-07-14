"""
Real-time WebSocket feed (supports Feature 1, 4, 8).
Pushes live control room state to connected dashboard clients every
few seconds, so the frontend doesn't need to poll — genuinely
demonstrates "real-time decision support" from the brief.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from agents.decision_orchestrator import DecisionOrchestrator
from agents.anomaly_detector import AnomalyDetector
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

orchestrator = DecisionOrchestrator()
anomaly_detector = AnomalyDetector()


@router.websocket("/ws/control-room")
async def control_room_feed(websocket: WebSocket):
    await websocket.accept()
    logger.info("Control room WebSocket client connected")
    try:
        while True:
            # Run anomaly detection each cycle so incidents surface automatically
            await anomaly_detector.process()
            state = await orchestrator.process()
            await websocket.send_json(state.model_dump(mode="json"))
            await asyncio.sleep(5)  # push every 5 seconds
    except WebSocketDisconnect:
        logger.info("Control room WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()