"""
FastAPI application entrypoint. Wires together all routers, middleware,
CORS, and rate limiting.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging

from core.config import get_settings
from core.rate_limiter import limiter
from api import routes_crowd, routes_wayfinding, routes_fan_assistant, routes_control_room, routes_voice, websocket_feed
logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.getLogger(__name__).info(f"{settings.APP_NAME} starting up...")
    yield
    logging.getLogger(__name__).info(f"{settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="GenAI-powered ecosystem for FIFA World Cup 2026 stadium operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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