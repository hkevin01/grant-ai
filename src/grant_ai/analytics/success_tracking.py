"""
Success Rate Analytics
Tracks and analyzes grant application success rates and related metrics.
"""
from typing import List, Dict

class SuccessRateAnalytics:
    """Tracks and analyzes grant application success rates."""
    def __init__(self):
        self.records: List[Dict] = []
    def add_record(self, org_id: str, grant_id: str, status: str, amount: float):
        """Add a record for a grant application."""
        self.records.append({
            'org_id': org_id,
            'grant_id': grant_id,
            'status': status,
            'amount': amount
        })
    def get_success_rate(self, org_id: str = None) -> float:
        """Calculate success rate for all or a specific organization."""
        filtered = self.records if org_id is None else [r for r in self.records if r['org_id'] == org_id]
        total = len(filtered)
        won = sum(1 for r in filtered if r['status'] == 'awarded')
        return (won / total) if total > 0 else 0.0
    def get_total_funding(self, org_id: str = None) -> float:
        """Calculate total funding awarded."""
        filtered = self.records if org_id is None else [r for r in self.records if r['org_id'] == org_id and r['status'] == 'awarded']
        return sum(r['amount'] for r in filtered)
