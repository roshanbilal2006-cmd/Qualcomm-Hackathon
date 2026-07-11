"""
Tests for GET /nearby_projects and GET /project/{id}.
Runs against the default mock-mode configuration (MockRERAAdapter),
using the seeded data/mock_rera.json dataset.
"""

from fastapi.testclient import TestClient

from mcp.main import create_app

client = TestClient(create_app())


def test_nearby_projects_returns_200():
    response = client.get("/nearby_projects")
    assert response.status_code == 200


def test_nearby_projects_contract_has_no_id_field():
    response = client.get("/nearby_projects")
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    for project in data:
        assert set(project.keys()) == {"name", "builder", "status", "distance"}
        assert "id" not in project


def test_project_by_id_returns_200_for_known_id():
    # Uses an id present in data/mock_rera.json
    response = client.get("/project/RERA-KA-00123")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == "RERA-KA-00123"
    assert data["name"] == "Prestige Tech Park"


def test_project_by_id_returns_404_for_unknown_id():
    response = client.get("/project/RERA-KA-99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()