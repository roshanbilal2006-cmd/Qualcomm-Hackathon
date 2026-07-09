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
                    logger.error(f"Cloud Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to synchronize with Qualcomm AI Cloud 100 at {self.service_url}: {str(e)}")

        return False

    async def get_heatmap(self) -> list[dict]:
        """
        Retrieves the public cloud heatmap dataset.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.service_url}/heatmap")
                if response.status_code == 200:
                    return response.json()
                logger.error(f"Cloud heatmap returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to retrieve cloud heatmap from {self.service_url}: {str(e)}")

        return []
