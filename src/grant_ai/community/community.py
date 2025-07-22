"""
Community features for Grant AI.
"""
from typing import List, Dict


def get_community_signals() -> List[str]:
    """Fetch community signals (e.g., trending topics, arXiv papers)."""
    # Example: return static trending topics
    return [
        "AI for Social Good",
        "Space Robotics",
        "Affordable Housing Innovation",
        "STEM Education Outreach",
    ]


class CommunitySignalIntegrator:
    """Integrate community signals for grant insights."""
    def __init__(self):
        self.sources: List[str] = ["arXiv", "NASA", "ESA", "user_feedback"]

    def fetch_signals(self, keywords: List[str]) -> Dict[str, List[Dict]]:
        # Placeholder: simulate fetching signals
        results = {}
        for source in self.sources:
            results[source] = [{"keyword": kw, "signal": f"Insight from {source}"} for kw in keywords]
        return results
