"""
Sensor service - orchestrates sensor reads via an injected SensorProvider.
Depends only on the SensorProvider interface and sensor Pydantic models -
never imports a concrete adapter.
"""

import logging
from typing import Union

from interfaces.sensor_provider import SensorProvider
from models.sensor_models import SensorReading, SensorOfflineResponse
from utils.exceptions import DeviceOfflineError

logger = logging.getLogger(__name__)


class SensorService:
    def __init__(self, provider: SensorProvider) -> None:
        self._provider = provider

    def get_current_reading(self) -> Union[SensorReading, SensorOfflineResponse]:
        try:
            raw = self._provider.read()
        except DeviceOfflineError as exc:
            logger.warning("Sensor read failed, reporting offline: %s", exc)
            return SensorOfflineResponse()

        return SensorReading(**raw)

    def get_status(self) -> str:
        return self._provider.get_status()