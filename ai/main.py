import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import random
import logging

app = FastAPI(title="LandSense FastVLM AI Service Simulator", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.ai")

class PredictRequest(BaseModel):
    images: list[str]

@app.post("/predict")
async def predict(payload: PredictRequest):
    logger.info(f"AI Service received {len(payload.images)} images for prediction.")
    
    stages = ["Excavation", "Foundation", "Structure", "Finishing", "Completed"]
    # Provide a realistic prediction
    stage = random.choice(stages)
    progress_map = {
        "Excavation": 15.0,
        "Foundation": 35.0,
        "Structure": 65.0,
        "Finishing": 85.0,
        "Completed": 100.0
    }
    progress = progress_map[stage]
    confidence = round(random.uniform(0.80, 0.98), 2)
    
    description = f"FastVLM visual reasoning: Construction site identified at stage '{stage}' (~{progress}% progress) with {confidence * 100}% confidence. Scaffold structures visible."
    
    # Generate mock 128-dim embedding vector
    embedding = [round(random.gauss(0, 0.1), 4) for _ in range(128)]
    
    return {
        "stage": stage,
        "progress": progress,
        "confidence": confidence,
        "description": description,
        "embedding": embedding
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
