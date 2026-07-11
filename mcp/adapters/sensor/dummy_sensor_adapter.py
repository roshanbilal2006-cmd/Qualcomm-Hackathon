"""
Dummy sensor adapter - generates realistic bounded-random readings.
Used when SENSOR_MODE=demo. Implements the SensorProvider interface.
"""

import random
from datetime import datetime, timezone

from mcp.interfaces.sensor_provider import SensorProvider


class DummySensorAdapter(SensorProvider):
    def __init__(self, device_id: str = "UNO-Q") -> None:
        self._device_id = device_id

    def read(self) -> dict:
        return {
            "device_id": self._device_id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "noise_db": round(random.uniform(40, 90), 1),
            "pm25": round(random.uniform(10, 100), 1),
            "pm10": round(random.uniform(20, 150), 1),
        }

    def get_status(self) -> str:
        # Dummy source is always "connected" - it has no external
        # dependency that can fail.
        return "connected"