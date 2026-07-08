import uvicorn
from fastapi import FastAPI
import logging

app = FastAPI(title="LandSense MCP (RERA filings / permits) Simulator", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.mcp")

@app.get("/nearby_projects")
async def get_nearby_projects(latitude: float, longitude: float, radius_meters: float = 500.0):
    """
    Returns mock RERA municipal permits near the query coordinate.
    """
    logger.info(f"MCP query at Lat={latitude}, Lng={longitude} with radius={radius_meters}m")
    
    # We will simulate a local list
    return [
        {
            "name": "Prestige Kings County (MCP-verified)",
            "builder": "Prestige Group",
            "status": "Approved",
            "distance": 120.0
        },
        {
            "name": "Unregistered Block B (MCP-warned)",
            "builder": "Unknown",
            "status": "Suspended / Flagged",
            "distance": 240.0
        }
    ]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
