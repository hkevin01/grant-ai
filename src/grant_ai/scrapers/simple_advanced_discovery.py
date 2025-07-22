"""
Simple Advanced Grant Discovery Test
Basic implementation for testing the new discovery features
Includes robust error handling and logging.
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import logging

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
from grant_ai.scrapers.nsf_grants import discover_nsf_grants
from grant_ai.scrapers.doe_grants import discover_doe_grants
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SimpleGrantResult:
    """Simple result from grant discovery."""
    source: str
    grants: List[Grant]
    success: bool
    message: str


class SimpleAdvancedDiscovery:
    """Discovers AI and space technology grants from advanced sources."""
    
    def __init__(self):
        # Sample grants for different sources
        self.sample_grants = {
            'nasa': [
                {
                    'title': 'NASA STTR: AI for Autonomous Spacecraft Navigation',
                    'description': 'Develop machine learning algorithms for autonomous spacecraft navigation and mission planning.',
                    'funder': 'NASA STTR Program',
                    'amount_min': 750000,
                    'amount_max': 1500000
                },
                {
                    'title': 'NASA SBIR: Computer Vision for Mars Exploration',
                    'description': 'Advanced computer vision and AI techniques for Mars rover navigation and scientific discovery.',
                    'funder': 'NASA SBIR Program',
                    'amount_min': 500000,
                    'amount_max': 1000000
                }
            ],
            'esa': [
                {
                    'title': 'ESA Discovery: Onboard AI Processing for Earth Observation',
                    'description': 'Edge computing and AI for real-time processing of Earth observation satellite data.',
                    'funder': 'European Space Agency',
                    'amount_min': 300000,
                    'amount_max': 800000
                }
            ],
            'nsf': [
                {
                    'title': 'NSF AI Institute: Foundations of Machine Learning',
                    'description': 'Research in fundamental machine learning algorithms and their applications.',
                    'funder': 'National Science Foundation',
                    'amount_min': 1000000,
                    'amount_max': 5000000
                },
                {
                    'title': 'NSF CISE: AI for Scientific Discovery',
                    'description': 'Artificial intelligence applications in scientific research and discovery.',
                    'funder': 'NSF Computer and Information Science',
                    'amount_min': 200000,
                    'amount_max': 500000
                }
            ],
            'doe': [
                {
                    'title': 'DOE AI for Climate Modeling',
                    'description': 'Machine learning approaches for climate prediction and energy systems.',
                    'funder': 'Department of Energy',
                    'amount_min': 800000,
                    'amount_max': 2000000
                }
            ]
        }
        logger.info("Initialized SimpleAdvancedDiscovery with sample grants.")

    def discover_ai_space_grants(self, keywords: List[str] = None) -> Dict[str, SimpleGrantResult]:
        """Discover grants related to AI and space technology using sample data."""
        
        results = {}
        for source, grants in self.sample_grants.items():
            try:
                filtered = [Grant(**g) for g in grants if any(k.lower() in g['title'].lower() for k in keywords)]
                results[source] = SimpleGrantResult(
                    source=source,
                    grants=filtered,
                    success=True,
                    message=f"Found {len(filtered)} grants."
                )
                logger.info(f"{source}: Found {len(filtered)} grants for keywords {keywords}.")
            except Exception as e:
                logger.error(f"Error discovering grants for source {source}: {e}")
                results[source] = SimpleGrantResult(
                    source=source,
                    grants=[],
                    success=False,
                    message=str(e)
                )
        
        return results

    def _search_source(self, source: str, keywords: List[str]) -> Dict:
        """Stub for searching a source."""
        logger.info(f"Searching {source} for keywords: {keywords}")
        return {
            'source': source,
            'success': True,
            'grants': [{'title': f'Sample {source} grant', 'domain': 'ai', 'confidence': 0.9}],
            'message': 'Search completed'
        }

    def get_discovery_summary(self, results: dict) -> dict:
        """Return summary of discovery results."""
        total_grants = sum(len(r.grants) for r in results.values() if hasattr(r, 'grants'))
        successful_sources = [k for k, r in results.items() if getattr(r, 'success', False)]
        success_rate = len(successful_sources) / max(1, len(results))
        return {
            'total_grants': total_grants,
            'successful_sources': successful_sources,
            'success_rate': success_rate
        }


class SimpleEnhancedGrantDiscovery(SimpleAdvancedDiscovery):
    """Enhanced version for advanced grant discovery with additional analytics."""
    
    def __init__(self):
        super().__init__()
        logger.info("Initialized SimpleEnhancedGrantDiscovery.")

    def discover_and_analyze(self, keywords: List[str]) -> Dict:
        """Discover grants and return analytics summary."""
        results = self.discover_ai_space_grants(keywords)
        all_grants = []
        for r in results.values():
            if r.success:
                all_grants.extend(r.grants)
        from grant_ai.analytics.advanced_analytics import GrantAnalytics
        analytics = GrantAnalytics()
        summary = analytics.summarize_grants(all_grants)
        return {
            "results": results,
            "analytics": summary,
        }
