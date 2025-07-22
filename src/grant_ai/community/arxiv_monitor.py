"""
Grant AI - arXiv Monitor
Monitors arXiv for trending research in AI and space technology.
"""

from typing import List, Dict


class ArxivMonitor:
    """
    Monitors arXiv for new papers in specified categories and analyzes trends.
    """

    def __init__(self, categories: List[str] = None):
        self.categories = categories or ["cs.AI", "astro-ph.IM"]

    def fetch_latest_papers(self) -> List[Dict]:
        """
        Fetch latest papers from arXiv in the specified categories.
        Returns a list of paper metadata.
        """
        # Placeholder: Replace with real arXiv API logic
        return [
            {
                "title": "AI for Space Exploration",
                "authors": ["Doe, J."],
                "category": "cs.AI"
            },
            {
                "title": "Imaging Mars with ML",
                "authors": ["Smith, A."],
                "category": "astro-ph.IM"
            }
        ]

    def get_categories(self) -> List[str]:
        """
        Return the list of monitored arXiv categories.
        """
        return self.categories
