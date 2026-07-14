"""
Global exception handlers for the FastAPI app.

Kept out of main.py (rather than inlined with @app.exception_handler
decorators there) so main.py stays a thin wiring file instead of growing
into a dumping ground as more error types get added later.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        # AppErrors are expected failure modes (bad input, upstream down,
        # unauthorized) — log at WARNING, not ERROR, and don't include a
        # stack trace since these aren't bugs.
        logger.warning(
            "AppError [%s] on %s: %s", exc.code.value, request.url.path, exc.message
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code.value, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        # Anything that reaches here was NOT raised as an AppError, which
        # means it's an unanticipated bug, not a known failure mode. Log
        # the full traceback for debugging, but never leak internals
        # (exception type, stack trace, file paths) back to the client.
        logger.error(
            "Unhandled exception on %s: %s", request.url.path, str(exc), exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "Something went wrong. Please try again.",
            },
        )
