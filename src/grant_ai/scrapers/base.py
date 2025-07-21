"""
Base class for grant web scrapers.
"""
from abc import ABC, abstractmethod
from typing import List

from grant_ai.models.grant import Grant


class GrantScraper(ABC):
    """Abstract base class for grant scrapers."""

    @abstractmethod
    def search_grants(self, query: str = "", **kwargs) -> list[Grant]:
        """Search for grants matching the query."""
        # Example implementation: return all grants containing the query in their title or description
        results = []
        for grant in self.get_all_grants():
            title_match = query.lower() in grant.title.lower()
            desc_match = query.lower() in grant.description.lower()
            if title_match or desc_match:
                results.append(grant)
        return results

    def get_all_grants(self) -> list[Grant]:
        """Return all grants (stub for demonstration)."""
        # This should be implemented in subclasses to fetch actual grants
        return []
