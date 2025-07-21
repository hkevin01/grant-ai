"""
Analytics module for Grant AI.
"""
from typing import List, Dict
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_grant_success(grants: List[Dict]) -> Dict:
    """
    Analyze grant success metrics.

    Args:
        grants (List[Dict]): List of grant dictionaries.

    Returns:
        Dict: Analysis results with total, successful, and success rate.
    """
    try:
        total = len(grants)
        successful = sum(1 for g in grants if g.get("status") == "awarded")
        success_rate = successful / total if total else 0.0
        logger.info(f"Analyzed {total} grants, {successful} successful.")
        return {
            "total": total,
            "successful": successful,
            "success_rate": success_rate,
        }
    except Exception as e:
        logger.error(f"Error analyzing grants: {e}")
        return {"total": 0, "successful": 0, "success_rate": 0.0}
