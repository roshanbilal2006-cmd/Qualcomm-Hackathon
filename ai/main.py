import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

load_dotenv()

try:
    from ai.engine import ImageDecodeError, VisionInferenceEngine
    from ai.npu_engine import SnapdragonVisionEngine
except ModuleNotFoundError:
    from engine import ImageDecodeError, VisionInferenceEngine
    from npu_engine import SnapdragonVisionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.ai")

app = FastAPI(title="LandSense AI Service", version="1.0.0")

# Attempt to load NPU engine first
npu_engine = SnapdragonVisionEngine()
if getattr(npu_engine, "loaded", False):
    engine = npu_engine
    logger.info("Using Local NPU Engine")
else:
    engine = VisionInferenceEngine()
    logger.info("Falling back to Vision Inference Engine (Cirrascale/OpenCV)")


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
        "status": "loaded" if getattr(engine, "loaded", False) else "not_loaded",
        "device": getattr(engine, "device", "unknown"),
        "runtime_backend": getattr(engine, "runtime_backend", "unknown"),
        "ai_backend": "npu_vlm" if isinstance(engine, SnapdragonVisionEngine) else "cirrascale_opencv",
        "model_artifacts_loaded": getattr(engine, "loaded", False),
        "model_dir": getattr(engine, "model_dir", None),
        "transformers_model_dir": None,
        "openrouter_enabled": False,
        "openrouter_model": None,
        "openrouter_error": None,
        "opencv_enabled": not isinstance(engine, SnapdragonVisionEngine),
        "inference_ready": getattr(engine, "loaded", False),
    }


@app.get("/health")
async def health_get():
    return await health()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
