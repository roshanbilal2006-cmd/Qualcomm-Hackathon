from pydantic import BaseModel, Field
from typing import Any, List, Optional

class ReraProjectSchema(BaseModel):
    name: str
    builder: str
    status: str
    distance: float

class ObservationInput(BaseModel):
    timestamp: str
    owner_id: Optional[str] = None
    latitude: float
    longitude: float
    images: List[str] = Field(default_factory=list, min_length=1, max_length=4)
    voice_query: Optional[str] = None
    noise_db: Optional[float] = None
    dust_pm25: Optional[float] = None
    dust_pm10: Optional[float] = None
    sensor_timestamp: Optional[str] = None

class ObservationResponse(BaseModel):
    observation_id: str
    timestamp: str
    latitude: float
    longitude: float
    images: List[str] = Field(default_factory=list)
    voice_query: Optional[str] = None
    construction_stage: Optional[str] = None
    confidence: Optional[float] = None
    progress: Optional[float] = None
    noise_db: Optional[float] = None
    dust_pm25: Optional[float] = None
    dust_pm10: Optional[float] = None
    sensor_status: str = "degraded"
    rera_projects: List[ReraProjectSchema] = Field(default_factory=list)
    development_score: float = 0.0
    summary: str = ""
    embedding: List[float] = Field(default_factory=list)
    opencv_analysis: dict[str, Any] = Field(default_factory=dict)
