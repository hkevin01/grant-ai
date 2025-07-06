"""
Simple OpenGrants Platform Integration
Simplified version for testing platform integrations.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from grant_ai.integrations import IntegrationResult, PlatformIntegration
from grant_ai.models import FundingType, Grant, GrantStatus


class SimpleOpenGrantsIntegration(PlatformIntegration):
    """Simple integration with OpenGrants platform for testing."""
    
    def __init__(self):
        super().__init__("simple_open_grants", enabled=True)
        
    async def discover_grants(
        self, organization, criteria: Dict[str, Any]
    ) -> IntegrationResult:
        """
        Discover grants from simplified OpenGrants platform.
        
        Args:
            organization: Organization profile
            criteria: Search criteria
            
        Returns:
            Integration result with discovered grants
        """
        try:
            # Create sample grants for testing
            grants = [
                Grant(
                    id=f"og-{uuid.uuid4().hex[:8]}",
                    title="Community Education Excellence Grant",
                    funder_name="National Education Foundation",
                    funder_type="foundation",
                    funding_type=FundingType.GRANT,
                    description="Supporting innovative education programs.",
                    amount_min=25000,
                    amount_max=100000,
                    amount_typical=None,
                    total_funding_available=None,
                    status=GrantStatus.OPEN,
                    application_deadline=(
                        datetime.now() + timedelta(days=45)
                    ).date(),
                    decision_date=None,
                    funding_start_date=None,
                    funding_duration_months=None,
                    focus_areas=['education', 'community impact'],
                    matching_funds_required=False,
                    matching_percentage=None,
                    application_url=None,
                    information_url=None,
                    contact_email=None,
                    contact_phone=None,
                    source="OpenGrants",
                    source_url=None,
                    relevance_score=None
                ),
                Grant(
                    id=f"og-{uuid.uuid4().hex[:8]}",
                    title="Youth Leadership Development Initiative",
                    funder_name="Community Foundation Collaborative",
                    funder_type="foundation",
                    funding_type=FundingType.GRANT,
                    description="Empowering young leaders through mentorship.",
                    amount_min=10000,
                    amount_max=50000,
                    amount_typical=None,
                    total_funding_available=None,
                    status=GrantStatus.OPEN,
                    application_deadline=(
                        datetime.now() + timedelta(days=30)
                    ).date(),
                    decision_date=None,
                    funding_start_date=None,
                    funding_duration_months=None,
                    focus_areas=['youth development', 'leadership'],
                    matching_funds_required=False,
                    matching_percentage=None,
                    application_url=None,
                    information_url=None,
                    contact_email=None,
                    contact_phone=None,
                    source="OpenGrants",
                    source_url=None,
                    relevance_score=None
                )
            ]
            
            return IntegrationResult(
                platform=self.name,
                grants=grants,
                success=True,
                message=f"Found {len(grants)} grants from OpenGrants",
                timestamp=datetime.now(),
                confidence_score=0.85
            )
            
        except Exception as e:
            return IntegrationResult(
                platform=self.name,
                grants=[],
                success=False,
                message=f"Error: {str(e)}",
                timestamp=datetime.now(),
                confidence_score=0.0
            )
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get information about this platform."""
        return {
            "name": self.name,
            "description": "Simple OpenGrants integration for testing",
            "supported_features": ["grant_discovery", "filtering"],
            "rate_limits": {"requests_per_hour": 100},
            "authentication_required": False,
            "data_freshness": "Daily updates"
        }
