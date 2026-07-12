import requests
import base64
import json
from io import BytesIO
from PIL import Image

# Create a small dummy image in base64
img = Image.new('RGB', (224, 224), color = 'red')
buffered = BytesIO()
img.save(buffered, format="JPEG")
img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
payload_image = f"data:image/jpeg;base64,{img_str}"

payload = {
    "timestamp": "2026-07-12T02:00:00Z",
    "owner_id": "test_owner",
    "latitude": 12.9716,
    "longitude": 77.7500,
    "images": [payload_image],
    "voice_query": "Test query"
}

try:
    print("Sending POST request to http://localhost:8000/observation...")
    response = requests.post("http://localhost:8000/observation", json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
