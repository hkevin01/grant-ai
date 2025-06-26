"""
AI-powered grant discovery agent for finding new grant opportunities.
Uses web search APIs and intelligent parsing to discover grants.
"""
import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
from grant_ai.models.organization import OrganizationProfile


class AIGrantAgent:
    """AI-powered agent for discovering grant opportunities."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Grant sources configuration
        self.sources = {
            'federal': {
                'grants_gov': 'https://www.grants.gov/api/v1/opportunities',
                'usaspending': 'https://api.usaspending.gov/api/v2/search/spending_by_award/',
            },
            'west_virginia': {
                'wv_gov': 'https://www.wv.gov/Pages/default.aspx',
                'wv_education': 'https://wvde.us/',
                'wv_arts': 'https://www.wvculture.org/arts/',
                'wv_development': 'https://www.wvcommerce.org/',
            },
            'foundations': {
                'benedum': 'https://benedum.org/grants/',
                'candid': 'https://candid.org/',
                'foundation_center': 'https://foundationcenter.org/',
            }
        }
    
    def search_grants_for_profile(self, profile: OrganizationProfile) -> List[Grant]:
        """Search for grants matching an organization profile."""
        grants = []
        
        # Generate search queries based on profile
        search_queries = self._generate_search_queries(profile)
        
        for query in search_queries:
            print(f"🔍 Searching for: {query}")
            
            # Search different sources
            grants.extend(self._search_web(query))
            grants.extend(self._search_grants_gov(query))
            grants.extend(self._search_wv_sources(query))
            
            # Avoid rate limiting
            time.sleep(1)
        
        # Remove duplicates and return
        unique_grants = self._deduplicate_grants(grants)
        return unique_grants
    
    def _generate_search_queries(self, profile: OrganizationProfile) -> List[str]:
        """Generate search queries based on organization profile."""
        queries = []
        
        # Basic queries from focus areas and location
        base_terms = []
        if profile.focus_areas:
            base_terms.extend([str(area).replace('_', ' ') for area in profile.focus_areas])
        if profile.location:
            base_terms.append(profile.location)
        
        # Enhanced queries using comprehensive profile information
        if base_terms:
            # Core organization queries
            queries.append(f"{' '.join(base_terms[:3])} grants West Virginia")
            queries.append(f"{' '.join(base_terms[:3])} funding opportunities nonprofit")
            queries.append(f"education grants {profile.location}")
            queries.append(f"youth development grants West Virginia")
            queries.append(f"arts education funding {profile.location}")
            
            # Appalachian and regional queries
            if hasattr(profile, 'region') and 'appalachian' in profile.region.lower():
                queries.append(f"Appalachian youth development grants")
                queries.append(f"Appalachian community grants West Virginia")
                queries.append(f"rural youth programs funding Appalachian")
            
            # Specific program queries
            if hasattr(profile, 'key_programs') and profile.key_programs:
                for program in profile.key_programs[:3]:  # Use top 3 programs
                    queries.append(f"{program} grants West Virginia")
                    queries.append(f"{program} funding opportunities")
            
            # Target demographic queries
            if hasattr(profile, 'target_demographics') and profile.target_demographics:
                for demo in profile.target_demographics[:3]:  # Use top 3 demographics
                    if 'youth' in demo.lower() or 'children' in demo.lower():
                        queries.append(f"{demo} development grants West Virginia")
                    elif 'family' in demo.lower():
                        queries.append(f"family support grants West Virginia")
                    elif 'addiction' in demo.lower():
                        queries.append(f"addiction prevention youth grants")
                        queries.append(f"substance abuse prevention funding")
            
            # Crisis and prevention queries
            if any('crisis' in str(area).lower() or 'prevention' in str(area).lower() for area in profile.focus_areas):
                queries.append(f"youth crisis intervention grants")
                queries.append(f"drug prevention programs funding")
                queries.append(f"substance abuse prevention youth grants")
            
            # Arts and creativity queries
            if any('art' in str(area).lower() or 'creative' in str(area).lower() for area in profile.focus_areas):
                queries.append(f"arts integration education grants")
                queries.append(f"fine arts education funding West Virginia")
                queries.append(f"creative arts youth programs")
            
            # Robotics and STEM queries
            if any('robotics' in str(area).lower() or 'stem' in str(area).lower() for area in profile.focus_areas):
                queries.append(f"robotics education grants West Virginia")
                queries.append(f"STEM youth programs funding")
                queries.append(f"competitive robotics team grants")
            
            # Outdoor and recreation queries
            if hasattr(profile, 'offerings') and profile.offerings:
                if any('outdoor' in offering.lower() or 'recreation' in offering.lower() for offering in profile.offerings):
                    queries.append(f"outdoor recreation youth grants")
                    queries.append(f"nature education programs funding")
        
        # Federal queries with enhanced targeting
        queries.extend([
            "federal education grants West Virginia",
            "federal youth development funding Appalachian",
            "federal arts education grants rural communities",
            "federal nonprofit grants West Virginia",
            "federal drug prevention youth programs",
            "federal family support grants rural areas",
            "federal after-school programs funding",
            "federal summer camp grants nonprofit"
        ])
        
        # State-specific queries
        if hasattr(profile, 'state') and profile.state:
            queries.extend([
                f"{profile.state} education grants nonprofit",
                f"{profile.state} youth development funding",
                f"{profile.state} arts education grants",
                f"{profile.state} community development grants"
            ])
        
        # County-specific queries
        if hasattr(profile, 'county') and profile.county:
            queries.extend([
                f"{profile.county} County youth grants",
                f"{profile.county} County education funding",
                f"{profile.county} County community grants"
            ])
        
        # Mission-specific queries
        if hasattr(profile, 'mission_statement') and profile.mission_statement:
            mission_keywords = profile.mission_statement.lower().split()
            key_words = [word for word in mission_keywords if len(word) > 4 and word not in ['through', 'their', 'with', 'that', 'this', 'they', 'have', 'will']]
            if key_words:
                queries.append(f"{' '.join(key_words[:3])} grants West Virginia")
        
        return queries[:8]  # Limit to top 8 queries for better performance
    
    def _search_web(self, query: str) -> List[Grant]:
        """Search the web for grant opportunities."""
        grants = []
        
        try:
            # Use DuckDuckGo Instant Answer API (no API key required)
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract information from DuckDuckGo results
                if data.get('Abstract'):
                    grant = self._parse_web_result(data, query)
                    if grant:
                        grants.append(grant)
                
                # Also search related topics
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        grant = self._parse_web_result(topic, query)
                        if grant:
                            grants.append(grant)
            
        except Exception as e:
            print(f"Error searching web for '{query}': {e}")
        
        return grants
    
    def _search_grants_gov(self, query: str) -> List[Grant]:
        """Search Grants.gov API for federal grants."""
        grants = []
        
        try:
            # Note: This would require an API key in production
            # For now, we'll simulate with sample data
            sample_grants = self._get_sample_federal_grants(query)
            grants.extend(sample_grants)
            
        except Exception as e:
            print(f"Error searching Grants.gov for '{query}': {e}")
        
        return grants
    
    def _search_wv_sources(self, query: str) -> List[Grant]:
        """Search West Virginia-specific grant sources."""
        grants = []
        
        try:
            # Search WV government sites
            wv_grants = self._get_sample_wv_grants(query)
            grants.extend(wv_grants)
            
        except Exception as e:
            print(f"Error searching WV sources for '{query}': {e}")
        
        return grants
    
    def _parse_web_result(self, data: Dict, query: str) -> Optional[Grant]:
        """Parse web search result into a Grant object."""
        try:
            title = data.get('Title', '') or data.get('Text', '')[:100]
            description = data.get('Abstract', '') or data.get('Text', '')
            
            if not title or not description:
                return None
            
            # Extract grant information using regex patterns
            amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:,\d{3})*)', description)
            amount = None
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            
            # Determine eligibility
            eligibility = []
            if any(word in description.lower() for word in ['nonprofit', '501c3', 'charitable']):
                eligibility.append(EligibilityType.NONPROFIT)
            if any(word in description.lower() for word in ['education', 'school', 'academic']):
                eligibility.append(EligibilityType.EDUCATION)
            
            # Determine focus areas
            focus_areas = []
            if any(word in description.lower() for word in ['education', 'learning', 'academic']):
                focus_areas.append('education')
            if any(word in description.lower() for word in ['art', 'arts', 'creative']):
                focus_areas.append('art_education')
            if any(word in description.lower() for word in ['youth', 'children', 'student']):
                focus_areas.append('youth_development')
            
            return Grant(
                id=f"ai_web_{int(time.time())}_{hash(title) % 10000}",
                title=title[:200],
                description=description[:1000],
                funder_name="Web Search Result",
                funder_type="Unknown",
                funding_type=FundingType.GRANT,
                amount_typical=amount,
                amount_min=amount,
                amount_max=amount * 1.5 if amount else None,
                status=GrantStatus.OPEN,
                eligibility_types=eligibility,
                focus_areas=focus_areas,
                source="AI Web Search",
                source_url=data.get('FirstURL', ''),
                contact_email=None,
                contact_phone=None,
                application_url=data.get('FirstURL', ''),
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Error parsing web result: {e}")
            return None
    
    def _get_sample_federal_grants(self, query: str) -> List[Grant]:
        """Get sample federal grants (in production, this would use real API)."""
        return [
            Grant(
                id="fed_001",
                title="21st Century Community Learning Centers",
                description="Federal funding for after-school and summer learning programs that support student academic achievement.",
                funder_name="U.S. Department of Education",
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=50000,
                amount_max=2000000,
                amount_typical=500000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'youth_development', 'after_school'],
                source="Grants.gov",
                source_url="https://www.grants.gov/web/grants/view-opportunity.html?oppId=12345",
                contact_email="grants@ed.gov",
                contact_phone="202-555-0123",
                application_url="https://www.grants.gov/web/grants/view-opportunity.html?oppId=12345",
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="fed_002",
                title="Arts Education Partnership Grants",
                description="Supporting arts education programs in schools and communities.",
                funder_name="National Endowment for the Arts",
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=10000,
                amount_max=100000,
                amount_typical=50000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['art_education', 'education'],
                source="Grants.gov",
                source_url="https://www.grants.gov/web/grants/view-opportunity.html?oppId=67890",
                contact_email="grants@arts.gov",
                contact_phone="202-555-0124",
                application_url="https://www.grants.gov/web/grants/view-opportunity.html?oppId=67890",
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _get_sample_wv_grants(self, query: str) -> List[Grant]:
        """Get sample West Virginia grants."""
        return [
            Grant(
                id="wv_001",
                title="West Virginia Arts Commission Grant",
                description="Supporting arts education and cultural programs in West Virginia communities.",
                funder_name="West Virginia Arts Commission",
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=1000,
                amount_max=10000,
                amount_typical=5000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['art_education', 'education'],
                source="WV Arts Commission",
                source_url="https://www.wvculture.org/arts/grants/",
                contact_email="arts@wvculture.org",
                contact_phone="304-558-0220",
                application_url="https://www.wvculture.org/arts/grants/",
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_002",
                title="Benedum Foundation Education Grant",
                description="Supporting innovative education programs in West Virginia and southwestern Pennsylvania.",
                funder_name="Claude Worthington Benedum Foundation",
                funder_type="Private Foundation",
                funding_type=FundingType.GRANT,
                amount_min=25000,
                amount_max=500000,
                amount_typical=100000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['education', 'youth_development'],
                source="Benedum Foundation",
                source_url="https://benedum.org/grants/",
                contact_email="info@benedum.org",
                contact_phone="412-288-0360",
                application_url="https://benedum.org/grants/",
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _deduplicate_grants(self, grants: List[Grant]) -> List[Grant]:
        """Remove duplicate grants based on title and funder."""
        seen = set()
        unique_grants = []
        
        for grant in grants:
            key = (grant.title.lower(), grant.funder_name.lower())
            if key not in seen:
                seen.add(key)
                unique_grants.append(grant)
        
        return unique_grants


def discover_grants_for_profile(profile: OrganizationProfile) -> List[Grant]:
    """Convenience function to discover grants for a profile."""
    agent = AIGrantAgent()
    return agent.search_grants_for_profile(profile)


if __name__ == "__main__":
    # Test the agent
    from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType

    # Create a test profile
    test_profile = OrganizationProfile(
        name="Test Organization",
        description="Test organization for grant discovery",
        focus_areas=[FocusArea.EDUCATION, FocusArea.ART_EDUCATION],
        program_types=[ProgramType.AFTER_SCHOOL, ProgramType.SUMMER_CAMPS],
        location="West Virginia",
        contact_name="Test Contact",
        contact_email="test@example.com",
        contact_phone="555-123-4567"
    )
    
    # Discover grants
    agent = AIGrantAgent()
    grants = agent.search_grants_for_profile(test_profile)
    
    print(f"Found {len(grants)} grants:")
    for grant in grants:
        print(f"- {grant.title} ({grant.funder_name}) - ${grant.amount_typical:,}") 