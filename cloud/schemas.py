from pydantic import BaseModel, Field
from typing import List

class ObservationCreate(BaseModel):
    observation_id: str
    timestamp: str
    latitude: float
    longitude: float
    construction_stage: str
    confidence: float = 0.0
    progress: float = Field(ge=0.0, le=100.0)
    noise_db: float | None = None
    dust_pm25: float | None = None
    dust_pm10: float | None = None
    sensor_status: str = "degraded"
    development_score: float
    summary: str
    embedding: List[float]

class HeatmapItem(BaseModel):
    latitude: float
    longitude: float
    score: int
    construction_stage: str
    dust: float | None = None
    noise: float | None = None

class StatsResponse(BaseModel):
    total_observations: int
    active_construction_sites: int
    average_development_score: int
    highest_noise_area: str
    last_updated: str

class ChatRequest(BaseModel):
    question: str
    latitude: float
    longitude: float

class ChatResponse(BaseModel):
    answer: str
