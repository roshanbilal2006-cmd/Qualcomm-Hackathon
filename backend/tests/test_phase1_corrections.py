from mcp.adapters.sensor.dummy_sensor_adapter import DummySensorAdapter
from backend.fusion.correlation import parse_iso_timestamp, correlate_sensor_data


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
