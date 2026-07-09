from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ObservationRequest, ObservationResponse, HeatmapResponse
import database
import ai_service
import uvicorn

app = FastAPI(
    title="LandSense AI Backend",
    description="Backend API for the LandSense AI Qualcomm Hackathon project",
    version="1.0.0"
)

# Allow CORS for local testing/development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Initializes the database on startup."""
    database.init_db()

@app.get("/")
def read_root():
    return {"message": "LandSense AI Backend is running."}

@app.post("/v1/observation", response_model=ObservationResponse)
def submit_observation(request: ObservationRequest):
    """
    Receives images, location, and voice query from the mobile device.
    Processes the data through the AI service and returns a construction report.
    """
    try:
        # 1. Save observation data to DB (excluding images for hackathon brevity)
        obs_id = database.save_observation(request)
        
        # 2. Process data via AI
        report = ai_service.process_observation(request)
        
        return report
        
    except Exception as e:
        print(f"Error processing observation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during processing.")

@app.get("/v1/heatmap", response_model=HeatmapResponse)
def get_heatmap():
    """
    Retrieves construction density points for the community heatmap.
    """
    try:
        points = database.get_heatmap_points()
        return HeatmapResponse(points=points)
    except Exception as e:
        print(f"Error fetching heatmap: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error fetching heatmap.")


if __name__ == "__main__":
    # Run the server locally on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
