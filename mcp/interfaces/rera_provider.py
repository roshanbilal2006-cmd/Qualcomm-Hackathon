"""
Abstract interface for RERA data providers.
Concrete implementations (mock, live) live in adapters/rera/.
Both rera_service and project_service depend only on this interface,
never on concrete adapters - this is what enforces a single source
of truth for RERA data across the module.
"""

from abc import ABC, abstractmethod


class RERAProvider(ABC):
    @abstractmethod
    def get_all(self) -> list[dict]:
        """
        Returns the full list of RERA project records as raw dicts,
        each containing at minimum: id, name, builder, status, distance.

        Implementations must raise RERAUnavailableError (from
        utils.exceptions) if the dataset cannot be retrieved -
        never return an empty list to signal failure, and never
        let low-level exceptions escape this method uncaught.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, project_id: str) -> dict | None:
        """
        Returns a single RERA project record as a raw dict, or None
        if no project with the given id exists. Must raise
        RERAUnavailableError if the underlying source itself is
        unreachable (as distinct from "not found", which is None).
        """
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> str:
        """
        Returns "mock" or "live" reflecting which mode is active,
        or more precisely, whether the underlying source is reachable.
        Must never raise.
        """
        raise NotImplementedError