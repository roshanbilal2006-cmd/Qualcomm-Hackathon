"""
Abstract interface for sensor data providers.
Concrete implementations (dummy, Arduino) live in adapters/sensor/.
Services depend only on this interface, never on concrete adapters.
"""

from abc import ABC, abstractmethod


class SensorProvider(ABC):
    @abstractmethod
    def read(self) -> dict:
        """
        Returns a raw sensor reading as a dict with keys:
        device_id, timestamp, noise_db, pm25, pm10.

        Implementations must raise a DeviceOfflineError (from
        utils.exceptions) if the reading cannot be obtained -
        never return partial or malformed data, and never let
        low-level exceptions (e.g. serial.SerialException) escape
        this method uncaught.
        """
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> str:
        """
        Returns "connected" or "disconnected", reflecting the current
        health of the underlying data source. Must never raise.
        """
        raise NotImplementedError