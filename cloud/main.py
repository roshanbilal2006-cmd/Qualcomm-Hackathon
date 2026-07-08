import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

app = FastAPI(title="Qualcomm AI Cloud 100 Simulator", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.cloud")

# Global in-memory storage of synced observations
cloud_observations: List[Dict[str, Any]] = []

class SyncObservation(BaseModel):
    observation_id: str
    timestamp: str
    latitude: float
    longitude: float
    construction_stage: str
    confidence: float
    progress: float
    noise_db: float | None = None
    dust_pm25: float | None = None
    dust_pm10: float | None = None
    sensor_status: str
    development_score: float
    summary: str
    embedding: List[float]

@app.post("/observation")
async def upload_observation(observation: SyncObservation):
    logger.info(f"Cloud synced: Observation={observation.observation_id}, Score={observation.development_score}")
    
    # Check if observation already exists, if so update it
    for i, obs in enumerate(cloud_observations):
        if obs["observation_id"] == observation.observation_id:
            cloud_observations[i] = observation.dict()
            return {"sync_status": "success", "global_id": f"cloud_obs_{observation.observation_id}"}
            
    cloud_observations.append(observation.dict())
    return {"sync_status": "success", "global_id": f"cloud_obs_{observation.observation_id}"}

@app.get("/heatmap")
async def get_heatmap():
    """
    Returns summarized dataset for public heatmaps.
    """
    heatmap_points = []
    for obs in cloud_observations:
        heatmap_points.append({
            "observation_id": obs["observation_id"],
            "latitude": obs["latitude"],
            "longitude": obs["longitude"],
            "development_score": obs["development_score"],
            "noise_db": obs["noise_db"],
            "dust_pm25": obs["dust_pm25"],
            "stage": obs["construction_stage"]
        })
    return heatmap_points

@app.get("/history")
async def get_history():
    """
    Returns global history feed.
    """
    return cloud_observations

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
