"""
Advanced Grant Discovery API Integration
Handles NASA NSPIRES, ESA, Grants.gov, and other federal/international sources
"""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus


@dataclass
class GrantDiscoveryResult:
    """Result from grant discovery API"""
    source: str
    grants: List[Grant]
    success: bool
    message: str
    keyword_matches: List[str]


class AdvancedGrantDiscovery:
    """Advanced grant discovery with API integration and AI filtering"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36'
            )
        })
        
        # AI/Space Technology Keywords
        self.ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural networks', 'computer vision',
            'natural language processing', 'nlp', 'robotics',
            'autonomous systems', 'data science',
            'predictive analytics', 'automation', 'intelligent systems'
        ]
        
        self.space_keywords = [
            'space robotics', 'earth observation', 'satellite data',
            'space technology', 'aerospace', 'planetary science',
            'astrobiology', 'space exploration', 'orbital mechanics',
            'spacecraft', 'mission planning', 'space systems'
        ]
        
        # Grant Sources Configuration
        self.sources = {
            'nasa_nspires': {
                'name': 'NASA NSPIRES',
                'url': ('https://nspires.nasaprs.com/external/'
                       'solicitations/solicitations.do'),
                'api_endpoint': 'https://api.nasa.gov/planetary/apod',
                'keywords': self.ai_keywords + self.space_keywords,
                'type': FundingType.GRANT
            },
            'esa_open_space': {
                'name': 'ESA Open Space Innovation Platform',
                'url': 'https://ideas.esa.int/servlet/hype/IMT',
                'keywords': (['space', 'innovation', 'technology'] + 
                           self.ai_keywords),
                'type': FundingType.GRANT
            },
            'grants_gov': {
                'name': 'Grants.gov Federal Opportunities',
                'url': 'https://www.grants.gov/web/grants/search-grants.html',
                'api_endpoint': ('https://www.grants.gov/grantsws/'
                               'rest/opportunities/search/'),
                'keywords': (self.ai_keywords + 
                           ['research', 'innovation', 'technology']),
                'type': FundingType.GRANT
            },
            'nsf_ai': {
                'name': 'NSF Artificial Intelligence Programs',
                'url': 'https://www.nsf.gov/funding/programs.jsp',
                'keywords': self.ai_keywords + ['research', 'education'],
                'type': FundingType.GRANT
            },
            'doe_ai': {
                'name': 'Department of Energy AI/ML Programs',
                'url': 'https://www.energy.gov/science/funding-opportunities',
                'keywords': (self.ai_keywords + 
                           ['energy', 'climate', 'modeling']),
                'type': FundingType.GRANT
            }
        }
    
    async def discover_grants_by_keywords(self, keywords: List[str], max_results: int = 50) -> Dict[str, GrantDiscoveryResult]:
        """Discover grants across all sources using keyword filtering"""
        results = {}
        
        for source_id, source_config in self.sources.items():
            try:
                grants = await self._scrape_source_with_keywords(source_id, source_config, keywords)
                
                # Filter by keyword relevance
                relevant_grants = self._filter_grants_by_relevance(grants, keywords)
                keyword_matches = self._find_keyword_matches(relevant_grants, keywords)
                
                results[source_id] = GrantDiscoveryResult(
                    source=source_config['name'],
                    grants=relevant_grants[:max_results],
                    success=True,
                    message=f"Found {len(relevant_grants)} relevant grants",
                    keyword_matches=keyword_matches
                )
                
            except Exception as e:
                results[source_id] = GrantDiscoveryResult(
                    source=source_config['name'],
                    grants=[],
                    success=False,
                    message=f"Error: {str(e)}",
                    keyword_matches=[]
                )
        
        return results
    
    async def _scrape_source_with_keywords(self, source_id: str, source_config: Dict, keywords: List[str]) -> List[Grant]:
        """Scrape a specific source with keyword filtering"""
        
        if source_id == 'nasa_nspires':
            return await self._scrape_nasa_nspires(keywords)
        elif source_id == 'esa_open_space':
            return await self._scrape_esa_open_space(keywords)
        elif source_id == 'grants_gov':
            return await self._scrape_grants_gov(keywords)
        elif source_id == 'nsf_ai':
            return await self._scrape_nsf_ai(keywords)
        elif source_id == 'doe_ai':
            return await self._scrape_doe_ai(keywords)
        else:
            return []
    
    async def _scrape_nasa_nspires(self, keywords: List[str]) -> List[Grant]:
        """Scrape NASA NSPIRES for relevant opportunities"""
        grants = []
        
        try:
            # NASA NSPIRES current opportunities
            url = "https://nspires.nasaprs.com/external/solicitations/solicitations.do"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for solicitation listings
            solicitations = soup.find_all(['div', 'tr'], class_=re.compile(r'solicitation|opportunity'))
            
            for sol in solicitations[:20]:  # Limit to first 20 for performance
                try:
                    title_elem = sol.find(['a', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Check if title contains relevant keywords
                    if not any(keyword.lower() in title.lower() for keyword in keywords):
                        continue
                    
                    # Extract additional information
                    description = self._extract_description(sol)
                    deadline = self._extract_deadline(sol)
                    amount = self._extract_amount(sol)
                    
                    grant = Grant(
                        id=f"nasa_{id(title)}",
                        title=title,
                        description=description,
                        funder_name="NASA",
                        amount_min=amount.get('min', 0),
                        amount_max=amount.get('max', 0),
                        funding_type=FundingType.GRANT,
                        eligibility_types=[EligibilityType.NONPROFIT],
                        application_deadline=deadline.date() if deadline else None,
                        status=GrantStatus.OPEN
                    )
                    grants.append(grant)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping NASA NSPIRES: {e}")
        
        return grants
    
    async def _scrape_esa_open_space(self, keywords: List[str]) -> List[Grant]:
        """Scrape ESA Open Space Innovation Platform"""
        grants = []
        
        try:
            # ESA Innovation Portal
            url = "https://ideas.esa.int/servlet/hype/IMT"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for innovation challenges and funding opportunities
            opportunities = soup.find_all(['div', 'article'], class_=re.compile(r'challenge|opportunity|funding'))
            
            for opp in opportunities[:15]:
                try:
                    title_elem = opp.find(['h1', 'h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Filter by keywords
                    if not any(keyword.lower() in title.lower() for keyword in keywords):
                        continue
                    
                    description = self._extract_description(opp)
                    deadline = self._extract_deadline(opp)
                    
                    grant = Grant(
                        title=title,
                        description=description,
                        agency="European Space Agency (ESA)",
                        deadline=deadline,
                        amount_min=0,
                        amount_max=0,  # ESA amounts vary widely
                        funding_type=FundingType.INTERNATIONAL_GRANT,
                        eligibility_type=EligibilityType.NONPROFIT,
                        source_url=url,
                        application_url=self._extract_application_url(opp, url),
                        status=GrantStatus.OPEN,
                        tags=['ESA', 'Space Innovation', 'International']
                    )
                    grants.append(grant)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error scraping ESA Open Space: {e}")
        
        return grants
    
    async def _scrape_grants_gov(self, keywords: List[str]) -> List[Grant]:
        """Scrape Grants.gov for federal opportunities"""
        grants = []
        
        try:
            # Grants.gov search with keywords
            base_url = "https://www.grants.gov/web/grants/search-grants.html"
            search_url = f"{base_url}?keywords=" + "+".join(keywords[:3])  # Limit to 3 keywords
            
            response = self.session.get(search_url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for grant listings
            grant_listings = soup.find_all(['div', 'tr'], class_=re.compile(r'grant|opportunity|listing'))
            
            for listing in grant_listings[:25]:
                try:
                    title_elem = listing.find(['a', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract agency information
                    agency_elem = listing.find(text=re.compile(r'Agency|Department'))
                    agency = agency_elem.strip() if agency_elem else "Federal Agency"
                    
                    description = self._extract_description(listing)
                    deadline = self._extract_deadline(listing)
                    amount = self._extract_amount(listing)
                    
                    grant = Grant(
                        title=title,
                        description=description,
                        agency=agency,
                        deadline=deadline,
                        amount_min=amount.get('min', 0),
                        amount_max=amount.get('max', 0),
                        funding_type=FundingType.FEDERAL_GRANT,
                        eligibility_type=EligibilityType.NONPROFIT,
                        source_url=search_url,
                        application_url=self._extract_application_url(listing, base_url),
                        status=GrantStatus.OPEN,
                        tags=['Federal', 'Grants.gov']
                    )
                    grants.append(grant)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error scraping Grants.gov: {e}")
        
        return grants
    
    async def _scrape_nsf_ai(self, keywords: List[str]) -> List[Grant]:
        """Scrape NSF AI and technology programs"""
        grants = []
        
        try:
            # NSF Funding Programs
            url = "https://www.nsf.gov/funding/programs.jsp"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for AI-related programs
            programs = soup.find_all(['div', 'li'], text=re.compile(r'artificial intelligence|machine learning|computer science', re.I))
            
            for program in programs[:10]:
                try:
                    # Find parent container with more info
                    container = program.find_parent(['div', 'li', 'tr'])
                    if not container:
                        continue
                    
                    title_elem = container.find(['a', 'h3', 'h4'])
                    title = title_elem.get_text(strip=True) if title_elem else program.get_text(strip=True)
                    
                    description = self._extract_description(container) or "NSF research funding opportunity in AI/ML"
                    
                    grant = Grant(
                        title=title,
                        description=description,
                        agency="National Science Foundation (NSF)",
                        deadline=None,  # NSF deadlines vary
                        amount_min=50000,
                        amount_max=500000,  # Typical NSF range
                        funding_type=FundingType.FEDERAL_GRANT,
                        eligibility_type=EligibilityType.NONPROFIT,
                        source_url=url,
                        application_url=url,
                        status=GrantStatus.OPEN,
                        tags=['NSF', 'AI', 'Research', 'Technology']
                    )
                    grants.append(grant)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error scraping NSF AI programs: {e}")
        
        return grants
    
    async def _scrape_doe_ai(self, keywords: List[str]) -> List[Grant]:
        """Scrape Department of Energy AI/ML programs"""
        grants = []
        
        try:
            # DOE Science funding opportunities
            url = "https://www.energy.gov/science/funding-opportunities"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for AI/ML related opportunities
            opportunities = soup.find_all(['div', 'article'], class_=re.compile(r'opportunity|funding'))
            
            for opp in opportunities[:10]:
                try:
                    title_elem = opp.find(['h2', 'h3', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Check for AI/ML relevance
                    if not any(keyword.lower() in title.lower() for keyword in self.ai_keywords):
                        continue
                    
                    description = self._extract_description(opp)
                    deadline = self._extract_deadline(opp)
                    
                    grant = Grant(
                        title=title,
                        description=description,
                        agency="U.S. Department of Energy",
                        deadline=deadline,
                        amount_min=100000,
                        amount_max=2000000,  # DOE grants can be substantial
                        funding_type=FundingType.FEDERAL_GRANT,
                        eligibility_type=EligibilityType.NONPROFIT,
                        source_url=url,
                        application_url=self._extract_application_url(opp, url),
                        status=GrantStatus.OPEN,
                        tags=['DOE', 'Energy', 'AI', 'Research']
                    )
                    grants.append(grant)
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error scraping DOE AI programs: {e}")
        
        return grants
    
    def _filter_grants_by_relevance(self, grants: List[Grant], keywords: List[str]) -> List[Grant]:
        """Filter grants by keyword relevance scoring"""
        scored_grants = []
        
        for grant in grants:
            score = 0
            text_content = f"{grant.title} {grant.description}".lower()
            
            # Score based on keyword matches
            for keyword in keywords:
                if keyword.lower() in text_content:
                    score += 1
            
            # Bonus scoring for AI/space technology terms
            for ai_term in self.ai_keywords:
                if ai_term.lower() in text_content:
                    score += 2
            
            for space_term in self.space_keywords:
                if space_term.lower() in text_content:
                    score += 1.5
            
            # Only include grants with some relevance
            if score > 0:
                grant.relevance_score = score
                scored_grants.append(grant)
        
        # Sort by relevance score (highest first)
        return sorted(scored_grants, key=lambda g: getattr(g, 'relevance_score', 0), reverse=True)
    
    def _find_keyword_matches(self, grants: List[Grant], keywords: List[str]) -> List[str]:
        """Find which keywords had matches in the grants"""
        matches = set()
        
        for grant in grants:
            text_content = f"{grant.title} {grant.description}".lower()
            for keyword in keywords:
                if keyword.lower() in text_content:
                    matches.add(keyword)
        
        return list(matches)
    
    def _extract_description(self, element) -> str:
        """Extract description from HTML element"""
        # Look for description in various elements
        desc_selectors = [
            'p', '.description', '.summary', '.abstract',
            '.content', '.details', '[class*="desc"]'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 50:  # Reasonable description length
                    return desc_text[:500]  # Limit to 500 chars
        
        # Fallback to element text
        return element.get_text(strip=True)[:300] if element else ""
    
    def _extract_deadline(self, element) -> Optional[datetime]:
        """Extract deadline from HTML element"""
        # Look for date patterns
        date_patterns = [
            r'deadline[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'due[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'closes[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        text = element.get_text() if element else ""
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse the date
                    from dateutil import parser
                    return parser.parse(date_str)
                except:
                    continue
        
        return None
    
    def _extract_amount(self, element) -> Dict[str, int]:
        """Extract funding amount from HTML element"""
        # Look for amount patterns
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+)\s*(?:USD|dollars)',
            r'up to \$([0-9,]+)',
            r'maximum \$([0-9,]+)'
        ]
        
        text = element.get_text() if element else ""
        amounts = []
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Clean and convert to int
                    amount_str = match.replace(',', '')
                    amount = int(float(amount_str))
                    amounts.append(amount)
                except:
                    continue
        
        if amounts:
            return {'min': min(amounts), 'max': max(amounts)}
        
        return {'min': 0, 'max': 0}
    
    def _extract_application_url(self, element, base_url: str) -> str:
        """Extract application URL from HTML element"""
        # Look for application links
        link_texts = ['apply', 'application', 'submit', 'proposal', 'solicitation']
        
        for link_text in link_texts:
            link = element.find('a', text=re.compile(link_text, re.IGNORECASE))
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('http'):
                    return href
                else:
                    from urllib.parse import urljoin
                    return urljoin(base_url, href)
        
        # Fallback to first link
        first_link = element.find('a')
        if first_link and first_link.get('href'):
            href = first_link.get('href')
            if href.startswith('http'):
                return href
            else:
                from urllib.parse import urljoin
                return urljoin(base_url, href)
        
        return base_url


# Integration with existing grant discovery system
class EnhancedGrantDiscovery:
    """Enhanced grant discovery with advanced API integration"""
    
    def __init__(self):
        self.advanced_discovery = AdvancedGrantDiscovery()
    
    async def discover_ai_space_grants(self, organization_keywords: List[str] = None) -> Dict[str, GrantDiscoveryResult]:
        """Discover AI and space technology grants"""
        
        # Default keywords if none provided
        if not organization_keywords:
            organization_keywords = [
                'artificial intelligence', 'machine learning', 'robotics',
                'space technology', 'data science', 'automation'
            ]
        
        return await self.advanced_discovery.discover_grants_by_keywords(organization_keywords)
    
    def get_discovery_summary(self, results: Dict[str, GrantDiscoveryResult]) -> Dict:
        """Get summary of discovery results"""
        total_grants = sum(len(result.grants) for result in results.values() if result.success)
        successful_sources = [result.source for result in results.values() if result.success]
        failed_sources = [result.source for result in results.values() if not result.success]
        
        all_keywords = set()
        for result in results.values():
            all_keywords.update(result.keyword_matches)
        
        return {
            'total_grants': total_grants,
            'successful_sources': successful_sources,
            'failed_sources': failed_sources,
            'matched_keywords': list(all_keywords),
            'source_count': len(results),
            'success_rate': len(successful_sources) / len(results) if results else 0
        }
