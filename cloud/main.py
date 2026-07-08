from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import math
from datetime import datetime

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LandSense AI Cloud", description="Community Intelligence Layer")

@app.post("/observation", status_code=200)
def create_observation(obs: schemas.ObservationCreate, db: Session = Depends(get_db)):
    db_obs = db.query(models.Observation).filter(models.Observation.observation_id == obs.observation_id).first()
    
    if db_obs:
        # Update existing
        for key, value in obs.dict().items():
            setattr(db_obs, key, value)
    else:
        # Create new
        db_obs = models.Observation(**obs.dict())
        db.add(db_obs)
        
    db.commit()
    db.refresh(db_obs)
    return {"status": "success", "message": "Observation stored successfully"}

@app.get("/heatmap", response_model=List[schemas.HeatmapItem])
def get_heatmap(db: Session = Depends(get_db)):
    # Returns all observations for heatmap
    observations = db.query(models.Observation).all()
    
    result = []
    for obs in observations:
        result.append(schemas.HeatmapItem(
            latitude=obs.latitude,
            longitude=obs.longitude,
            score=obs.development_score,
            construction_stage=obs.construction_stage,
            dust=obs.dust,
            noise=obs.noise
        ))
    return result

def haversine(lat1, lon1, lat2, lon2):
    # Simple haversine formula for distance in km
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.get("/nearby")
def get_nearby(lat: float, lng: float, radius_km: float = 5.0, db: Session = Depends(get_db)):
    # In a real DB with PostGIS we'd use spatial queries. For SQLite, we fetch all and filter or do a rough bounding box.
    # For hackathon simplicity, fetch all and filter in Python.
    all_obs = db.query(models.Observation).all()
    nearby = []
    for obs in all_obs:
        if haversine(lat, lng, obs.latitude, obs.longitude) <= radius_km:
            nearby.append(obs)
    return nearby

@app.get("/history")
def get_history(
    lat: Optional[float] = None, 
    lng: Optional[float] = None, 
    radius_km: Optional[float] = 5.0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Observation)
    
    if start_date:
        query = query.filter(models.Observation.timestamp >= start_date)
    if end_date:
        query = query.filter(models.Observation.timestamp <= end_date)
        
    results = query.all()
    
    if lat is not None and lng is not None:
        filtered = [obs for obs in results if haversine(lat, lng, obs.latitude, obs.longitude) <= radius_km]
        return filtered
        
    return results

@app.get("/latest_sensor")
def get_latest_sensor(db: Session = Depends(get_db)):
    latest = db.query(models.Observation).order_by(models.Observation.timestamp.desc()).first()
    if not latest:
        raise HTTPException(status_code=404, detail="No sensor data available")
        
    return {
        "timestamp": latest.timestamp,
        "dust": latest.dust,
        "noise": latest.noise,
        "latitude": latest.latitude,
        "longitude": latest.longitude
    }

@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Observation).count()
    if total == 0:
        return schemas.StatsResponse(
            total_observations=0,
            active_construction_sites=0,
            average_development_score=0,
            highest_noise_area="None",
            last_updated="N/A"
        )
        
    # Active sites - assume progress < 100 means active
    active = db.query(models.Observation).filter(models.Observation.progress < 100).count()
    
    # Average score
    avg_score = db.query(func.avg(models.Observation.development_score)).scalar() or 0
    
    # Highest noise area (just returning coordinates since we don't do reverse geocoding here)
    highest_noise_obs = db.query(models.Observation).order_by(models.Observation.noise.desc()).first()
    highest_noise_area = f"Lat: {highest_noise_obs.latitude}, Lng: {highest_noise_obs.longitude}"
    
    # Last updated
    latest = db.query(models.Observation).order_by(models.Observation.timestamp.desc()).first()
    last_updated = latest.timestamp if latest else "N/A"
    
    return schemas.StatsResponse(
        total_observations=total,
        active_construction_sites=active,
        average_development_score=int(avg_score),
        highest_noise_area=highest_noise_area,
        last_updated=last_updated
    )
