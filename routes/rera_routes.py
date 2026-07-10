"""
Routes for GET /rera.
Thin HTTP layer only - delegates entirely to RERAService via app.state.
Returns a plain JSON array per the locked contract (no wrapper object).
"""

from fastapi import APIRouter, Request, HTTPException

from models.rera_models import RERAProject
from utils.exceptions import RERAUnavailableError

router = APIRouter()


@router.get(
    "/rera",
    response_model=list[RERAProject],
    status_code=200,
)
def get_rera_dataset(request: Request):
    rera_service = request.app.state.rera_service
    try:
        return rera_service.get_all_projects()
    except RERAUnavailableError as exc:
        raise HTTPException(status_code=500, detail="RERA data source unavailable") from exc