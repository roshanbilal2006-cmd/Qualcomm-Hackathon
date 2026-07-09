import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger("landsense.iot_adapter")

class IoTAdapter:
    def __init__(self, service_url: str = "http://localhost:8002"):
        self.service_url = service_url

    async def get_sensor_data(self, latitude: float | None = None, longitude: float | None = None) -> dict:
        """
        Retrieves environmental telemetry from Arduino UNO Q IoT node.
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
                    logger.error(f"IoT Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to connect to IoT Service at {self.service_url}: {str(e)}")

        # Fallback dummy environmental data
        logger.warning("Using fallback local mock sensor data.")
        return {
            "noise_db": 62.5,
            "pm25": 32.1,
            "pm10": 68.4,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": "MOCK_UNO_Q_FALLBACK"
        }
