import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models.domain import ObservationInput, ObservationResponse
from backend.models.db import DBObservation, DBReraProject
from backend.adapters.ai_adapter import AIAdapter
from backend.adapters.iot_adapter import IoTAdapter
from backend.adapters.cloud_adapter import CloudAdapter
from backend.adapters.mcp_adapter import MCPAdapter
from backend.fusion.correlation import correlate_sensor_data, haversine_distance
from backend.fusion.scoring import calculate_development_score

logger = logging.getLogger("landsense.pipeline")

class ObservationPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.ai_adapter = AIAdapter()
        self.iot_adapter = IoTAdapter()
        self.cloud_adapter = CloudAdapter()
        self.mcp_adapter = MCPAdapter()

    async def execute(self, input_data: ObservationInput) -> ObservationResponse:
        """
        Executes the entire construction intelligence observation pipeline.
        """
        # Step 1: Initialize ID and timestamp
        obs_id = str(uuid.uuid4())
        logger.info(f"Pipeline started for observation {obs_id} at Lat: {input_data.latitude}, Lng: {input_data.longitude}")

        # Step 2: Validate Images
        if not input_data.images:
            logger.warning("No images provided in observation request.")

        # Step 3: Trigger local AI Prediction (FastVLM simulation)
        ai_result = await self.ai_adapter.predict(input_data.images)
        logger.info(f"AI Prediction received: Stage={ai_result.get('stage')}, Progress={ai_result.get('progress')}%")

        # Step 4: Request Arduino IoT Sensor telemetry
        sensor_data = await self.iot_adapter.get_sensor_data()
        
        # Step 5: Correlation Engine Checks
        # The sensor node reports its coordinates (either hardcoded or dynamic)
        sensor_lat = sensor_data.get("latitude", 12.9716)
        sensor_lon = sensor_data.get("longitude", 77.7500)
        
        is_correlated = correlate_sensor_data(
            phone_lat=input_data.latitude,
            phone_lon=input_data.longitude,
            phone_timestamp_str=input_data.timestamp,
            sensor_data=sensor_data,
            sensor_lat=sensor_lat,
            sensor_lon=sensor_lon
        )

        noise_db = 0.0
        pm25 = 0.0
        pm10 = 0.0
        sensor_status = "degraded"

        if is_correlated:
            noise_db = sensor_data.get("noise_db", 0.0)
            pm25 = sensor_data.get("pm25", 0.0)
            pm10 = sensor_data.get("pm10", 0.0)
            sensor_status = "connected"
            logger.info("IoT sensor data correlated successfully.")
        else:
            logger.warning("IoT sensor telemetry ignored (fails time or distance correlation window).")

        # Step 6: SQLite RERA Lookup (radius search up to 500m)
        rera_projects = []
        db_projects = self.db.query(DBReraProject).all()
        for p in db_projects:
            dist = haversine_distance(input_data.latitude, input_data.longitude, p.latitude, p.longitude)
            if dist <= 500.0:
                rera_projects.append({
                    "name": p.name,
                    "builder": p.builder,
                    "status": p.status,
                    "distance": round(dist, 1)
                })
        
        # Sort by distance
        rera_projects.sort(key=lambda x: x["distance"])
        logger.info(f"SQLite RERA lookup found {len(rera_projects)} projects within 500m.")

        # Step 7: Perform Data Fusion & Scoring
        fusion_result = calculate_development_score(
            visual_stage=ai_result.get("stage", "Unknown"),
            progress=ai_result.get("progress", 0.0),
            visual_confidence=ai_result.get("confidence", 0.0),
            sensor_status=sensor_status,
            noise_db=noise_db,
            dust_pm25=pm25,
            dust_pm10=pm10,
            rera_projects=rera_projects
        )

        # Step 8: Build the Universal Data Object
        fused_observation = {
            "observation_id": obs_id,
            "timestamp": input_data.timestamp,
            "latitude": input_data.latitude,
            "longitude": input_data.longitude,
            "images": input_data.images,
            "voice_query": input_data.voice_query,
            "construction_stage": ai_result.get("stage"),
            "confidence": ai_result.get("confidence"),
            "progress": ai_result.get("progress"),
            "noise_db": noise_db if sensor_status == "connected" else None,
            "dust_pm25": pm25 if sensor_status == "connected" else None,
            "dust_pm10": pm10 if sensor_status == "connected" else None,
            "sensor_status": sensor_status,
            "rera_projects": rera_projects,
            "development_score": fusion_result.get("development_score", 0.0),
            "summary": fusion_result.get("summary", ""),
            "embedding": ai_result.get("embedding", [])
        }

        # Step 9: Save observation to local SQLite DB history
        db_obs = DBObservation(
            observation_id=obs_id,
            timestamp=fused_observation["timestamp"],
            latitude=fused_observation["latitude"],
            longitude=fused_observation["longitude"],
            voice_query=fused_observation["voice_query"],
            construction_stage=fused_observation["construction_stage"],
            confidence=fused_observation["confidence"],
            progress=fused_observation["progress"],
            noise_db=fused_observation["noise_db"],
            dust_pm25=fused_observation["dust_pm25"],
            dust_pm10=fused_observation["dust_pm10"],
            sensor_status=fused_observation["sensor_status"],
            development_score=fused_observation["development_score"],
            summary=fused_observation["summary"]
        )
        db_obs.images = fused_observation["images"]
        db_obs.rera_projects = fused_observation["rera_projects"]
        db_obs.embedding = fused_observation["embedding"]

        self.db.add(db_obs)
        self.db.commit()
        logger.info("Observation details saved to local SQLite DB.")

        # Step 10: Sync to Qualcomm AI Cloud (excluding raw files)
        await self.cloud_adapter.upload_observation(fused_observation)

        return ObservationResponse(**fused_observation)
