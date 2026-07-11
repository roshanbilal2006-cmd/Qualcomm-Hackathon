"""
Project service - derives /nearby_projects and /project/{id} from the
single RERAProvider source of truth. Depends only on the RERAProvider
interface and the rera/project Pydantic models - never imports a
concrete adapter.
"""

import logging

from mcp.interfaces.rera_provider import RERAProvider
from mcp.models.rera_models import RERAProject
from mcp.models.project_models import NearbyProject
from mcp.utils.exceptions import RERAUnavailableError

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, rera_provider: RERAProvider) -> None:
        self._rera_provider = rera_provider

    def get_nearby_projects(self) -> list[NearbyProject]:
        try:
            raw_projects = self._rera_provider.get_all()
        except RERAUnavailableError as exc:
            logger.error("RERA dataset unavailable for nearby_projects: %s", exc)
            raise

        # Validate against the full model first (ensures data integrity),
        # then project down to the locked public contract for this
        # endpoint - name, builder, status, distance only. No `id`.
        full_projects = [RERAProject(**project) for project in raw_projects]
        return [
            NearbyProject(
                name=project.name,
                builder=project.builder,
                status=project.status,
                distance=project.distance,
            )
            for project in full_projects
        ]

    def get_project_by_id(self, project_id: str) -> RERAProject | None:
        try:
            raw_project = self._rera_provider.get_by_id(project_id)
        except RERAUnavailableError as exc:
            logger.error("RERA source unavailable for project_id=%s: %s", project_id, exc)
            raise

        if raw_project is None:
            return None

        return RERAProject(**raw_project)