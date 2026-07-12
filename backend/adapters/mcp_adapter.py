import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger("landsense.mcp_adapter")

class MCPAdapter:
    def __init__(
        self,
        service_url: str = "http://localhost:8004",
        cloud_service_url: str = "http://localhost:8003",
    ):
        self.service_url = service_url
        self.cloud_service_url = cloud_service_url

    async def get_nearby_projects(self, latitude: float, longitude: float, radius_meters: float = 500.0) -> list:
        """
        Retrieves nearby RERA projects and status via the MCP adapter.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(
                    f"{self.service_url}/nearby_projects",
                    params={"latitude": latitude, "longitude": longitude, "radius_meters": radius_meters}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"MCP Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Service at {self.service_url}: {str(e)}")

        return []

    async def get_sensor_data(self, latitude: float | None = None, longitude: float | None = None) -> dict:
        """
        Retrieves environmental telemetry from the MCP sensor interface.
        Returns:
            {
                "noise_db": float,
                "pm25": float,
                "pm10": float,
                "timestamp": str,
                "device_id": str
            }
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                params = {}
                if latitude is not None and longitude is not None:
                    params = {"lat": latitude, "lon": longitude}
                response = await client.get(f"{self.service_url}/sensor", params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"MCP Sensor Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Sensor Service at {self.service_url}: {str(e)}")

        cloud_sensor_data = await self._get_latest_cloud_sensor()
        if cloud_sensor_data:
            logger.warning("Using latest cloud sensor data because MCP service is unavailable.")
            return cloud_sensor_data

        logger.warning("No MCP or cloud sensor data available.")
        return {}

    async def _get_latest_cloud_sensor(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.cloud_service_url}/latest_sensor")
                if response.status_code != 200:
                    logger.warning(
                        "Cloud latest sensor returned status code %s: %s",
                        response.status_code,
                        response.text,
                    )
                    return {}

                data = response.json()
                noise_db = data.get("noise_db", data.get("noise"))
                pm25 = data.get("dust_pm25", data.get("dust"))
                pm10 = data.get("dust_pm10")
                if noise_db is None or pm25 is None or pm10 is None:
                    logger.warning("Cloud latest sensor payload is missing one or more sensor fields.")
                    return {}

                return {
                    "noise_db": noise_db,
                    "pm25": pm25,
                    "pm10": pm10,
                    "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    "device_id": "CLOUD_LATEST_SENSOR",
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                }
        except Exception as e:
            logger.warning(
                "Cloud latest sensor unavailable at %s: %s",
                self.cloud_service_url,
                str(e),
            )
            return {}
