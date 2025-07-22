"""
Marketplace features for organizations to discover, share, and collaborate on grants.
"""
from typing import List, Dict

class GrantMarketplace:
    """Marketplace for grant opportunities and organization collaboration."""
    def __init__(self):
        """Initialize the marketplace with empty listings."""
        self.listings: List[Dict] = []

    def add_listing(self, grant_info: Dict):
        """Add a new grant listing to the marketplace.
        Args:
            grant_info: Dictionary containing grant details.
        """
        self.listings.append(grant_info)

    def search_listings(self, keywords: List[str]) -> List[Dict]:
        """Search listings by keywords in the title.
        Args:
            keywords: List of keywords to search for.
        Returns:
            List of matching grant listings.
        """
        return [g for g in self.listings if any(
            kw in g.get('title', '') for kw in keywords
        )]

    def list_grants(self) -> List[Dict]:
        """Return all grant listings in the marketplace.
        Returns:
            List of all grant listings.
        """
        return list(self.listings)
