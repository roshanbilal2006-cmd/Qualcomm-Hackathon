from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database.session import get_db
from backend.models.domain import ObservationInput, ObservationResponse, ReraProjectSchema
from backend.models.db import DBObservation, DBReraProject
from backend.pipeline.orchestrator import ObservationPipeline
from backend.fusion.correlation import haversine_distance

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": "Snapdragon X Elite Laptop",
        "role": "Orchestration Brain"
    }

@router.post("/observation", response_model=ObservationResponse)
async def create_observation(
    payload: ObservationInput,
    db: Session = Depends(get_db)
):
    """
    Ingests construction scans from Android devices and processes them through
    the sensor fusion pipeline.
    """
    pipeline = ObservationPipeline(db)
    try:
        response = await pipeline.execute(payload)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )

@router.get("/history", response_model=List[ObservationResponse])
async def get_history(db: Session = Depends(get_db)):
    """
    Retrieves the history of all local construction observations.
    """
    db_obs = db.query(DBObservation).order_by(DBObservation.timestamp.desc()).all()
    observations = []
    for o in db_obs:
        observations.append(
            ObservationResponse(
                observation_id=o.observation_id,
                timestamp=o.timestamp,
                latitude=o.latitude,
                longitude=o.longitude,
                images=o.images,
                voice_query=o.voice_query,
                construction_stage=o.construction_stage,
                confidence=o.confidence,
                progress=o.progress,
                noise_db=o.noise_db,
                dust_pm25=o.dust_pm25,
                dust_pm10=o.dust_pm10,
                sensor_status=o.sensor_status,
                rera_projects=[ReraProjectSchema(**p) for p in o.rera_projects],
                development_score=o.development_score,
                summary=o.summary,
                embedding=o.embedding
            )
        )
    return observations

@router.get("/observation/{observation_id}", response_model=ObservationResponse)
async def get_observation_by_id(
    observation_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves details for a specific observation by ID.
    """
    o = db.query(DBObservation).filter(DBObservation.observation_id == observation_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    return ObservationResponse(
        observation_id=o.observation_id,
        timestamp=o.timestamp,
        latitude=o.latitude,
        longitude=o.longitude,
        images=o.images,
        voice_query=o.voice_query,
        construction_stage=o.construction_stage,
        confidence=o.confidence,
        progress=o.progress,
        noise_db=o.noise_db,
        dust_pm25=o.dust_pm25,
        dust_pm10=o.dust_pm10,
        sensor_status=o.sensor_status,
        rera_projects=[ReraProjectSchema(**p) for p in o.rera_projects],
        development_score=o.development_score,
        summary=o.summary,
        embedding=o.embedding
    )

@router.get("/nearby", response_model=List[ReraProjectSchema])
async def get_nearby_projects(
    latitude: float,
    longitude: float,
    radius: float = 500.0,
    db: Session = Depends(get_db)
):
    """
    Queries local database for nearby RERA construction projects.
    """
    db_projects = db.query(DBReraProject).all()
    nearby = []
    for p in db_projects:
        dist = haversine_distance(latitude, longitude, p.latitude, p.longitude)
        if dist <= radius:
            nearby.append(
                ReraProjectSchema(
                    name=p.name,
                    builder=p.builder,
                    status=p.status,
                    distance=round(dist, 1)
                )
            )
    
    nearby.sort(key=lambda x: x.distance)
    return nearby

@router.get("/heatmap")
async def get_heatmap_points(db: Session = Depends(get_db)):
    """
    Retrieves coordinate points and key metrics to generate the heatmaps.
    """
    db_obs = db.query(DBObservation).all()
    points = []
    for o in db_obs:
        points.append({
            "observation_id": o.observation_id,
            "latitude": o.latitude,
            "longitude": o.longitude,
            "development_score": o.development_score,
            "noise_db": o.noise_db,
            "dust_pm25": o.dust_pm25,
            "stage": o.construction_stage
        })
    return points
