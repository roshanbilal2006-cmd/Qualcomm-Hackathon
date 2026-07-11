"""
Tests for GET /sensor.
Runs against the default demo-mode configuration (DummySensorAdapter).
"""

from fastapi.testclient import TestClient

from mcp.main import create_app

client = TestClient(create_app())


def test_sensor_endpoint_returns_200():
    response = client.get("/sensor")
    assert response.status_code == 200


def test_sensor_endpoint_returns_valid_reading_shape():
    response = client.get("/sensor")
    data = response.json()

    if "status" in data:
        # Offline shape
        assert data == {"status": "offline"}
    else:
        # Reading shape
        assert set(data.keys()) == {
            "device_id", "timestamp", "noise_db", "pm25", "pm10"
        }
        assert 40 <= data["noise_db"] <= 90
        assert 10 <= data["pm25"] <= 100
        assert 20 <= data["pm10"] <= 150


def test_sensor_endpoint_device_id_matches_default():
    response = client.get("/sensor")
    data = response.json()
    if "device_id" in data:
        assert data["device_id"] == "UNO-Q"