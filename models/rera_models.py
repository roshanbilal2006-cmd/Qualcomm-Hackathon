"""
Pydantic models for RERA project data.
This is the single source-of-truth model for the RERA dataset.
Used directly as the response shape for /rera and /project/{id}.

Note: /nearby_projects uses a stripped-down projection of this model
(see models/project_models.py) that omits `id`, per the locked
LandSense API contract.
"""

from typing import Literal
from pydantic import BaseModel, Field


class RERAProject(BaseModel):
    id: str = Field(..., min_length=1, examples=["RERA-KA-00123"])
    name: str = Field(..., min_length=1, examples=["Prestige Tech Park"])
    builder: str = Field(..., min_length=1, examples=["Prestige"])
    status: Literal["Approved", "Pending", "Rejected", "Under Review"] = Field(
        ..., examples=["Approved"]
    )
    distance: float = Field(..., ge=0, examples=[0.9])