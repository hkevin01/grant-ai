"""
NSF Grant Scraper for Grant AI
"""
from typing import List, Dict
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)

def discover_nsf_grants(keywords: List[str]) -> List[Dict]:
    """
    Discover NSF grants matching keywords.

    Args:
        keywords (List[str]): List of keywords to match.

    Returns:
        List[Dict]: List of matching NSF grants.
    """
    try:
        # Simulated NSF grant data
        sample_grants = [
            {"title": "NSF AI Research Program", "description": "AI for science.", "status": "open"},
            {"title": "NSF STEM Education Grant", "description": "STEM outreach.", "status": "awarded"},
        ]
        results = [g for g in sample_grants if any(k.lower() in g["title"].lower() for k in keywords)]
        logger.info(f"NSF grants discovered: {len(results)} for keywords: {keywords}")
        return results
    except Exception as e:
        logger.error(f"Error discovering NSF grants: {e}")
        return []
