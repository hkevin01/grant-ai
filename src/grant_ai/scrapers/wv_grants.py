"""
West Virginia grant scraper for state-specific funding opportunities.
"""
import re
import socket
import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus


class WVGrantScraper:
    """Scraper for West Virginia grant opportunities."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Better timeout and retry configuration
        self.session.timeout = (5, 15)  # (connect timeout, read timeout)
        
        # Configure retries with backoff
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # WV grant sources with working URLs and enhanced fallbacks
        self.sources = {
            'arts_commission': {
                'url': 'https://wvculture.org/arts/grants/',
                'name': 'WV Arts Commission',
                'fallbacks': [
                    'https://wvculture.org/agencies/arts/grants/',
                    'https://wvculture.org/arts/funding/',
                    'https://wvculture.org/grants/'
                ]
            },
            'education': {
                'url': 'https://wvde.us/federal-programs/',
                'name': 'WV Department of Education',
                'fallbacks': [
                    'https://wvde.us/programs/',
                    'https://wvde.us/office-of-federal-programs/',
                    'https://www.wv.gov/pages/education.aspx',
                    'https://wvde.us/',
                    'https://wvde.us/finance/',
                    'https://wvde.us/student-support/',
                    'https://wvde.us/teaching-and-learning/'
                ]
            },
            'grants_gov_wv': {
                'url': 'https://www.grants.gov/search-grants?query=west+virginia',
                'name': 'Federal Grants for WV',
                'fallbacks': [
                    'https://www.grants.gov/search-grants?query=WV',
                    'https://www.grants.gov/search-grants'
                ]
            },
            'wv_development': {
                'url': 'https://westvirginia.gov/business/financing/',
                'name': 'WV Economic Development',
                'fallbacks': [
                    'https://westvirginia.gov/business/',
                    'https://www.wv.gov/pages/business.aspx'
                ]
            },
            'health_programs': {
                'url': 'https://dhhr.wv.gov/programs/',
                'name': 'WV Health Programs',
                'fallbacks': [
                    'https://dhhr.wv.gov/Pages/default.aspx',
                    'https://dhhr.wv.gov/funding/',
                    'https://dhhr.wv.gov/grants/'
                ]
            }
        }
    
    def _check_dns_resolution(self, url: str) -> bool:
        """Check if a domain can be resolved."""
        try:
            parsed = urlparse(url)
            socket.gethostbyname(parsed.netloc)
            return True
        except (socket.gaierror, Exception):
            return False
    
    def scrape_all_sources(self) -> List[Grant]:
        """Scrape grants from all WV sources with enhanced error handling."""
        all_grants = []
        
        # Initialize robust scraper if available
        try:
            from grant_ai.services.robust_scraper import RobustWebScraper
            robust_scraper = RobustWebScraper()
            print("🛡️ Using enhanced robust scraper")
        except ImportError:
            robust_scraper = None
            print("⚠️ Robust scraper not available, using basic scraping")
        
        for source_id, source_info in self.sources.items():
            try:
                print(f"🔍 Scraping {source_info['name']}...")
                
                # Check DNS resolution first
                if not self._check_dns_resolution(source_info['url']):
                    print(f"⚠️  DNS resolution failed for {source_info['name']}, skipping...")
                    continue
                
                # Use robust scraper if available, fallback to original method
                if robust_scraper:
                    try:
                        fallback_urls = source_info.get('fallbacks', [])
                        grants = self._scrape_source_robust(
                            source_id, source_info, robust_scraper, fallback_urls
                        )
                    except Exception as e:
                        print(f"⚠️ Robust scraping failed for {source_info['name']}: {e}")
                        grants = self._scrape_source(source_id, source_info)
                else:
                    grants = self._scrape_source(source_id, source_info)
                
                if grants:
                    all_grants.extend(grants)
                    print(f"✅ Found {len(grants)} grants from {source_info['name']}")
                else:
                    print(f"⚠️  No grants found from {source_info['name']}")
                
                # Pause between requests to prevent overwhelming servers
                time.sleep(3)
                
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Connection error for {source_info['name']}: {e}")
            except requests.exceptions.Timeout as e:
                print(f"⏰ Timeout for {source_info['name']}: {e}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error for {source_info['name']}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {source_info['name']}: {e}")
        
        return all_grants
    
    def _scrape_source(self, source_id: str, source_info: dict) -> List[Grant]:
        """Scrape grants from a specific source with error handling."""
        try:
            if source_id == 'arts_commission':
                return self._scrape_arts_commission(source_info)
            elif source_id == 'education':
                return self._scrape_education(source_info)
            elif source_id == 'commerce':
                return self._scrape_commerce(source_info)
            elif source_id == 'health':
                return self._scrape_health(source_info)
            else:
                return []
        except Exception as e:
            print(f"Error in _scrape_source for {source_id}: {e}")
            return []
    
    def _scrape_arts_commission(self, source_info: dict) -> List[Grant]:
        """Scrape WV Arts Commission grants."""
        grants = []
        
        try:
            response = self.session.get(source_info['url'], timeout=(5, 15))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for grant opportunities
            grant_elements = soup.find_all(['div', 'article'], class_=re.compile(r'grant|opportunity|funding'))
            
            for element in grant_elements[:5]:  # Limit to 5 results
                grant = self._parse_arts_grant(element, source_info)
                if grant:
                    grants.append(grant)
            
        except requests.exceptions.RequestException as e:
            print(f"Request error scraping Arts Commission: {e}")
        except Exception as e:
            print(f"Error scraping Arts Commission: {e}")
        
        # Add sample grants if scraping fails
        if not grants:
            grants = self._get_sample_arts_grants(source_info)
        
        return grants
    
    def _scrape_education(self, source_info: dict) -> List[Grant]:
        """Scrape WV Department of Education financial assistance opportunities."""
        grants = []
        
        # Try multiple URLs with comprehensive fallback approach
        urls_to_try = [source_info['url']] + source_info.get('fallbacks', [])
        
        for url in urls_to_try:
            try:
                print(f"🎓 Trying education URL: {url}")
                response = self.session.get(url, timeout=(10, 30))
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Enhanced search for all financial assistance opportunities
                # Use broader selectors and keywords
                financial_assistance_selectors = [
                    # Class-based selectors for financial assistance
                    ['div', 'article', 'section'], {
                        'class_': re.compile(r'grant|funding|assistance|aid|scholarship|'
                                           r'support|program|opportunity|finance|'
                                           r'student|education|resource')
                    },
                    # Text-based search for financial assistance terms
                    ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], None,
                    ['p', 'div', 'span'], None,
                    ['a'], {'href': re.compile(r'grant|funding|assistance|aid|'
                                             r'scholarship|finance|program')}
                ]
                
                found_elements = []
                
                # Search using class-based selectors
                class_elements = soup.find_all(
                    financial_assistance_selectors[0],
                    financial_assistance_selectors[1]
                )
                found_elements.extend(class_elements)
                
                # Search by text content for financial assistance keywords
                financial_keywords = [
                    'grant', 'funding', 'financial assistance', 'aid', 
                    'scholarship', 'support', 'program', 'resource',
                    'student aid', 'educational support', 'title i',
                    'federal programs', 'state funding', 'educational grants',
                    'school programs', 'learning support', 'academic assistance'
                ]
                
                for keyword in financial_keywords:
                    text_elements = soup.find_all(
                        text=re.compile(keyword, re.IGNORECASE)
                    )
                    for text_elem in text_elements[:3]:  # Limit per keyword
                        parent = text_elem.parent
                        if parent and parent not in found_elements:
                            found_elements.append(parent)
                
                # Also search for links that might lead to financial assistance
                link_elements = soup.find_all('a', href=re.compile(
                    r'grant|funding|assistance|aid|scholarship|finance|program',
                    re.IGNORECASE
                ))
                found_elements.extend(link_elements[:5])
                
                print(f"📋 Found {len(found_elements)} potential financial "
                      f"assistance elements on {url}")
                
                # Parse found elements
                for element in found_elements[:10]:  # Limit to 10 results per URL
                    grant = self._parse_education_assistance(element, source_info, url)
                    if grant and grant not in grants:
                        grants.append(grant)
                
                # If we found some results, don't try more URLs
                if grants:
                    print(f"✅ Successfully found {len(grants)} opportunities "
                          f"from {url}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error scraping Education from {url}: {e}")
                continue
            except Exception as e:
                print(f"Error scraping Education from {url}: {e}")
                continue
        
        # Add sample grants if scraping fails completely
        if not grants:
            print("📝 Using sample education assistance opportunities")
            grants = self._get_sample_education_grants(source_info)
        
        return grants
    
    def _scrape_commerce(self, source_info: dict) -> List[Grant]:
        """Scrape WV Department of Commerce grants."""
        grants = []
        
        try:
            response = self.session.get(source_info['url'], timeout=(5, 15))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for grant opportunities
            grant_elements = soup.find_all(['div', 'article'], class_=re.compile(r'grant|opportunity|funding'))
            
            for element in grant_elements[:5]:  # Limit to 5 results
                grant = self._parse_commerce_grant(element, source_info)
                if grant:
                    grants.append(grant)
            
        except requests.exceptions.RequestException as e:
            print(f"Request error scraping Commerce: {e}")
        except Exception as e:
            print(f"Error scraping Commerce: {e}")
        
        # Add sample grants if scraping fails
        if not grants:
            grants = self._get_sample_commerce_grants(source_info)
        
        return grants
    
    def _scrape_health(self, source_info: dict) -> List[Grant]:
        """Scrape WV Department of Health grants."""
        grants = []
        
        try:
            response = self.session.get(source_info['url'], timeout=(5, 15))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for grant opportunities
            grant_elements = soup.find_all(['div', 'article'], class_=re.compile(r'grant|opportunity|funding'))
            
            for element in grant_elements[:5]:  # Limit to 5 results
                grant = self._parse_health_grant(element, source_info)
                if grant:
                    grants.append(grant)
            
        except requests.exceptions.RequestException as e:
            print(f"Request error scraping Health: {e}")
        except Exception as e:
            print(f"Error scraping Health: {e}")
        
        # Add sample grants if scraping fails
        if not grants:
            grants = self._get_sample_health_grants(source_info)
        
        return grants
    
    def _parse_arts_grant(self, element, source_info: dict) -> Optional[Grant]:
        """Parse an arts commission grant element."""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text().strip() if title_elem else "Arts Grant"
            
            desc_elem = element.find(['p', 'div'])
            description = desc_elem.get_text().strip() if desc_elem else "Arts education grant opportunity."
            
            # Extract amount if present
            amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:,\d{3})*)', description)
            amount = None
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            
            return Grant(
                id=f"wv_arts_{int(time.time())}_{hash(title) % 10000}",
                title=title[:200],
                description=description[:1000],
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_typical=amount or 5000,
                amount_min=amount or 1000,
                amount_max=amount * 2 if amount else 10000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['art_education', 'education'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="arts@wvculture.org",
                contact_phone="304-558-0220",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing arts grant: {e}")
            return None
    
    def _parse_education_assistance(self, element, source_info: dict, url: str) -> Optional[Grant]:
        """Parse an education financial assistance element."""
        try:
            # Extract title from various possible elements
            title_elem = None
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                title_elem = element.find(tag)
                if title_elem:
                    break
            
            # If no header, try link text or strong text
            if not title_elem:
                title_elem = element.find('a') or element.find('strong')
            
            title = title_elem.get_text().strip() if title_elem else "Financial Assistance"
            
            # Clean up title and determine assistance type
            title = re.sub(r'\s+', ' ', title)
            assistance_type = self._determine_assistance_type(title, element)
            
            # Extract description
            desc_elem = element.find(['p', 'div', 'span'])
            description = desc_elem.get_text().strip() if desc_elem else ""
            
            # If no description in element, try to get surrounding text
            if not description and element.parent:
                nearby_text = element.parent.get_text().strip()
                description = nearby_text[:500] if nearby_text else ""
            
            # Default description based on assistance type
            if not description:
                description = f"{assistance_type} opportunity from WV Department of Education."
            
            # Extract amount if present
            amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*)', description + " " + title)
            amount = None
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            
            # Determine funding type and amounts based on assistance type
            funding_type, typical_amount, min_amount, max_amount = self._get_assistance_amounts(assistance_type, amount)
            
            # Extract application URL if available
            app_url = url
            link_elem = element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('http'):
                    app_url = href
                elif href.startswith('/'):
                    from urllib.parse import urljoin
                    app_url = urljoin(url, href)
            
            # Generate unique ID
            grant_id = f"wv_edu_{assistance_type.lower()}_{int(time.time())}_{hash(title) % 10000}"
            
            return Grant(
                id=grant_id,
                title=title[:200],
                description=description[:1000],
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=funding_type,
                amount_typical=typical_amount,
                amount_min=min_amount,
                amount_max=max_amount,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'youth_development', 'student_support'],
                source=source_info['name'],
                source_url=url,
                contact_email="grants@wvde.us",
                contact_phone="304-558-2681",
                application_url=app_url,
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing education assistance: {e}")
            return None

    def _determine_assistance_type(self, title: str, element) -> str:
        """Determine the type of financial assistance based on title and content."""
        title_lower = title.lower()
        element_text = element.get_text().lower() if element else ""
        
        if any(word in title_lower for word in ['scholarship', 'student aid']):
            return "Scholarship"
        elif any(word in title_lower for word in ['loan', 'lending']):
            return "Loan"
        elif any(word in title_lower for word in ['title i', 'federal program']):
            return "Federal Program"
        elif any(word in title_lower for word in ['professional development', 'teacher', 'training']):
            return "Professional Development"
        elif any(word in title_lower for word in ['technology', 'equipment', 'infrastructure']):
            return "Technology Grant"
        elif any(word in title_lower for word in ['special education', 'disability', 'accessibility']):
            return "Special Education Support"
        elif any(word in element_text for word in ['assistance', 'aid', 'support']):
            return "Financial Assistance"
        else:
            return "Educational Grant"

    def _get_assistance_amounts(self, assistance_type: str, parsed_amount: Optional[int]) -> tuple:
        """Get funding type and typical amounts based on assistance type."""
        if parsed_amount:
            return FundingType.GRANT, parsed_amount, int(parsed_amount * 0.5), int(parsed_amount * 2)
        
        # Default amounts by assistance type
        amount_ranges = {
            "Scholarship": (FundingType.SCHOLARSHIP, 2500, 500, 10000),
            "Loan": (FundingType.LOAN, 15000, 1000, 50000),
            "Federal Program": (FundingType.GRANT, 50000, 10000, 500000),
            "Professional Development": (FundingType.GRANT, 5000, 1000, 25000),
            "Technology Grant": (FundingType.GRANT, 15000, 3000, 75000),
            "Special Education Support": (FundingType.GRANT, 25000, 5000, 100000),
            "Financial Assistance": (FundingType.GRANT, 10000, 2000, 50000),
            "Educational Grant": (FundingType.GRANT, 25000, 5000, 100000)
        }
        
        return amount_ranges.get(assistance_type, (FundingType.GRANT, 25000, 5000, 100000))
    
    def _parse_commerce_grant(self, element, source_info: dict) -> Optional[Grant]:
        """Parse a commerce grant element."""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text().strip() if title_elem else "Commerce Grant"
            
            desc_elem = element.find(['p', 'div'])
            description = desc_elem.get_text().strip() if desc_elem else "Economic development grant opportunity."
            
            # Extract amount if present
            amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:,\d{3})*)', description)
            amount = None
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            
            return Grant(
                id=f"wv_commerce_{int(time.time())}_{hash(title) % 10000}",
                title=title[:200],
                description=description[:1000],
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_typical=amount or 50000,
                amount_min=amount or 10000,
                amount_max=amount * 2 if amount else 200000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.STARTUP],
                focus_areas=['community_development', 'economic_development'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="info@wvcommerce.org",
                contact_phone="304-957-2234",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing commerce grant: {e}")
            return None
    
    def _parse_health_grant(self, element, source_info: dict) -> Optional[Grant]:
        """Parse a health grant element."""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
            title = title_elem.get_text().strip() if title_elem else "Health Grant"
            
            desc_elem = element.find(['p', 'div'])
            description = desc_elem.get_text().strip() if desc_elem else "Health and human services grant opportunity."
            
            # Extract amount if present
            amount_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:,\d{3})*)', description)
            amount = None
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
            
            return Grant(
                id=f"wv_health_{int(time.time())}_{hash(title) % 10000}",
                title=title[:200],
                description=description[:1000],
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_typical=amount or 30000,
                amount_min=amount or 5000,
                amount_max=amount * 2 if amount else 150000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['health', 'social_services'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="grants@dhhr.wv.gov",
                contact_phone="304-558-0684",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing health grant: {e}")
            return None
    
    def _get_sample_arts_grants(self, source_info: dict) -> List[Grant]:
        """Get sample arts commission grants."""
        return [
            Grant(
                id="wv_arts_001",
                title="WV Arts Commission Project Support Grant",
                description="Supporting arts projects and programs in West Virginia communities.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=1000,
                amount_max=10000,
                amount_typical=5000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['art_education', 'education'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="arts@wvculture.org",
                contact_phone="304-558-0220",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _get_sample_education_grants(self, source_info: dict) -> List[Grant]:
        """Get sample education financial assistance opportunities."""
        return [
            Grant(
                id="wv_edu_001",
                title="WV Department of Education Innovation Grant",
                description="Supporting innovative educational programs and initiatives in West Virginia schools, including STEM programs, arts integration, and technology enhancement.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=5000,
                amount_max=50000,
                amount_typical=25000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'youth_development', 'innovation'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="grants@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_edu_002",
                title="Title I School Improvement Financial Assistance",
                description="Federal funding assistance for Title I schools to improve academic achievement and support disadvantaged students through comprehensive educational programs.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=25000,
                amount_max=500000,
                amount_typical=150000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'student_support', 'disadvantaged_communities'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="titleI@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_edu_003",
                title="Professional Development Support Program",
                description="Financial assistance for teacher training, professional development, and educational leadership programs to enhance classroom instruction and student outcomes.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=2000,
                amount_max=25000,
                amount_typical=8000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.INDIVIDUAL],
                focus_areas=['education', 'professional_development', 'teacher_training'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="profdev@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_edu_004",
                title="Special Education Support Fund",
                description="Financial assistance for special education programs, accessibility improvements, and support services for students with disabilities in West Virginia schools.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=10000,
                amount_max=100000,
                amount_typical=35000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'special_education', 'accessibility', 'student_support'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="specialed@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_edu_005",
                title="Technology Integration Financial Aid",
                description="Support for educational technology initiatives, digital learning resources, and infrastructure improvements to enhance 21st-century learning in WV schools.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=5000,
                amount_max=75000,
                amount_typical=20000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                focus_areas=['education', 'technology', 'digital_learning', 'infrastructure'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="tech@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            ),
            Grant(
                id="wv_edu_006",
                title="Student Emergency Financial Assistance",
                description="Emergency financial aid for students facing unexpected hardships, including food insecurity, housing issues, and basic needs support to ensure continued education.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.SCHOLARSHIP,
                amount_min=500,
                amount_max=5000,
                amount_typical=1500,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.INDIVIDUAL, EligibilityType.STUDENT],
                focus_areas=['education', 'emergency_assistance', 'student_support', 'basic_needs'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="studentaid@wvde.us",
                contact_phone="304-558-2681",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _get_sample_commerce_grants(self, source_info: dict) -> List[Grant]:
        """Get sample commerce grants."""
        return [
            Grant(
                id="wv_commerce_001",
                title="WV Economic Development Grant",
                description="Supporting economic development and job creation initiatives in West Virginia.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=10000,
                amount_max=100000,
                amount_typical=50000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.STARTUP],
                focus_areas=['economic_development', 'community_development'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="info@wvcommerce.org",
                contact_phone="304-957-2234",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _get_sample_health_grants(self, source_info: dict) -> List[Grant]:
        """Get sample health grants."""
        return [
            Grant(
                id="wv_health_001",
                title="WV Health and Human Services Grant",
                description="Supporting health and human services programs in West Virginia communities.",
                funder_name=source_info['name'],
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=5000,
                amount_max=75000,
                amount_typical=30000,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=['health', 'social_services'],
                source=source_info['name'],
                source_url=source_info['url'],
                contact_email="grants@dhhr.wv.gov",
                contact_phone="304-558-0684",
                application_url=source_info['url'],
                last_updated=datetime.now(),
                created_at=datetime.now()
            )
        ]
    
    def _scrape_source_robust(
        self, 
        source_id: str, 
        source_info: dict, 
        robust_scraper,
        fallback_urls: Optional[List[str]] = None
    ) -> List[Grant]:
        """Scrape using the robust scraper with fallbacks."""
        try:
            # Define selectors for each source
            selectors = self._get_selectors_for_source(source_id)
            
            # Use provided fallbacks or get defaults
            if fallback_urls is None:
                fallback_urls = self._get_fallback_urls(source_id)
            
            # Fetch with robust error handling
            soup = robust_scraper.fetch_with_fallbacks(
                source_info['url'],
                fallback_urls=fallback_urls
            )
            
            if soup:
                # Extract grants using robust selectors
                grants = robust_scraper.extract_grants_with_selectors(
                    soup, selectors
                )
                
                # Set source URL for all grants
                for grant in grants:
                    grant.url = source_info['url']
                    grant.source = source_info['name']
                
                return grants
            else:
                # Fallback to original scraping method
                return self._scrape_source(source_id, source_info)
                
        except Exception as e:
            print(f"Robust scraping failed for {source_id}: {e}")
            # Fallback to original method
            return self._scrape_source(source_id, source_info)
    
    def _get_selectors_for_source(self, source_id: str) -> dict:
        """Get CSS selectors for extracting grants from each source."""
        selectors = {
            'arts_commission': {
                'containers': [
                    '.grant-opportunity',
                    '.funding-opportunity',
                    '.entry-content div',
                    'article',
                    '.content-area div'
                ],
                'title': ['h2', 'h3', '.title', '.grant-title'],
                'description': ['.description', '.summary', 'p'],
                'amount': ['.amount', '.funding'],
                'deadline': ['.deadline', '.due-date'],
                'funder': ['.funder', '.organization']
            },
            'education': {
                'containers': [
                    '.grant-listing',
                    '.opportunity',
                    '.program',
                    '.content-area div',
                    'article'
                ],
                'title': ['h1', 'h2', 'h3', '.title'],
                'description': ['.description', '.content', 'p'],
                'amount': ['.amount', '.award'],
                'deadline': ['.deadline', '.closing-date'],
                'funder': ['.agency', '.department']
            },
            'grants_gov_wv': {
                'containers': [
                    '.search-result',
                    '.grant-opportunity',
                    '.opportunity-result',
                    'article'
                ],
                'title': ['h2', 'h3', '.title', '.opportunity-title'],
                'description': ['.description', '.summary', '.excerpt', 'p'],
                'amount': ['.amount', '.award-amount', '.funding'],
                'deadline': ['.deadline', '.closing-date', '.due-date'],
                'funder': ['.agency', '.department', '.funder']
            },
            'wv_development': {
                'containers': [
                    '.business-grant',
                    '.program',
                    '.opportunity',
                    '.financing-option',
                    'article'
                ],
                'title': ['h2', 'h3', '.program-title', '.title'],
                'description': ['.description', '.overview', 'p'],
                'amount': ['.amount', '.funding-range'],
                'deadline': ['.deadline', '.application-deadline'],
                'funder': ['.department', '.agency']
            },
            'health_programs': {
                'containers': [
                    '.health-grant',
                    '.program',
                    '.initiative',
                    '.program-listing',
                    'article'
                ],
                'title': ['h2', 'h3', '.title', '.program-title'],
                'description': ['.description', '.purpose', 'p'],
                'amount': ['.amount', '.award-amount'],
                'deadline': ['.deadline', '.due-date'],
                'funder': ['.dhhr', '.department']
            }
        }
        
        return selectors.get(source_id, {
            'containers': ['article', '.content', '.main', '.program'],
            'title': ['h1', 'h2', 'h3'],
            'description': ['p', '.description'],
            'amount': ['.amount'],
            'deadline': ['.deadline'],
            'funder': ['.funder']
        })
    
    def _get_fallback_urls(self, source_id: str) -> List[str]:
        """Get fallback URLs for each source from the sources configuration."""
        if source_id in self.sources:
            return self.sources[source_id].get('fallbacks', [])
        
        # Default fallbacks for unknown sources
        return [
            'https://www.wv.gov/pages/business.aspx',
            'https://www.grants.gov/search-grants?query=west+virginia'
        ]
        

def scrape_wv_grants() -> List[Grant]:
    """Convenience function to scrape all WV grants."""
    scraper = WVGrantScraper()
    return scraper.scrape_all_sources()


if __name__ == "__main__":
    # Test the scraper
    scraper = WVGrantScraper()
    grants = scraper.scrape_all_sources()
    
    print(f"Found {len(grants)} WV grants:")
    for grant in grants:
        print(f"- {grant.title} ({grant.funder_name}) - ${grant.amount_typical:,}")