"""
Analytics dashboard module for Grant Research AI.
"""

from typing import List, Dict

class AnalyticsDashboard:
    """Analytics dashboard for grant and organization metrics."""
    def __init__(self):
        self.metrics = {}
    def summarize_grants(self, grants: List[dict]) -> Dict:
        """Summarize grant statistics for dashboard."""
        total = len(grants)
        by_type = {}
        for grant in grants:
            gtype = grant.get('funding_type', 'unknown')
            by_type[gtype] = by_type.get(gtype, 0) + 1
        return {'total_grants': total, 'by_type': by_type}
    def generate_report(self, grants: List[dict]) -> str:
        """Generate a text report for grants analytics."""
        summary = self.summarize_grants(grants)
        lines = [f"Total grants: {summary['total_grants']}"]
        for gtype, count in summary['by_type'].items():
            lines.append(f"{gtype}: {count}")
        return '\n'.join(lines)
