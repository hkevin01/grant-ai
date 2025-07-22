"""
Community Signal Integration Service
Monitors arXiv, NASA/ESA reports, and trending research for grant relevance.
Includes robust error handling and centralized logging.
"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from grant_ai.models.grant import Grant
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommunitySignal:
    """A community signal (publication, report, etc.)"""
    title: str
    authors: List[str]
    abstract: str
    publication_date: datetime
    source: str
    url: str
    keywords: List[str]
    relevance_score: float


class CommunitySignalIntegrator:
    """Integrates community signals from arXiv, NASA/ESA reports, and trending research."""
    
    def __init__(self):
        logger.info("Initialized CommunitySignalIntegrator.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36'
            )
        })
        
        # arXiv categories relevant to AI and space
        self.arxiv_categories = [
            'cs.AI',      # Artificial Intelligence
            'cs.LG',      # Machine Learning
            'cs.CV',      # Computer Vision
            'cs.RO',      # Robotics
            'astro-ph.IM', # Instrumentation and Methods for Astrophysics
            'astro-ph.EP', # Earth and Planetary Astrophysics
            'astro-ph.SR', # Solar and Stellar Astrophysics
            'physics.space-ph'  # Space Physics
        ]
        
        # Keywords for filtering relevant signals
        self.relevance_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural networks', 'computer vision', 'robotics',
            'space technology', 'satellite', 'spacecraft', 'mars',
            'earth observation', 'remote sensing', 'planetary science',
            'autonomous systems', 'space exploration'
        ]
        
        self.sources = ['arxiv', 'nasa_reports', 'esa_reports']
    
    def fetch_signals(self, keywords: List[str]) -> Dict[str, List[Dict]]:
        """Fetch signals from all sources matching keywords."""
        results = {}
        for source in self.sources:
            results[source] = self._fetch_source_signals(source, keywords)
        return results
    
    def _fetch_source_signals(self, source: str, keywords: List[str]) -> List[Dict]:
        """Stub for fetching signals from a source."""
        # TODO: Implement real fetching logic
        logger.info(f"Fetching signals from {source} for keywords: {keywords}")
        return [{'title': f'Sample {source} result', 'keywords': keywords}]
    
    def fetch_arxiv_signals(self, categories: List[str]) -> List[Dict]:
        """Fetch trending papers from arXiv for given categories."""
        try:
            logger.info(f"Fetching arXiv signals for categories: {categories}")
            
            signals = []
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for category in categories:
                try:
                    # arXiv API query
                    url = f"http://export.arxiv.org/api/query"
                    params = {
                        'search_query': f'cat:{category}',
                        'start': 0,
                        'max_results': 50,
                        'sortBy': 'submittedDate',
                        'sortOrder': 'descending'
                    }
                    
                    response = self.session.get(url, params=params, timeout=15)
                    
                    # Parse XML response
                    root = ET.fromstring(response.content)
                    
                    # Namespace for arXiv API
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    for entry in root.findall('atom:entry', ns):
                        try:
                            title = entry.find('atom:title', ns).text.strip()
                            summary = entry.find('atom:summary', ns).text.strip()
                            
                            # Parse authors
                            authors = []
                            for author in entry.findall('atom:author', ns):
                                name = author.find('atom:name', ns)
                                if name is not None:
                                    authors.append(name.text)
                            
                            # Parse publication date
                            published = entry.find('atom:published', ns).text
                            pub_date = datetime.fromisoformat(
                                published.replace('Z', '+00:00')
                            )
                            
                            # Skip if too old
                            if pub_date < cutoff_date:
                                continue
                            
                            # Get paper URL
                            paper_url = entry.find('atom:id', ns).text
                            
                            # Extract keywords from title and abstract
                            keywords = self._extract_keywords(f"{title} {summary}")
                            
                            signal = CommunitySignal(
                                title=title,
                                authors=authors,
                                abstract=summary,
                                publication_date=pub_date,
                                source=f"arXiv:{category}",
                                url=paper_url,
                                keywords=keywords,
                                relevance_score=0.0  # Will be calculated later
                            )
                            signals.append(signal)
                            
                        except Exception as e:
                            logger.warning(f"Error processing arXiv entry: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error querying arXiv category {category}: {e}")
                    continue
            
            logger.info(f"Fetched {len(signals)} signals from arXiv.")
            return signals
            
        except Exception as e:
            logger.error(f"Error fetching arXiv signals: {e}")
            return []
    
    def fetch_nasa_reports(self) -> List[Dict]:
        """Fetch recent NASA technical reports."""
        try:
            logger.info("Fetching NASA technical reports.")
            
            signals = []
            
            # NASA Technical Reports Server
            url = "https://ntrs.nasa.gov/search.jsp"
            params = {
                'N': '0',
                'Ntk': 'All',
                'Ntt': 'artificial intelligence OR machine learning OR robotics',
                'Ntx': 'mode matchallpartial'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find report listings
            report_items = soup.find_all(['div', 'tr'], class_=re.compile(r'result|item'))
            
            for item in report_items[:20]:  # Limit results
                try:
                    title_elem = item.find(['a', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract abstract/description
                    abstract_elem = item.find(['p', 'div'], class_=re.compile(r'abstract|summary|description'))
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                    
                    # Extract authors
                    author_elem = item.find(text=re.compile(r'Author|By:'))
                    authors = []
                    if author_elem:
                        author_text = author_elem.parent.get_text()
                        authors = [a.strip() for a in author_text.split(',')]
                    
                    # Extract URL
                    report_url = title_elem.get('href', '') if title_elem.name == 'a' else url
                    if report_url and not report_url.startswith('http'):
                        report_url = f"https://ntrs.nasa.gov{report_url}"
                    
                    keywords = self._extract_keywords(f"{title} {abstract}")
                    
                    signal = CommunitySignal(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        publication_date=datetime.now(),  # NASA doesn't always provide dates
                        source="NASA Technical Reports",
                        url=report_url,
                        keywords=keywords,
                        relevance_score=0.0
                    )
                    signals.append(signal)
                    
                except Exception as e:
                    logger.warning(f"Error processing NASA report item: {e}")
                    continue
                    
            logger.info(f"Fetched {len(signals)} signals from NASA.")
            return signals
            
        except Exception as e:
            logger.error(f"Error fetching NASA reports: {e}")
            return []
    
    def fetch_esa_reports(self) -> List[Dict]:
        """Fetch recent ESA technical reports."""
        try:
            logger.info("Fetching ESA technical reports.")
            
            signals = []
            
            # ESA Technical Publications
            url = "https://www.esa.int/Science_Exploration/Space_Science/Publications"
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find publication listings
            pub_items = soup.find_all(['div', 'li'], class_=re.compile(r'publication|document'))
            
            for item in pub_items[:15]:  # Limit results
                try:
                    title_elem = item.find(['a', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Check for AI/space relevance
                    if not any(keyword.lower() in title.lower() for keyword in self.relevance_keywords):
                        continue
                    
                    # Extract description
                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|summary'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Extract URL
                    pub_url = title_elem.get('href', '') if title_elem.name == 'a' else url
                    if pub_url and not pub_url.startswith('http'):
                        pub_url = f"https://www.esa.int{pub_url}"
                    
                    keywords = self._extract_keywords(f"{title} {description}")
                    
                    signal = CommunitySignal(
                        title=title,
                        authors=[],  # ESA doesn't always list authors prominently
                        abstract=description,
                        publication_date=datetime.now(),
                        source="ESA Technical Publications",
                        url=pub_url,
                        keywords=keywords,
                        relevance_score=0.0
                    )
                    signals.append(signal)
                    
                except Exception as e:
                    logger.warning(f"Error processing ESA publication item: {e}")
                    continue
            
            logger.info(f"Fetched {len(signals)} signals from ESA.")
            return signals
            
        except Exception as e:
            logger.error(f"Error fetching ESA reports: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.relevance_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _filter_and_score_signals(self, signals: List[CommunitySignal]) -> List[CommunitySignal]:
        """Filter and score signals by relevance"""
        scored_signals = []
        
        for signal in signals:
            # Calculate relevance score
            score = 0
            
            # Score based on keyword matches
            score += len(signal.keywords) * 2
            
            # Bonus for AI keywords in title
            title_lower = signal.title.lower()
            ai_keywords = ['artificial intelligence', 'machine learning', 'ai', 'ml', 'neural', 'deep learning']
            for ai_kw in ai_keywords:
                if ai_kw in title_lower:
                    score += 3
            
            # Bonus for space keywords in title
            space_keywords = ['space', 'satellite', 'mars', 'planetary', 'spacecraft']
            for space_kw in space_keywords:
                if space_kw in title_lower:
                    score += 2
            
            # Bonus for recent publications (arXiv only has accurate dates)
            if 'arxiv' in signal.source.lower():
                days_old = (datetime.now() - signal.publication_date).days
                if days_old < 7:
                    score += 2
                elif days_old < 14:
                    score += 1
            
            signal.relevance_score = score
            
            # Only include signals with some relevance
            if score > 0:
                scored_signals.append(signal)
        
        # Sort by relevance score (highest first)
        return sorted(scored_signals, key=lambda s: s.relevance_score, reverse=True)
    
    def generate_grant_insights(self, signals: Dict[str, List[CommunitySignal]]) -> Dict:
        """Generate insights for grant discovery based on community signals"""
        
        # Flatten all signals
        all_signals = []
        for source_signals in signals.values():
            all_signals.extend(source_signals)
        
        if not all_signals:
            return {
                'trending_keywords': [],
                'hot_topics': [],
                'research_directions': [],
                'funding_opportunity_insights': []
            }
        
        # Find trending keywords
        keyword_counts = {}
        for signal in all_signals:
            for keyword in signal.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        trending_keywords = sorted(
            keyword_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        
        # Identify hot topics (high-scoring recent signals)
        hot_topics = [
            signal.title for signal in all_signals[:5]
            if signal.relevance_score >= 5
        ]
        
        # Extract research directions from abstracts
        research_directions = self._extract_research_directions(all_signals)
        
        # Generate funding opportunity insights
        funding_insights = self._generate_funding_insights(all_signals)
        
        return {
            'trending_keywords': [kw for kw, count in trending_keywords],
            'hot_topics': hot_topics,
            'research_directions': research_directions,
            'funding_opportunity_insights': funding_insights,
            'total_signals': len(all_signals),
            'source_breakdown': {
                source: len(source_signals)
                for source, source_signals in signals.items()
            }
        }
    
    def _extract_research_directions(self, signals: List[CommunitySignal]) -> List[str]:
        """Extract emerging research directions from signals"""
        directions = []
        
        # Look for common patterns in high-scoring signals
        high_score_signals = [s for s in signals if s.relevance_score >= 4]
        
        for signal in high_score_signals[:10]:
            # Extract key phrases from abstracts
            abstract = signal.abstract.lower()
            
            # Look for methodology keywords
            methods = ['novel', 'new approach', 'framework', 'algorithm', 'method']
            for method in methods:
                if method in abstract:
                    # Extract surrounding context
                    start = max(0, abstract.find(method) - 50)
                    end = min(len(abstract), abstract.find(method) + 100)
                    context = abstract[start:end].strip()
                    if context:
                        directions.append(context)
        
        return directions[:5]  # Return top 5 directions
    
    def _generate_funding_insights(self, signals: List[CommunitySignal]) -> List[str]:
        """Generate insights about potential funding opportunities"""
        insights = []
        
        # Analyze signal patterns
        arxiv_count = sum(1 for s in signals if 'arxiv' in s.source.lower())
        nasa_count = sum(1 for s in signals if 'nasa' in s.source.lower())
        esa_count = sum(1 for s in signals if 'esa' in s.source.lower())
        
        if arxiv_count > 10:
            insights.append(
                f"High academic activity ({arxiv_count} arXiv papers) suggests "
                "strong research interest - good timing for research grants"
            )
        
        if nasa_count > 3:
            insights.append(
                f"NASA technical reports ({nasa_count}) indicate agency focus - "
                "check NASA SBIR/STTR opportunities"
            )
        
        if esa_count > 2:
            insights.append(
                f"ESA publications ({esa_count}) suggest European space agency "
                "interest - consider ESA funding programs"
            )
        
        # Keyword-based insights
        all_keywords = []
        for signal in signals:
            all_keywords.extend(signal.keywords)
        
        if 'artificial intelligence' in all_keywords:
            insights.append(
                "Strong AI signal - NSF AI programs and DOE AI initiatives likely relevant"
            )
        
        if 'space technology' in all_keywords:
            insights.append(
                "Space technology focus - NASA STTR and commercial space grants available"
            )
        
        return insights[:5]  # Return top 5 insights
    
    def get_recent_signals(self, days_back: int = 30) -> Dict[str, List[CommunitySignal]]:
        """Get recent community signals from multiple sources"""
        signals = {}
        
        # Get arXiv signals
        try:
            signals['arxiv'] = self.fetch_arxiv_signals(self.arxiv_categories)
        except Exception as e:
            logger.error(f"Error getting arXiv signals: {e}")
            signals['arxiv'] = []
        
        # Get NASA/ESA technical reports
        try:
            signals['nasa_reports'] = self.fetch_nasa_reports()
        except Exception as e:
            logger.error(f"Error getting NASA reports: {e}")
            signals['nasa_reports'] = []
        
        try:
            signals['esa_reports'] = self.fetch_esa_reports()
        except Exception as e:
            logger.error(f"Error getting ESA reports: {e}")
            signals['esa_reports'] = []
        
        # Filter and score signals
        for source in signals:
            signals[source] = self._filter_and_score_signals(signals[source])
        
        logger.info("Recent signals fetched and processed.")
        return signals
    
    def analyze_trends(self, signals: dict) -> dict:
        """Analyze trends from fetched signals."""
        # Basic placeholder for trend analysis logic
        return {source: 'Trending' for source in signals}


# Integration function
def get_community_insights_for_grants(grants: List[Grant]) -> Dict:
    """Get community insights to enhance grant discovery"""
    integrator = CommunitySignalIntegrator()
    
    # Get recent community signals
    signals = integrator.get_recent_signals(days_back=30)
    
    # Generate insights
    insights = integrator.generate_grant_insights(signals)
    
    # Match signals to grants (find related research)
    grant_signal_matches = {}
    for grant in grants:
        grant_text = f"{grant.title} {grant.description}".lower()
        matching_signals = []
        
        for source_signals in signals.values():
            for signal in source_signals:
                # Check for keyword overlap
                signal_keywords = [kw.lower() for kw in signal.keywords]
                if any(keyword in grant_text for keyword in signal_keywords):
                    matching_signals.append(signal)
        
        if matching_signals:
            grant_key = grant.title[:50] if grant.title else f"grant_{id(grant)}"
            grant_signal_matches[grant_key] = matching_signals[:3]  # Top 3 matches
    
    return {
        'community_signals': signals,
        'insights': insights,
        'grant_signal_matches': grant_signal_matches,
        'integrator': integrator
    }
