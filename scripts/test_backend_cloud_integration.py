import sys
import time
from datetime import datetime, timezone

import requests


BACKEND_URL = "http://localhost:8000"
CLOUD_URL = "http://localhost:8003"


def require_service(name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code < 500:
            return
    except requests.RequestException as exc:
        raise RuntimeError(f"{name} is not reachable at {url}: {exc}") from exc

    raise RuntimeError(
        f"{name} returned HTTP {response.status_code} at {url}: {response.text}"
    )


def main():
    require_service("Backend", f"{BACKEND_URL}/history")
    require_service("Cloud", f"{CLOUD_URL}/history")

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": 12.9716,
        "longitude": 77.7500,
        "images": ["integration_test_frame"],
        "voice_query": "Integration test scan from backend to cloud.",
    }

    backend_response = requests.post(
        f"{BACKEND_URL}/observation",
        json=payload,
        timeout=20,
    )
    backend_response.raise_for_status()
    observation = backend_response.json()
    observation_id = observation["observation_id"]

    cloud_match = None
    for _ in range(10):
        cloud_response = requests.get(f"{CLOUD_URL}/history", timeout=5)
        cloud_response.raise_for_status()
        cloud_history = cloud_response.json()
        cloud_match = next(
            (
                item
                for item in cloud_history
                if item.get("observation_id") == observation_id
            ),
            None,
        )
        if cloud_match:
            break
        time.sleep(0.5)

    if not cloud_match:
        raise AssertionError(
            f"Backend observation {observation_id} was not found in cloud history"
        )

    latest_sensor = requests.get(f"{CLOUD_URL}/latest_sensor", timeout=5)
    latest_sensor.raise_for_status()

    print("Backend -> Cloud integration passed")
    print(f"Observation ID: {observation_id}")
    print(f"Backend stage:  {observation.get('construction_stage')}")
    print(f"Sensor status:  {observation.get('sensor_status')}")
    print(f"Cloud score:    {cloud_match.get('development_score')}")
    print(f"Latest cloud:   {latest_sensor.json()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Integration test failed: {exc}", file=sys.stderr)
        print(
            "Start the services first with: python scripts/run_all.py",
            file=sys.stderr,
        )
        sys.exit(1)
