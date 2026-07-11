"""
Adapter factory - the single place in the codebase that decides
which concrete adapter implements each interface, based on config.

Called exactly once, from main.py, at application startup. No other
module should ever import a concrete adapter class directly - always
go through these factory functions and depend on the interface type.
"""

from mcp.config.settings import Settings
from mcp.interfaces.sensor_provider import SensorProvider
from mcp.interfaces.rera_provider import RERAProvider

from mcp.adapters.sensor.dummy_sensor_adapter import DummySensorAdapter
from mcp.adapters.sensor.arduino_sensor_adapter import ArduinoSensorAdapter
from mcp.adapters.rera.mock_rera_adapter import MockRERAAdapter
from mcp.adapters.rera.live_rera_adapter import LiveRERAAdapter


def build_sensor_provider(settings: Settings) -> SensorProvider:
    if settings.sensor_mode == "demo":
        return DummySensorAdapter()

    if settings.sensor_mode == "live":
        return ArduinoSensorAdapter(
            port=settings.arduino_port,
            baud_rate=settings.arduino_baud_rate,
            read_timeout_seconds=settings.arduino_read_timeout_seconds,
        )

    # Unreachable in practice - Settings.sensor_mode is a Literal type
    # validated by Pydantic at startup, so this branch only guards
    # against future refactors that loosen that type.
    raise ValueError(f"Unknown sensor_mode: {settings.sensor_mode}")


def build_rera_provider(settings: Settings) -> RERAProvider:
    if settings.rera_mode == "mock":
        return MockRERAAdapter(data_path=settings.mock_rera_data_path)

    if settings.rera_mode == "live":
        return LiveRERAAdapter(
            base_url=settings.live_rera_base_url,
            api_key=settings.live_rera_api_key,
        )

    raise ValueError(f"Unknown rera_mode: {settings.rera_mode}")