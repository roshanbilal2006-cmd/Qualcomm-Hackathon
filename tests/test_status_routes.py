"""
Tests for GET /status.
Runs against the default demo/mock configuration.
"""

from fastapi.testclient import TestClient

from main import create_app

client = TestClient(create_app())


def test_status_endpoint_returns_200():
    response = client.get("/status")
    assert response.status_code == 200


def test_status_endpoint_contract_shape():
    response = client.get("/status")
    data = response.json()

    assert set(data.keys()) == {"arduino", "sensor_mode", "rera_mode", "mcp"}
    assert data["arduino"] in {"connected", "disconnected"}
    assert data["sensor_mode"] in {"demo", "live"}
    assert data["rera_mode"] in {"mock", "live"}
    assert data["mcp"] in {"healthy", "degraded"}


def test_status_endpoint_reflects_default_demo_mock_config():
    response = client.get("/status")
    data = response.json()

    assert data["sensor_mode"] == "demo"
    assert data["rera_mode"] == "mock"
    assert data["arduino"] == "connected"