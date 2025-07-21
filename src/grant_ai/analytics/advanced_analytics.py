"""
Advanced Analytics for Grant AI
Provides reporting, metrics, and insights for grant discovery and application management.
"""
from typing import List, Dict
from grant_ai.models.grant import Grant
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)

class GrantAnalytics:
    """Analytics and reporting for grant discovery and applications."""
    def __init__(self):
        logger.info("Initialized GrantAnalytics.")

    def summarize_grants(self, grants: List[Grant]) -> Dict:
        """Summarize grants by domain, relevance, and funding amount."""
        summary = {
            "total": len(grants),
            "domains": {},
            "funding": 0.0,
        }
        for grant in grants:
            domain = getattr(grant, 'domain', 'other')
            summary["domains"].setdefault(domain, 0)
            summary["domains"][domain] += 1
            summary["funding"] += getattr(grant, 'amount', 0.0)
        logger.info(f"Summarized {len(grants)} grants.")
        return summary

    def generate_report(self, grants: List[Grant]) -> str:
        """Generate a text report for a list of grants."""
        summary = self.summarize_grants(grants)
        report = [f"Total grants: {summary['total']}"]
        for domain, count in summary['domains'].items():
            report.append(f"  {domain.title()}: {count}")
        report.append(f"Total funding: ${summary['funding']:,.2f}")
        logger.info("Generated grant report.")
        return "\n".join(report)
