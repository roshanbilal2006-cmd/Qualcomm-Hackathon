"""
Pydantic models for the /sensor endpoint.
"""

from typing import Literal
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    device_id: str = Field(..., min_length=1, examples=["UNO-Q"])
    timestamp: str = Field(..., examples=["2026-07-08T10:15:32Z"])
    noise_db: float = Field(..., ge=40, le=90, examples=[72.4])
    pm25: float = Field(..., ge=10, le=100, examples=[38.1])
    pm10: float = Field(..., ge=20, le=150, examples=[61.7])


class SensorOfflineResponse(BaseModel):
    status: Literal["offline"] = "offline"