"""
Pydantic model for the /status endpoint.
"""

from typing import Literal
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    arduino: Literal["connected", "disconnected"] = Field(
        ..., examples=["connected"]
    )
    sensor_mode: Literal["demo", "live"] = Field(..., examples=["demo"])
    rera_mode: Literal["mock", "live"] = Field(..., examples=["mock"])
    mcp: Literal["healthy", "degraded"] = Field(..., examples=["healthy"])