import math
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from cloud import models

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_observation(self, obs_data: dict) -> models.Observation:
        obs_id = obs_data.get("observation_id")
        db_obs = self.db.query(models.Observation).filter(models.Observation.observation_id == obs_id).first()
        
        if db_obs:
            for key, value in obs_data.items():
                setattr(db_obs, key, value)
        else:
            db_obs = models.Observation(**obs_data)
            self.db.add(db_obs)
            
        self.db.commit()
        self.db.refresh(db_obs)
        return db_obs

    def get_all_observations(self) -> List[models.Observation]:
        return self.db.query(models.Observation).all()

    def get_nearby_observations(self, lat: float, lng: float, radius_km: float = 5.0) -> List[models.Observation]:
        all_obs = self.get_all_observations()
        nearby = []
        for obs in all_obs:
            if haversine(lat, lng, obs.latitude, obs.longitude) <= radius_km:
                nearby.append(obs)
        return nearby

    def get_history(self, lat: Optional[float] = None, lng: Optional[float] = None, 
                    radius_km: Optional[float] = 5.0, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> List[models.Observation]:
        query = self.db.query(models.Observation)
        
        if start_date:
            query = query.filter(models.Observation.timestamp >= start_date)
        if end_date:
            query = query.filter(models.Observation.timestamp <= end_date)
            
        results = query.all()
        
        if lat is not None and lng is not None:
            filtered = [obs for obs in results if haversine(lat, lng, obs.latitude, obs.longitude) <= radius_km]
            return filtered
            
        return results

    def get_latest_sensor(self) -> Optional[models.Observation]:
        return (
            self.db.query(models.Observation)
            .filter(models.Observation.sensor_status == "connected")
            .filter(models.Observation.noise_db.isnot(None))
            .filter(models.Observation.dust_pm25.isnot(None))
            .filter(models.Observation.dust_pm10.isnot(None))
            .order_by(models.Observation.timestamp.desc())
            .first()
        )

    def get_stats(self) -> dict:
        total = self.db.query(models.Observation).count()
        if total == 0:
            return {
                "total_observations": 0,
                "active_construction_sites": 0,
                "average_development_score": 0,
                "highest_noise_area": "None",
                "last_updated": "N/A"
            }
            
        active = self.db.query(models.Observation).filter(models.Observation.progress < 100).count()
        avg_score = self.db.query(func.avg(models.Observation.development_score)).scalar() or 0
        
        highest_noise_obs = self.db.query(models.Observation).order_by(models.Observation.noise_db.desc()).first()
        highest_noise_area = f"Lat: {highest_noise_obs.latitude}, Lng: {highest_noise_obs.longitude}" if highest_noise_obs else "None"
        
        latest = self.db.query(models.Observation).order_by(models.Observation.timestamp.desc()).first()
        last_updated = latest.timestamp if latest else "N/A"
        
        return {
            "total_observations": total,
            "active_construction_sites": active,
            "average_development_score": int(avg_score),
            "highest_noise_area": highest_noise_area,
            "last_updated": last_updated
        }
