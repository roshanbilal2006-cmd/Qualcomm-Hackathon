import asyncio

import pytest

from mcp.adapters.sensor.dummy_sensor_adapter import DummySensorAdapter
from mcp.adapters.rera.live_rera_adapter import LiveRERAAdapter
from mcp.utils.exceptions import RERAUnavailableError
from backend.adapters.ai_adapter import AIAdapter
from backend.fusion.correlation import parse_iso_timestamp, correlate_sensor_data
from backend.fusion.scoring import calculate_development_score


def test_ai_adapter_unavailable_fallback_is_provider_neutral_and_has_empty_embedding(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json):
            raise RuntimeError("AI service unavailable")

    monkeypatch.setattr("backend.adapters.ai_adapter.httpx.AsyncClient", FakeAsyncClient)

    async def run_prediction():
        return await AIAdapter(service_url="http://localhost:8001").predict(["/tmp/image.jpg"])

    result = asyncio.run(run_prediction())

    assert result["stage"] == "Unknown"
    assert result["progress"] == 0.0
    assert result["confidence"] == 0.0
    assert result["description"] == "Current AI service unavailable; visual construction evidence was not verified."
    assert result["embedding"] == []


def test_dummy_sensor_identifies_simulated_payload_and_status():
    sensor = DummySensorAdapter()
    payload = sensor.read()
    assert payload.get("data_origin") == "simulated"
    assert payload.get("sensor_source") == "dummy"
    assert sensor.get_status() == "simulated"


def test_parse_invalid_timestamp_returns_none_and_not_now():
    assert parse_iso_timestamp("not-a-date") is None


def test_missing_sensor_coordinates_do_not_create_a_valid_correlation():
    # Missing coordinates should not become a hardcoded valid location
    assert (
        correlate_sensor_data(
            phone_lat=12.9716,
            phone_lon=77.7500,
            phone_timestamp_str="2026-07-09T10:30:00Z",
            sensor_data={"timestamp": "2026-07-09T10:30:01Z"},
            sensor_lat=None,
            sensor_lon=None,
        )
        is False
    )


def test_invalid_timestamp_prevents_temporal_correlation():
    assert (
        correlate_sensor_data(
            phone_lat=12.9716,
            phone_lon=77.7500,
            phone_timestamp_str="not-a-date",
            sensor_data={"timestamp": "2026-07-09T10:30:01Z"},
            sensor_lat=12.9716,
            sensor_lon=77.7500,
        )
        is False
    )


def test_live_rera_unavailable_path_never_becomes_mock():
    adapter = LiveRERAAdapter(base_url=None, api_key=None)

    assert adapter.get_status() == "unavailable"

    with pytest.raises(RERAUnavailableError, match="not yet configured"):
        adapter.get_all()

    with pytest.raises(RERAUnavailableError, match="not yet configured"):
        adapter.get_by_id("RERA-KA-00123")


def test_crowdsourced_environmental_data_stays_distinct_from_physical_sensor_evidence():
    score = calculate_development_score(
        visual_stage="Finishing",
        progress=50.0,
        visual_confidence=0.87,
        sensor_status="crowdsourced",
        noise_db=75.0,
        dust_pm25=50.0,
        dust_pm10=40.0,
        rera_projects=[],
    )

    assert "Sensor evidence is not physical hardware telemetry" in score["summary"]
    assert "High noise and dust telemetry confirms active physical development" not in score["summary"]
