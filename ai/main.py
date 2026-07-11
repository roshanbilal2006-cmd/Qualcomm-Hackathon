import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

load_dotenv()

try:
    from ai.engine import ImageDecodeError, VisionInferenceEngine
except ModuleNotFoundError:
    from engine import ImageDecodeError, VisionInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.ai")

app = FastAPI(title="LandSense FastVLM AI Service", version="1.0.0")
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
        "model_artifacts_loaded": bool(engine.transformers_model_dir or engine.model_artifacts),
        "model_dir": str(engine.model_dir),
        "transformers_model_dir": str(engine.transformers_model_dir) if engine.transformers_model_dir else None,
        "inference_ready": engine.loaded,
    }


@app.get("/health")
async def health_get():
    return await health()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
