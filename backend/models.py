from pydantic import BaseModel
from typing import List, Optional

# --- Request Models ---

class ObservationRequest(BaseModel):
    images: List[str]
    latitude: str
    longitude: str
    timestamp: str
    voice_query: Optional[str] = None
    device: str = "OnePlus15"


# --- Response Models ---

class ObservationResponse(BaseModel):
    construction_stage: str
    progress_percent: int
    confidence: float
    dust_level: str
    noise_level: str
    development_score: int
    nearby_projects: int
    summary: str

class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    activity_level: str  # "High", "Medium", "Low"

class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]
