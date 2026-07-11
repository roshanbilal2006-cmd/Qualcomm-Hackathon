"""
Routes for GET /status.
Thin HTTP layer only - delegates entirely to StatusService via app.state.
This endpoint is designed to always succeed (200), reporting degraded
states within the response body rather than via HTTP error codes.
"""

from fastapi import APIRouter, Request

from mcp.models.status_models import StatusResponse

router = APIRouter()


@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=200,
)
def get_status(request: Request):
    status_service = request.app.state.status_service
    return status_service.get_status()