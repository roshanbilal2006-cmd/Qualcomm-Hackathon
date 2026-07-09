"""
Tests for GET /rera.
Runs against the default mock-mode configuration (MockRERAAdapter).
"""

from fastapi.testclient import TestClient

from main import create_app

client = TestClient(create_app())


def test_rera_endpoint_returns_200():
    response = client.get("/rera")
    assert response.status_code == 200


def test_rera_endpoint_returns_plain_array():
    response = client.get("/rera")
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_rera_endpoint_full_project_shape():
    response = client.get("/rera")
    data = response.json()

    for project in data:
        assert set(project.keys()) == {
            "id", "name", "builder", "status", "distance"
        }


def test_rera_endpoint_valid_status_values():
    response = client.get("/rera")
    data = response.json()
    valid_statuses = {"Approved", "Pending", "Rejected", "Under Review"}

    for project in data:
        assert project["status"] in valid_statuses