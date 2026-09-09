"""
Live RERA adapter - stub for future integration with the live
Karnataka RERA data source (or other government API).
Used when RERA_MODE=live. Implements the RERAProvider interface.

This adapter remains intentionally non-functional in Phase 1. If no
LIVE_RERA_BASE_URL is configured, it must report a clear unavailable
state and never silently substitute a mock or synthetic provider.
"""

import logging

import httpx

from mcp.interfaces.rera_provider import RERAProvider
from mcp.utils.exceptions import RERAUnavailableError

logger = logging.getLogger(__name__)


class LiveRERAAdapter(RERAProvider):
    def __init__(self, base_url: str | None, api_key: str | None) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def get_all(self) -> list[dict]:
        if not self._base_url:
            raise RERAUnavailableError(
                "Live RERA integration is not yet configured "
                "(LIVE_RERA_BASE_URL is not set). "
                "No silent fallback to mock RERA is allowed."
            )

        try:
            response = httpx.get(
                f"{self._base_url}/projects",
                headers=self._auth_headers(),
                timeout=5.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("Live RERA request failed: %s", exc)
            raise RERAUnavailableError(f"Live RERA source unreachable: {exc}") from exc

    def get_by_id(self, project_id: str) -> dict | None:
        if not self._base_url:
            raise RERAUnavailableError(
                "Live RERA integration is not yet configured "
                "(LIVE_RERA_BASE_URL is not set). "
                "No silent fallback to mock RERA is allowed."
            )

        try:
            response = httpx.get(
                f"{self._base_url}/projects/{project_id}",
                headers=self._auth_headers(),
                timeout=5.0,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.error("Live RERA request failed: %s", exc)
            raise RERAUnavailableError(f"Live RERA source unreachable: {exc}") from exc

    def get_status(self) -> str:
        return "unavailable" if not self._base_url else "live"

    def _auth_headers(self) -> dict:
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        return {}