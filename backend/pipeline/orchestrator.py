import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.models.domain import ObservationInput, ObservationResponse
from backend.models.db import DBObservation
from backend.adapters.ai_adapter import AIAdapter
from backend.adapters.cloud_adapter import CloudAdapter
from backend.adapters.mcp_adapter import MCPAdapter
from backend.fusion.correlation import correlate_sensor_data, haversine_distance
from backend.fusion.scoring import calculate_development_score

logger = logging.getLogger("landsense.pipeline")

class ObservationPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.ai_adapter = AIAdapter()
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

        # Step 3: Trigger OpenRouter + OpenCV visual prediction
        ai_result = await self.ai_adapter.predict(input_data.images)
        logger.info(f"AI Prediction received: Stage={ai_result.get('stage')}, Progress={ai_result.get('progress')}%")

        # Step 4: Obtain environment telemetry from MCP Service (formerly IoT)
        sensor_data = {}
        if input_data.noise_db is not None or input_data.dust_pm25 is not None or input_data.dust_pm10 is not None:
            sensor_data = {
                "timestamp": input_data.sensor_timestamp or input_data.timestamp,
                "device_id": "WEB_UPLOAD_SENSOR",
                "latitude": input_data.latitude,
                "longitude": input_data.longitude
            }
            if input_data.noise_db is not None:
                sensor_data["noise_db"] = input_data.noise_db
            if input_data.dust_pm25 is not None:
                sensor_data["pm25"] = input_data.dust_pm25
            if input_data.dust_pm10 is not None:
                sensor_data["pm10"] = input_data.dust_pm10
        else:
            sensor_data = await self.mcp_adapter.get_sensor_data(latitude=input_data.latitude, longitude=input_data.longitude)
        
        # Step 5: Correlation Engine Checks
        # Missing sensor coordinates must stay missing and cannot be replaced
        # with any hardcoded real-world location.
        sensor_lat = sensor_data.get("latitude")
        sensor_lon = sensor_data.get("longitude")

        is_correlated = correlate_sensor_data(
            phone_lat=input_data.latitude,
            phone_lon=input_data.longitude,
            phone_timestamp_str=input_data.timestamp,
            sensor_data=sensor_data,
            sensor_lat=sensor_lat,
            sensor_lon=sensor_lon,
        )

        noise_db = None
        pm25 = None
        pm10 = None
        sensor_status = "degraded"
        sensor_source = sensor_data.get("sensor_source") or sensor_data.get("data_origin") or "unknown"
        rera_source = "unknown"

        if is_correlated:
            noise_db = sensor_data.get("noise_db")
            pm25 = sensor_data.get("pm25")
            pm10 = sensor_data.get("pm10")
            if sensor_source == "dummy" or sensor_data.get("data_origin") == "simulated":
                sensor_status = "simulated"
            elif any(value is not None for value in (noise_db, pm25, pm10)):
                sensor_status = "connected"
            else:
                sensor_status = "degraded"

            if sensor_status == "connected":
                logger.info("IoT sensor data correlated successfully via MCP.")
            elif sensor_status == "simulated":
                logger.warning("A simulated dummy sensor payload was correlated; it remains identifiable as simulated and is not physical hardware evidence.")
            else:
                logger.info("No dust/noise telemetry supplied with observation.")
        else:
            logger.warning("IoT sensor telemetry ignored (fails time or distance correlation window).")

        # Step 6: MCP RERA Lookup (radius search up to 500m)
        rera_projects = await self.mcp_adapter.get_nearby_projects(
            latitude=input_data.latitude,
            longitude=input_data.longitude,
            radius_meters=500.0,
        )
        logger.info(f"MCP RERA lookup found {len(rera_projects)} projects within 500m.")
        if rera_projects:
            rera_source = "mock" if rera_projects and all(project.get("source") == "mock" for project in rera_projects) else "unknown"

        # Crowdsourcing fallback: preserve the fallback semantics but label it
        # explicitly as crowdsourced/external rather than a physical sensor.
        if sensor_status != "connected" and rera_projects:
            for project in rera_projects:
                if project.get("noise_db") or project.get("dust_pm25") or project.get("dust_pm10"):
                    noise_db = project.get("noise_db")
                    pm25 = project.get("dust_pm25")
                    pm10 = project.get("dust_pm10")
                    sensor_status = "crowdsourced"
                    sensor_source = "crowdsourced"
                    logger.info(f"Using crowdsourced/external environmental fallback from nearby project: {project.get('name')}")
                    break

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
        ai_description = ai_result.get("description", "").strip()
        fusion_summary = fusion_result.get("summary", "")
        summary = f"{ai_description} {fusion_summary}".strip() if ai_description else fusion_summary

        # Step 8: Build the Universal Data Object
        fused_observation = {
            "observation_id": obs_id,
            "timestamp": input_data.timestamp,
            "owner_id": input_data.owner_id,
            "latitude": input_data.latitude,
            "longitude": input_data.longitude,
            "images": [],
            "voice_query": input_data.voice_query,
            "construction_stage": ai_result.get("stage"),
            "confidence": ai_result.get("confidence"),
            "progress": ai_result.get("progress"),
            "noise_db": noise_db if sensor_status == "connected" else None,
            "dust_pm25": pm25 if sensor_status == "connected" else None,
            "dust_pm10": pm10 if sensor_status == "connected" else None,
            "sensor_status": sensor_status,
            "sensor_source": sensor_source,
            "data_origin": sensor_source,
            "rera_source": rera_source,
            "rera_projects": rera_projects,
            "development_score": fusion_result.get("development_score", 0.0),
            "summary": summary,
            "embedding": ai_result.get("embedding", []),
            "opencv_analysis": ai_result.get("opencv_analysis", {})
        }

        # Step 9: Save observation to local SQLite DB history
        db_obs = DBObservation(
            observation_id=obs_id,
            owner_id=fused_observation["owner_id"],
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
        db_obs.opencv_analysis = fused_observation["opencv_analysis"]

        self.db.add(db_obs)
        self.db.commit()
        logger.info("Observation details saved to local SQLite DB.")

        # Step 10: Sync to Qualcomm AI Cloud (excluding raw files)
        cloud_observation = fused_observation.copy()
        cloud_observation.pop("owner_id", None)
        await self.cloud_adapter.upload_observation(cloud_observation)

        response_payload = fused_observation.copy()
        response_payload.pop("owner_id", None)
        return ObservationResponse(**response_payload)
