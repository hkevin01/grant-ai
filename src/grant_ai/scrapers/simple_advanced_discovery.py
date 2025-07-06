"""
Simple Advanced Grant Discovery Test
Basic implementation for testing the new discovery features
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus


@dataclass
class SimpleGrantResult:
    """Simple result from grant discovery"""
    source: str
    grants: List[Grant]
    success: bool
    message: str


class SimpleAdvancedDiscovery:
    """Simple version for testing advanced grant discovery"""
    
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
    
    def discover_ai_space_grants(self, keywords: List[str] = None) -> Dict[str, SimpleGrantResult]:
        """Discover AI and space technology grants (simplified)"""
        
        results = {}
        
        # NASA grants
        nasa_grants = self._create_grants_from_samples('nasa')
        results['nasa_nspires'] = SimpleGrantResult(
            source='NASA NSPIRES',
            grants=nasa_grants,
            success=True,
            message=f"Found {len(nasa_grants)} NASA grants"
        )
        
        # ESA grants
        esa_grants = self._create_grants_from_samples('esa')
        results['esa_open_space'] = SimpleGrantResult(
            source='ESA Open Space Innovation',
            grants=esa_grants,
            success=True,
            message=f"Found {len(esa_grants)} ESA grants"
        )
        
        # NSF grants
        nsf_grants = self._create_grants_from_samples('nsf')
        results['nsf_ai'] = SimpleGrantResult(
            source='NSF AI Programs',
            grants=nsf_grants,
            success=True,
            message=f"Found {len(nsf_grants)} NSF grants"
        )
        
        # DOE grants
        doe_grants = self._create_grants_from_samples('doe')
        results['doe_ai'] = SimpleGrantResult(
            source='DOE AI Programs',
            grants=doe_grants,
            success=True,
            message=f"Found {len(doe_grants)} DOE grants"
        )
        
        return results
    
    def _create_grants_from_samples(self, source: str) -> List[Grant]:
        """Create Grant objects from sample data"""
        grants = []
        
        for sample in self.sample_grants.get(source, []):
            try:
                grant = Grant(
                    id=str(uuid.uuid4()),
                    title=sample['title'],
                    description=sample['description'],
                    funder_name=sample['funder'],
                    amount_min=sample.get('amount_min', 0),
                    amount_max=sample.get('amount_max', 0),
                    funding_type=FundingType.GRANT,
                    eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.RESEARCH],
                    status=GrantStatus.OPEN
                )
                # Add relevance score for testing
                grant.relevance_score = 8.5  # High relevance
                grants.append(grant)
            except Exception as e:
                print(f"Error creating grant: {e}")
                continue
        
        return grants
    
    def get_discovery_summary(self, results: Dict[str, SimpleGrantResult]) -> Dict:
        """Get summary of discovery results"""
        total_grants = sum(len(result.grants) for result in results.values() if result.success)
        successful_sources = [result.source for result in results.values() if result.success]
        failed_sources = [result.source for result in results.values() if not result.success]
        
        # Sample keywords for demo
        matched_keywords = ['artificial intelligence', 'machine learning', 'space technology', 'robotics']
        
        return {
            'total_grants': total_grants,
            'successful_sources': successful_sources,
            'failed_sources': failed_sources,
            'matched_keywords': matched_keywords,
            'source_count': len(results),
            'success_rate': len(successful_sources) / len(results) if results else 0
        }


class SimpleEnhancedGrantDiscovery:
    """Enhanced grant discovery with simple implementation"""
    
    def __init__(self):
        self.advanced_discovery = SimpleAdvancedDiscovery()
    
    def discover_ai_space_grants(self, organization_keywords: List[str] = None):
        """Discover AI and space technology grants"""
        return self.advanced_discovery.discover_ai_space_grants(organization_keywords)
    
    def get_discovery_summary(self, results):
        """Get summary of discovery results"""
        return self.advanced_discovery.get_discovery_summary(results)
