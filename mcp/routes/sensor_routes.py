"""
Routes for GET /sensor.
Thin HTTP layer only - delegates entirely to SensorService via app.state.
"""

from typing import Union

from fastapi import APIRouter, Request

from mcp.models.sensor_models import SensorReading, SensorOfflineResponse

router = APIRouter()


@router.get(
    "/sensor",
    response_model=Union[SensorReading, SensorOfflineResponse],
    status_code=200,
)
def get_sensor_reading(request: Request):
    sensor_service = request.app.state.sensor_service
    return sensor_service.get_current_reading()