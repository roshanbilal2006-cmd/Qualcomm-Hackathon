"""
Mock RERA adapter - serves RERA project data from a local JSON file.
Used when RERA_MODE=mock. Implements the RERAProvider interface.
"""

import json
import logging
from pathlib import Path

from mcp.interfaces.rera_provider import RERAProvider
from mcp.utils.exceptions import RERAUnavailableError

logger = logging.getLogger(__name__)


class MockRERAAdapter(RERAProvider):
    def __init__(self, data_path: str) -> None:
        self._data_path = Path(data_path)
        self._cache: list[dict] | None = None

    def _load(self) -> list[dict]:
        if self._cache is not None:
            return self._cache

        try:
            with self._data_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            logger.error("Mock RERA data file not found: %s", self._data_path)
            raise RERAUnavailableError(
                f"Mock RERA dataset not found at {self._data_path}"
            ) from exc
        except json.JSONDecodeError as exc:
            logger.error("Mock RERA data file is malformed: %s", exc)
            raise RERAUnavailableError(
                f"Mock RERA dataset at {self._data_path} is malformed: {exc}"
            ) from exc

        if not isinstance(data, list):
            raise RERAUnavailableError(
                f"Mock RERA dataset at {self._data_path} must be a JSON array"
            )

        self._cache = data
        return self._cache

    def get_all(self) -> list[dict]:
        return self._load()

    def get_by_id(self, project_id: str) -> dict | None:
        projects = self._load()
        for project in projects:
            if project.get("id") == project_id:
                return project
        return None

    def get_status(self) -> str:
        try:
            self._load()
            return "mock"
        except RERAUnavailableError:
            return "mock"