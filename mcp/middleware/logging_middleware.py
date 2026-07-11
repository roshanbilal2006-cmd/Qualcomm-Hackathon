"""
Logging middleware - assigns a request ID, times processing, and logs
timestamp, request ID, processing time, and status for every request.
"""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from mcp.utils.request_id import generate_request_id
from mcp.utils.timing import Timer

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = generate_request_id()
        request.state.request_id = request_id

        with Timer() as timer:
            try:
                response = await call_next(request)
            except Exception:
                logger.error(
                    "Unhandled exception during %s %s",
                    request.method,
                    request.url.path,
                    exc_info=True,
                    extra={"request_id": request_id},
                )
                raise

        logger.info(
            "%s %s -> %s (%sms)",
            request.method,
            request.url.path,
            response.status_code,
            timer.elapsed_ms,
            extra={"request_id": request_id},
        )
        response.headers["X-Request-ID"] = request_id
        return response