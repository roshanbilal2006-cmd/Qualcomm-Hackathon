import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.database.session import init_db
from backend.api.routes import router as api_router

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] - %(message)s"
)
logger = logging.getLogger("landsense.backend")

app = FastAPI(
    title="LandSense AI Orchestrator",
    description="The local Snapdragon X Elite Brain coordinating the multi-device pipelines.",
    version="1.0.0"
)

# Enable CORS for the dashboard front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include APIs
app.include_router(api_router)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing LandSense SQLite Database and seeding projects...")
    init_db()
    logger.info("Database loaded and ready.")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
