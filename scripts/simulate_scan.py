import requests
import json
from datetime import datetime, timezone
import random
import sys
import base64
from io import BytesIO

from PIL import Image, ImageDraw

BACKEND_URL = "http://localhost:8000"

def create_mock_construction_image():
    image = Image.new("RGB", (640, 420), "#9fb7c9")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 300, 640, 420), fill="#b98552")

    for x in range(120, 501, 95):
        draw.rectangle((x, 120, x + 16, 310), fill="#6f7680")
    for y in range(145, 256, 55):
        draw.rectangle((90, y, 540, y + 14), fill="#6f7680")

    draw.line((90, 105, 540, 285), fill="#d6b35a", width=6)
    draw.line((540, 105, 90, 285), fill="#d6b35a", width=6)
    draw.rectangle((420, 250, 505, 305), fill="#c84d32")
    draw.rectangle((445, 225, 479, 250), fill="#f3c24d")

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=86)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"

def trigger_simulation(correlated=True):
    print("-------------------------------------------------------------------")
    print(f"Triggering LandSense Scan (Spatial Correlation: {correlated})")
    print("-------------------------------------------------------------------")

    # If correlated is True, keep offset within ~25 meters of the IoT node (12.9716, 77.7500)
    # If False, offset far away (e.g., 800m) to trigger a mismatch/disconnected status
    if correlated:
        lat = 12.9716 + random.uniform(-0.0001, 0.0001)
        lon = 77.7500 + random.uniform(-0.0001, 0.0001)
    else:
        lat = 12.9716 + 0.0080
        lon = 77.7500 + 0.0080

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": lat,
        "longitude": lon,
        "images": [create_mock_construction_image()],
        "voice_query": "Is this project RERA approved? Check noise and particulate emissions."
    }

    try:
        response = requests.post(f"{BACKEND_URL}/observation", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("Successfully processed observation by Snapdragon X Elite pipeline!")
            print(f"Observation ID:      {result['observation_id']}")
            print(f"Construction Stage:  {result['construction_stage']}")
            print(f"Confidence Level:    {result['confidence']}")
            print(f"Sensor Status:       {result['sensor_status']}")
            print(f"Development Score:   {result['development_score']}/100")
            print(f"RERA Filings Found:  {len(result['rera_projects'])}")
            print(f"Fusion Reason:       {result['summary']}")
        else:
            print(f"Error: Backend returned status code {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Backend server on http://localhost:8000")
        print("Make sure you start the servers first using python scripts/run_all.py")

if __name__ == "__main__":
    is_correlated = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == "fail":
        is_correlated = False
    
    trigger_simulation(correlated=is_correlated)
