"""
Registry for managing multiple institution adapters.
"""
from typing import Optional

from devvyn.institutions.base import Institution, InstitutionAdapter


class InstitutionRegistry:
    """
    Registry of all available institution adapters.

    Provides a single point of access for querying across institutions.
    """

    def __init__(self):
        self._institutions: dict[str, InstitutionAdapter] = {}

    def register(self, adapter: InstitutionAdapter) -> None:
        """Register an institution adapter."""
        self._institutions[adapter.id] = adapter

    def get(self, institution_id: str) -> Optional[InstitutionAdapter]:
        """Get an institution adapter by ID."""
        return self._institutions.get(institution_id.lower())

    def all(self) -> list[InstitutionAdapter]:
        """Get all registered institution adapters."""
        return list(self._institutions.values())

    def ids(self) -> list[str]:
        """Get all registered institution IDs."""
        return list(self._institutions.keys())

    def __contains__(self, institution_id: str) -> bool:
        return institution_id.lower() in self._institutions

    def __iter__(self):
        return iter(self._institutions.values())

    def __len__(self) -> int:
        return len(self._institutions)


# Global registry singleton
_registry: Optional[InstitutionRegistry] = None


def get_registry() -> InstitutionRegistry:
    """
    Get the global institution registry.

    Lazily initializes with all known institution adapters.
    """
    global _registry
    if _registry is None:
        _registry = InstitutionRegistry()

        # Register all known institutions
        from devvyn.institutions.usask import get_usask_adapter
        from devvyn.institutions.saskpolytech import get_saskpolytech_adapter

        _registry.register(get_usask_adapter())
        _registry.register(get_saskpolytech_adapter())

    return _registry


def get_institution(institution_id: str) -> Optional[InstitutionAdapter]:
    """Convenience function to get an institution by ID."""
    return get_registry().get(institution_id)
