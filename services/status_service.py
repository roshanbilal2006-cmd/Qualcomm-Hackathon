"""
Status service - aggregates sensor and RERA provider health, plus
current mode configuration, into the StatusResponse contract.
Depends only on provider interfaces, Settings, and the status model -
never imports a concrete adapter.
"""

import logging

from interfaces.sensor_provider import SensorProvider
from interfaces.rera_provider import RERAProvider
from config.settings import Settings
from models.status_models import StatusResponse

logger = logging.getLogger(__name__)


class StatusService:
    def __init__(
        self,
        sensor_provider: SensorProvider,
        rera_provider: RERAProvider,
        settings: Settings,
    ) -> None:
        self._sensor_provider = sensor_provider
        self._rera_provider = rera_provider
        self._settings = settings

    def get_status(self) -> StatusResponse:
        arduino_status = self._sensor_provider.get_status()

        rera_reachable = True
        try:
            # A cheap reachability probe: get_status() is documented to
            # never raise, but we still verify the RERA source can
            # actually serve data, since get_status() alone only
            # reports "mock"/"live" mode, not true reachability.
            self._rera_provider.get_all()
        except Exception as exc:  # noqa: BLE001 - deliberately broad,
            # this is a best-effort health probe, not a re-raise path.
            logger.warning("RERA reachability probe failed: %s", exc)
            rera_reachable = False

        sensor_healthy = arduino_status == "connected"
        mcp_status = "healthy" if (sensor_healthy and rera_reachable) else "degraded"

        return StatusResponse(
            arduino=arduino_status,  # type: ignore[arg-type]
            sensor_mode=self._settings.sensor_mode,
            rera_mode=self._settings.rera_mode,
            mcp=mcp_status,
        )