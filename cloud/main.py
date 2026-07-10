from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas
from .database import engine, get_db
from .services.retrieval_service import RetrievalService
from .services.prompt_builder import build_prompt
from .services.llm_service import LLMService

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LandSense AI Cloud", description="Community Intelligence Layer")

llm_service = LLMService()

def get_retrieval_service(db: Session = Depends(get_db)) -> RetrievalService:
    return RetrievalService(db)

@app.post("/observation", status_code=200)
def create_observation(obs: schemas.ObservationCreate, rs: RetrievalService = Depends(get_retrieval_service)):
    rs.create_or_update_observation(obs.dict())
    return {"status": "success", "message": "Observation stored successfully"}

@app.get("/heatmap", response_model=List[schemas.HeatmapItem])
def get_heatmap(rs: RetrievalService = Depends(get_retrieval_service)):
    observations = rs.get_all_observations()
    
    result = []
    for obs in observations:
        result.append(schemas.HeatmapItem(
            latitude=obs.latitude,
            longitude=obs.longitude,
            score=obs.development_score,
            construction_stage=obs.construction_stage,
            dust=obs.dust_pm25,
            noise=obs.noise_db
        ))
    return result

@app.get("/nearby")
def get_nearby(lat: float, lng: float, radius_km: float = 5.0, rs: RetrievalService = Depends(get_retrieval_service)):
    return rs.get_nearby_observations(lat, lng, radius_km)

@app.get("/history")
def get_history(
    lat: Optional[float] = None, 
    lng: Optional[float] = None, 
    radius_km: Optional[float] = 5.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    rs: RetrievalService = Depends(get_retrieval_service)
):
    return rs.get_history(lat, lng, radius_km, start_date, end_date)

@app.get("/latest_sensor")
def get_latest_sensor(rs: RetrievalService = Depends(get_retrieval_service)):
    latest = rs.get_latest_sensor()
    if not latest:
        raise HTTPException(status_code=404, detail="No sensor data available")
        
    return {
        "timestamp": latest.timestamp,
        "dust": latest.dust_pm25,
        "noise": latest.noise_db,
        "latitude": latest.latitude,
        "longitude": latest.longitude
    }

@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats(rs: RetrievalService = Depends(get_retrieval_service)):
    return schemas.StatsResponse(**rs.get_stats())

@app.post("/chat", response_model=schemas.ChatResponse)
def chat_assistant(req: schemas.ChatRequest, rs: RetrievalService = Depends(get_retrieval_service)):
    # 1. Retrieve Context
    nearby_obs = rs.get_nearby_observations(req.latitude, req.longitude)
    history_obs = rs.get_history(req.latitude, req.longitude)
    latest_obs = rs.get_latest_sensor()
    
    # Check if we have absolutely nothing
    if not nearby_obs and not history_obs and not latest_obs:
        return schemas.ChatResponse(answer="There is currently no community information available.")

    # 2. Build Prompt
    prompt = build_prompt(req.question, nearby_obs, history_obs, latest_obs)
    
    # 3. Call LLM
    try:
        answer = llm_service.generate_answer(prompt)
        return schemas.ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service Unavailable: " + str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cloud.main:app", host="0.0.0.0", port=8003, reload=True)
