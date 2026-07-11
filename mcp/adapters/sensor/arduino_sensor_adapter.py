"""
Arduino sensor adapter - reads real sensor data over a serial connection.
Used when SENSOR_MODE=live. Implements the SensorProvider interface.

Expected wire format: a single line of comma-separated values,
e.g. "72.4,38.1,61.7" representing noise_db,pm25,pm10 - adjust
parse logic here if the actual Arduino sketch uses a different format.
"""

import logging
from datetime import datetime, timezone

import serial

from mcp.interfaces.sensor_provider import SensorProvider
from mcp.utils.exceptions import DeviceOfflineError

logger = logging.getLogger(__name__)


class ArduinoSensorAdapter(SensorProvider):
    def __init__(
        self,
        port: str,
        baud_rate: int,
        read_timeout_seconds: float,
        device_id: str = "UNO-Q",
    ) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._read_timeout_seconds = read_timeout_seconds
        self._device_id = device_id

    def read(self) -> dict:
        try:
            with serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                timeout=self._read_timeout_seconds,
            ) as connection:
                raw_line = connection.readline().decode("utf-8", errors="strict").strip()

                if not raw_line:
                    raise DeviceOfflineError(
                        f"No data received from Arduino on port {self._port} "
                        f"within {self._read_timeout_seconds}s timeout"
                    )

                parts = raw_line.split(",")
                if len(parts) != 3:
                    raise DeviceOfflineError(
                        f"Malformed reading from Arduino: '{raw_line}'"
                    )

                noise_db, pm25, pm10 = (float(p) for p in parts)

        except serial.SerialException as exc:
            logger.warning("Serial connection failed on port %s: %s", self._port, exc)
            raise DeviceOfflineError(
                f"Could not open serial port {self._port}: {exc}"
            ) from exc
        except (UnicodeDecodeError, ValueError) as exc:
            logger.warning("Failed to parse Arduino output: %s", exc)
            raise DeviceOfflineError(f"Could not parse Arduino output: {exc}") from exc

        return {
            "device_id": self._device_id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "noise_db": round(noise_db, 1),
            "pm25": round(pm25, 1),
            "pm10": round(pm10, 1),
        }

    def get_status(self) -> str:
        try:
            with serial.Serial(
                port=self._port,
                baudrate=self._baud_rate,
                timeout=0.5,
            ):
                return "connected"
        except serial.SerialException:
            return "disconnected"