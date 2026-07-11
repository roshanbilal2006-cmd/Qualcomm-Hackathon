"""
RERA service - serves the raw RERA dataset via an injected RERAProvider.
Depends only on the RERAProvider interface and RERAProject model -
never imports a concrete adapter.
"""

import logging

from mcp.interfaces.rera_provider import RERAProvider
from mcp.models.rera_models import RERAProject
from mcp.utils.exceptions import RERAUnavailableError

logger = logging.getLogger(__name__)


class RERAService:
    def __init__(self, provider: RERAProvider) -> None:
        self._provider = provider

    def get_all_projects(self) -> list[RERAProject]:
        try:
            raw_projects = self._provider.get_all()
        except RERAUnavailableError as exc:
            logger.error("RERA dataset unavailable: %s", exc)
            raise

        return [RERAProject(**project) for project in raw_projects]

    def get_status(self) -> str:
        return self._provider.get_status()