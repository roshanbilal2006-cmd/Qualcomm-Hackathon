"""
Routes for GET /nearby_projects and GET /project/{id}.
Thin HTTP layer only - delegates entirely to ProjectService via app.state.
Converts RERAUnavailableError to 500 and a missing project to 404.
"""

from fastapi import APIRouter, Request, HTTPException

from mcp.models.rera_models import RERAProject
from mcp.models.project_models import NearbyProject
from mcp.utils.exceptions import RERAUnavailableError

router = APIRouter()


@router.get(
    "/nearby_projects",
    response_model=list[NearbyProject],
    status_code=200,
)
def get_nearby_projects(
    request: Request,
    latitude: float = 0.0,
    longitude: float = 0.0,
    radius_meters: float = 500.0
):
    project_service = request.app.state.project_service
    try:
        return project_service.get_nearby_projects(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters
        )
    except RERAUnavailableError as exc:
        raise HTTPException(status_code=500, detail="RERA data source unavailable") from exc


@router.get(
    "/project/{id}",
    response_model=RERAProject,
    status_code=200,
)
def get_project_by_id(id: str, request: Request):
    project_service = request.app.state.project_service
    try:
        project = project_service.get_project_by_id(id)
    except RERAUnavailableError as exc:
        raise HTTPException(status_code=500, detail="RERA data source unavailable") from exc

    if project is None:
        raise HTTPException(status_code=404, detail=f"Project with id '{id}' not found")

    return project