import uvicorn
from fastapi import FastAPI
from datetime import datetime, timezone
import random
import logging

app = FastAPI(title="LandSense Arduino UNO Q IoT Node Simulator", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("landsense.iot")

@app.get("/sensor")
async def get_sensor_data(lat: float = 12.9716, lon: float = 77.7500):
    """
    Simulates Arduino UNO Q sensor telemetry of dust particulates (PM2.5/PM10) and noise levels.
    """
    noise = round(random.uniform(55.0, 88.0), 1)
    pm25 = round(random.uniform(15.0, 95.0), 1)
    pm10 = round(pm25 * random.uniform(1.5, 2.2), 1)
    
    logger.info(f"IoT Node reporting: Noise={noise}dB, PM2.5={pm25}ug/m3")
    
    return {
        "noise_db": noise,
        "pm25": pm25,
        "pm10": pm10,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": "ARDUINO_UNO_Q_WHITEFIELD",
        # Return sensor coordinate to allow correlation rules to execute
        "latitude": lat,
        "longitude": lon
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)
