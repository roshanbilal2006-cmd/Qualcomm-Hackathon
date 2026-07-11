"""
Pydantic model for the /nearby_projects endpoint.

This is intentionally a narrower projection of RERAProject
(models/rera_models.py), per the locked LandSense API contract:
only name, builder, status, and distance are exposed here.
The internal `id` field exists in RERAProject for /project/{id}
lookups but must not appear in this response.
"""

from typing import Literal
from pydantic import BaseModel, Field


class NearbyProject(BaseModel):
    name: str = Field(..., min_length=1, examples=["Prestige Tech Park"])
    builder: str = Field(..., min_length=1, examples=["Prestige"])
    status: Literal["Approved", "Pending", "Rejected", "Under Review"] = Field(
        ..., examples=["Approved"]
    )
    distance: float = Field(..., ge=0, examples=[0.9])