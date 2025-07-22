"""
Grant AI - Enhanced Proposal Generator
Generates grant proposals aligned with NASA, ESA, and AI best practices.
"""

from typing import Dict, Any
from grant_ai.models.organization import OrganizationProfile
from grant_ai.models.grant import Grant
from grant_ai.utils.logger import GrantAILogger


class EnhancedProposalGenerator:
    """
    Generates enhanced grant proposals with domain-specific templates and
    responsible AI alignment.
    """

    def __init__(self):
        pass

    def generate_proposal(
        self,
        organization: OrganizationProfile,
        grant: Grant,
        template: str = "nasa"
    ) -> Dict[str, Any]:
        """
        Generate a proposal for the given organization and grant using the
        specified template.
        """
        logger = GrantAILogger("proposal_generator")
        proposal = {
            "title": (
                getattr(organization, 'organization_name', str(organization)) +
                " Proposal for " + getattr(grant, 'title', str(grant))
            ),
            "summary": (
                f"This proposal aligns with {template.upper()} requirements "
                "and responsible AI practices."
            ),
            "objectives": ["Advance STEM education", "Promote responsible AI"],
            "budget": getattr(grant, 'amount', None),
            "template": template,
        }
        logger.info(f"Generated proposal for {proposal['title']}")
        return proposal

    def get_supported_templates(self) -> list:
        """
        Return a list of supported proposal templates.
        """
        return ["nasa", "esa", "ai_responsible"]
