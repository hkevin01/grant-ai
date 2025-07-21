"""
DOE Grant Scraper for Grant AI
"""
from typing import List, Dict
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)

def discover_doe_grants(keywords: List[str]) -> List[Dict]:
    """
    Discover DOE grants matching keywords.
    
    Args:
        keywords (List[str]): List of keywords to match.
        
    Returns:
        List[Dict]: List of matching DOE grants.
    """
    try:
        # Simulated DOE grant data
        sample_grants = [
            {"title": "DOE Energy AI Initiative", "description": "AI for energy.", "status": "open"},
            {"title": "DOE Robotics Grant", "description": "Robotics for energy.", "status": "awarded"},
        ]
        results = [g for g in sample_grants if any(k.lower() in g["title"].lower() for k in keywords)]
        logger.info(f"DOE grants discovered: {len(results)} for keywords: {keywords}")
        return results
    except Exception as e:
        logger.error(f"Error discovering DOE grants: {e}")
        return []
