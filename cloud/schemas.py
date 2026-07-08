from pydantic import BaseModel, Field
from typing import List

class ObservationCreate(BaseModel):
    observation_id: str
    latitude: float
    longitude: float
    timestamp: str
    construction_stage: str
    progress: int = Field(ge=0, le=100)
    dust: float
    noise: float
    development_score: int
    summary: str
    embedding: List[float]

class HeatmapItem(BaseModel):
    latitude: float
    longitude: float
    score: int
    construction_stage: str
    dust: float
    noise: float

class StatsResponse(BaseModel):
    total_observations: int
    active_construction_sites: int
    average_development_score: int
    highest_noise_area: str
    last_updated: str
