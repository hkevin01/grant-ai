"""
Base class for grant web scrapers.
"""
from abc import ABC, abstractmethod
from typing import List

from grant_ai.models.grant import Grant


class GrantScraper(ABC):
    """Abstract base class for grant scrapers."""
    
    @abstractmethod
    def search_grants(self, query: str = "", **kwargs) -> List[Grant]:
        """Search for grants matching the query."""
        pass
