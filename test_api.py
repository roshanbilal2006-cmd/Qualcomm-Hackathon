from fastapi.testclient import TestClient
from cloud.main import app

client = TestClient(app)

def test_create_observation():
    payload = {
        "observation_id": "obs-123",
        "latitude": 12.97,
        "longitude": 77.59,
        "timestamp": "2026-07-08T10:00:00Z",
        "construction_stage": "Structural",
        "progress": 62,
        "dust": 42.0,
        "noise": 71.0,
        "development_score": 87,
        "summary": "Building frame in progress",
        "embedding": [0.1, 0.2, 0.3, 0.4]
    }
    response = client.post("/observation", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_heatmap():
    response = client.get("/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["latitude"] == 12.97
    assert data[0]["score"] == 87

def test_get_history():
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_latest_sensor():
    response = client.get("/latest_sensor")
    assert response.status_code == 200
    data = response.json()
    assert data["dust"] == 42.0
    assert data["noise"] == 71.0

def test_get_nearby():
    response = client.get("/nearby?lat=12.97&lng=77.59&radius_km=5.0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_observations"] >= 1

if __name__ == "__main__":
    print("Testing create observation...")
    test_create_observation()
    print("Testing get heatmap...")
    test_get_heatmap()
    print("Testing get history...")
    test_get_history()
    print("Testing get latest sensor...")
    test_get_latest_sensor()
    print("Testing get nearby...")
    test_get_nearby()
    print("Testing get stats...")
    test_get_stats()
    print("All tests passed!")
