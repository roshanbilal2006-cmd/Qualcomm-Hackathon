"""
Typed exception hierarchy and global exception handling.

Adapters raise these typed exceptions instead of letting low-level
errors (serial.SerialException, json.JSONDecodeError, httpx errors,
etc.) escape uncaught. Services catch these and convert them into
the safe response shapes defined in the API contract. Anything that
still escapes is caught by the global handler registered here,
logged with full detail server-side, and returned to the client as
a generic error with no stack trace.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class LandSenseIoTError(Exception):
    """Base class for all typed errors raised within this module."""


class DeviceOfflineError(LandSenseIoTError):
    """Raised by a SensorProvider when a reading cannot be obtained."""


class RERAUnavailableError(LandSenseIoTError):
    """Raised by a RERAProvider when the underlying data source
    cannot be reached or read, as distinct from a simple 'not found'
    for a specific project id."""


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers a catch-all exception handler on the given FastAPI app.
    Ensures no unhandled exception ever returns a raw stack trace to
    the client - logs full detail server-side, returns a generic
    500 response instead.

    Note: DeviceOfflineError and RERAUnavailableError are expected to
    be caught within services (sensor_service, rera_service,
    project_service) and converted into contract-defined response
    shapes (e.g. {"status": "offline"}) or explicit HTTPExceptions
    (e.g. 404, 500) at the route level. This handler is the last
    line of defense for anything that escapes that layer.
    """

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )