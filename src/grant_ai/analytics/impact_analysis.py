"""
Grant AI - Impact Analysis Module
Analyzes the impact of grant programs and funding on target organizations and communities.
"""

from typing import List, Dict
from grant_ai.models.organization import OrganizationProfile
from grant_ai.models.grant import Grant
from grant_ai.utils.logger import GrantAILogger


class ImpactAnalysis:
    """
    Provides methods to analyze the impact of grants on organizations and
    communities.
    """

    def __init__(self):
        pass

    def analyze_impact(
        self,
        organization: OrganizationProfile,
        grants: List[Grant]
    ) -> Dict:
        """
        Analyze the impact of grants on the given organization.
        Returns a dictionary with impact metrics and recommendations.
        """
        logger = GrantAILogger("impact_analysis")
        total_funding = sum(getattr(grant, 'amount', 0) for grant in grants)
        num_grants = len(grants)
        impact_score = min(1.0, total_funding / 1000000)
        logger.info(f"Analyzed impact for {getattr(organization, 'organization_name', str(organization))} with {num_grants} grants.")
        return {
            "organization": getattr(
                organization, 'organization_name', str(organization)
            ),
            "total_funding": total_funding,
            "num_grants": num_grants,
            "impact_score": impact_score,
            "recommendations": [
                "Increase outreach for higher impact grants.",
                "Focus on grants with proven community outcomes."
            ],
        }

    def get_metrics(self, organization: OrganizationProfile, grants: List[Grant]) -> Dict:
        """
        Return basic metrics for the organization and grants (for reporting).
        """
        return {
            "organization": getattr(organization, 'organization_name', str(organization)),
            "grant_count": len(grants),
            "total_funding": sum(getattr(grant, 'amount', 0) for grant in grants),
        }
