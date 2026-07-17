"""
FastAPI application entrypoint. Wires together all routers, middleware,
CORS, and rate limiting.
"""
import logging
import subprocess
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from core.config import get_settings
from core.error_handlers import register_error_handlers
from core.security_headers import SecurityHeadersMiddleware
from features.control_room import routes as routes_control_room
from features.control_room import ws as websocket_feed
from features.crowd import routes as routes_crowd
from features.fan_assistant import routes as routes_fan_assistant
from features.voice import routes as routes_voice
from features.wayfinding import routes as routes_wayfinding

logging.basicConfig(level=logging.INFO)
settings = get_settings()
logger = logging.getLogger(__name__)

voice_worker_process: subprocess.Popen | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global voice_worker_process
    logger.info(f"{settings.APP_NAME} starting up...")

    # Spawn the LiveKit voice worker as a child process alongside the API.
    # Render's free plan has no separate background worker service type,
    # so this runs it as its own OS process inside the same web service
    # instance — LiveKit's signal handling and asyncio loop work exactly
    # as when run standalone with `python -m features.voice.worker start`.
    try:
        voice_worker_process = subprocess.Popen(
            [sys.executable, "-m", "features.voice.worker", "start"],
        )
        logger.info(f"Voice worker started (pid={voice_worker_process.pid})")
    except Exception:
        logger.exception("Failed to start voice worker subprocess")

    yield

    logger.info(f"{settings.APP_NAME} shutting down...")
    if voice_worker_process and voice_worker_process.poll() is None:
        voice_worker_process.terminate()
        try:
            voice_worker_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            voice_worker_process.kill()


app = FastAPI(
    title=settings.APP_NAME,
    description="GenAI-powered ecosystem for FIFA World Cup 2026 stadium operations",
    version="1.0.0",
    lifespan=lifespan,
)

register_error_handlers(app)

# Middleware order matters: Starlette applies these in reverse of
# add_middleware() order, so SecurityHeadersMiddleware (added last) wraps
# every response including CORS/GZip ones.
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(routes_crowd.router)
app.include_router(routes_wayfinding.router)
app.include_router(routes_fan_assistant.router)
app.include_router(routes_control_room.router)
app.include_router(routes_voice.router)
app.include_router(websocket_feed.router)


@app.get("/health")
async def health_check():
    """Required for Render's health checks — prevents cold-start kill issues."""
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running. See /docs for API reference."}