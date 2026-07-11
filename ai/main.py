import logging

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from ai.engine import ImageDecodeError, VisionInferenceEngine
except ModuleNotFoundError:
    from engine import ImageDecodeError, VisionInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.ai")

app = FastAPI(title="LandSense OpenRouter + OpenCV AI Service", version="1.0.0")
engine = VisionInferenceEngine()


class PredictRequest(BaseModel):
    images: list[str] = Field(default_factory=list)


@app.post("/predict")
async def predict(payload: PredictRequest):
    try:
        return engine.predict(payload.images)
    except ImageDecodeError:
        logger.warning("Invalid image payload received | image_count=%d", len(payload.images))
        return {
            "status": "error",
            "message": "Invalid image",
        }


@app.post("/health")
async def health():
    return {
        "model": engine.model_name,
        "status": "loaded" if engine.loaded else "not_loaded",
        "device": engine.device,
        "runtime_backend": engine.runtime_backend,
        "ai_backend": "openrouter_opencv",
        "model_artifacts_loaded": False,
        "model_dir": None,
        "transformers_model_dir": None,
        "openrouter_enabled": bool(engine.openrouter_api_key),
        "openrouter_model": engine.openrouter_vision_model if engine.openrouter_api_key else None,
        "openrouter_error": engine._openrouter_error,
        "opencv_enabled": True,
        "inference_ready": engine.loaded,
    }


@app.get("/health")
async def health_get():
    return await health()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
