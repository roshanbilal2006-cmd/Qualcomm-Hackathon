import httpx
import logging

logger = logging.getLogger("landsense.cloud_adapter")

class CloudAdapter:
    def __init__(self, service_url: str = "http://localhost:8003"):
        self.service_url = service_url

    async def upload_observation(self, observation: dict) -> bool:
        """
        Uploads processed construction observation (no raw files) to Qualcomm AI Cloud 100.
        """
        # Ensure we do not upload raw image blobs/base64 strings
        processed_data = observation.copy()
        if "images" in processed_data:
            # Replace images with their count or reference identifiers
            processed_data["images"] = [f"image_{i}" for i in range(len(processed_data["images"]))]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.service_url}/observation",
                    json=processed_data
                )
                if response.status_code == 200:
                    logger.info("Successfully synchronized observation to Qualcomm AI Cloud 100.")
                    return True
                else:
                    logger.warning(f"Cloud Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(
                "Qualcomm AI Cloud simulator unavailable at %s; observation remains in local SQLite. %s",
                self.service_url,
                str(e),
            )

        return False

    async def get_heatmap(self) -> list[dict]:
        """
        Retrieves the public cloud heatmap dataset.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/heatmap")
                if response.status_code == 200:
                    return [self._normalize_heatmap_point(item) for item in response.json()]
                logger.warning(f"Cloud heatmap returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(
                "Cloud heatmap unavailable at %s; using local SQLite heatmap fallback. %s",
                self.service_url,
                str(e),
            )

        return []

    def _normalize_heatmap_point(self, item: dict) -> dict:
        return {
            "observation_id": item.get("observation_id", ""),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "development_score": item.get("development_score", item.get("score", 0)),
            "noise_db": item.get("noise_db", item.get("noise", 0.0)),
            "dust_pm25": item.get("dust_pm25", item.get("dust", 0.0)),
            "stage": item.get("stage", item.get("construction_stage", "Unknown")),
        }
