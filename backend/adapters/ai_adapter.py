import httpx
import logging

logger = logging.getLogger("landsense.ai_adapter")

class AIAdapter:
    def __init__(self, service_url: str = "http://localhost:8001"):
        self.service_url = service_url

    async def predict(self, images: list[str]) -> dict:
        """
        Sends images to the local AI service and normalizes the model contract
        for the existing backend pipeline.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.service_url}/predict",
                    json={"images": images}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "error":
                        logger.error(f"AI Service rejected image payload: {result.get('message')}")
                    else:
                        return self._normalize_prediction(result)
                else:
                    logger.error(f"AI Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to connect to AI Service at {self.service_url}: {str(e)}")
        
        # Do not fabricate construction progress if the Qualcomm VLM service is unavailable.
        logger.warning("AI service unavailable; returning explicit unknown visual result.")
        return {
            "stage": "Unknown",
            "progress": 0.0,
            "confidence": 0.0,
            "description": "Qualcomm FastVLM service unavailable; visual construction evidence was not verified.",
            "embedding": [0.01] * 128
        }

    def _normalize_prediction(self, result: dict) -> dict:
        return {
            "stage": result.get("construction_stage", result.get("stage", "Unknown")),
            "progress": float(result.get("progress_percentage", result.get("progress", 0.0))),
            "confidence": float(result.get("confidence", 0.0)),
            "description": result.get("description", ""),
            "embedding": result.get("embedding", []),
            "site_likelihood": float(result.get("site_likelihood", 0.0)),
            "opencv_analysis": result.get("opencv_analysis", {}),
        }
