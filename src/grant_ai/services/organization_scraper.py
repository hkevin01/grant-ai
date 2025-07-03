"""
Organization Web Scraper Service

This service scrapes organization websites to extract real data for filling out
the organization profile questionnaire.
"""

import re
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

from ..models.organization import FocusArea, ProgramType
from ..models.questionnaire import QuestionnaireResponse, Questionnaire


class OrganizationScraper:
    """
    Web scraper for extracting organization information from websites.
    
    This scraper uses various techniques to extract real organization data:
    - Meta tags and structured data
    - Common content patterns
    - Contact information extraction
    - Mission statement detection
    - Program and focus area identification
    """
    
    def __init__(self):
        """Initialize the scraper with common patterns and headers."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Common patterns for extracting organization information
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'ein': r'\b\d{2}-\d{7}\b',
            'year': r'\b(19|20)\d{2}\b',
            'address': r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter)',
        }
        
        # Keywords for identifying focus areas and program types
        self.focus_keywords = {
            FocusArea.EDUCATION: ['education', 'learning', 'school', 'academic', 'teaching', 'student', 'curriculum'],
            FocusArea.MUSIC_EDUCATION: ['music', 'musical', 'orchestra', 'band', 'choir', 'instrumental'],
            FocusArea.ART_EDUCATION: ['art', 'arts', 'creative', 'painting', 'drawing', 'sculpture', 'visual'],
            FocusArea.ROBOTICS: ['robotics', 'robot', 'automation', 'mechanical', 'engineering'],
            FocusArea.HOUSING: ['housing', 'home', 'residential', 'shelter', 'accommodation'],
            FocusArea.AFFORDABLE_HOUSING: ['affordable housing', 'low-income housing', 'subsidized housing'],
            FocusArea.COMMUNITY_DEVELOPMENT: ['community', 'development', 'neighborhood', 'infrastructure'],
            FocusArea.SOCIAL_SERVICES: ['social', 'welfare', 'assistance', 'support', 'help', 'aid'],
            FocusArea.YOUTH_DEVELOPMENT: ['youth', 'teen', 'adolescent', 'young', 'children', 'kids'],
            FocusArea.SENIOR_SERVICES: ['senior', 'elderly', 'aging', 'retirement', 'adult'],
        }
        
        self.program_keywords = {
            ProgramType.AFTER_SCHOOL: ['after school', 'afterschool', 'extracurricular', 'enrichment'],
            ProgramType.SUMMER_CAMPS: ['summer camp', 'summer program', 'summer activities'],
            ProgramType.HOUSING_DEVELOPMENT: ['housing development', 'construction', 'building'],
            ProgramType.SUPPORT_SERVICES: ['support services', 'counseling', 'case management'],
            ProgramType.EDUCATIONAL_WORKSHOPS: ['workshop', 'training', 'seminar', 'class'],
            ProgramType.COMMUNITY_OUTREACH: ['community outreach', 'outreach', 'engagement'],
        }
    
    def scrape_organization(self, website_url: str) -> Dict[str, Any]:
        """
        Scrape organization information from a website.
        
        Args:
            website_url: The organization's website URL
            
        Returns:
            Dictionary containing extracted organization data
        """
        try:
            # Normalize URL
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            # Fetch the webpage
            response = self.session.get(website_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information
            data = {
                'name': self._extract_organization_name(soup, website_url),
                'description': self._extract_description(soup),
                'focus_areas': self._identify_focus_areas(soup),
                'program_types': self._identify_program_types(soup),
                'target_demographics': self._extract_target_demographics(soup),
                'location': self._extract_location(soup),
                'website': website_url,
                'contact_name': self._extract_contact_name(soup),
                'contact_email': self._extract_contact_email(soup),
                'contact_phone': self._extract_contact_phone(soup),
                'ein': self._extract_ein(soup),
                'founded_year': self._extract_founded_year(soup),
                'annual_budget': None,  # Usually not publicly available
            }
            
            return data
            
        except Exception as e:
            print(f"Error scraping {website_url}: {e}")
            return {}
    
    def _extract_organization_name(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract organization name from various sources."""
        # Try meta tags first
        meta_name = soup.find('meta', property='og:site_name')
        if meta_name and meta_name.get('content'):
            return meta_name['content'].strip()
        
        # Try title tag
        title = soup.find('title')
        if title and title.text:
            title_text = title.text.strip()
            # Clean up common title suffixes
            for suffix in [' - Home', ' | Home', ' - Welcome', ' | Welcome']:
                if title_text.endswith(suffix):
                    title_text = title_text[:-len(suffix)]
            return title_text
        
        # Try h1 tags
        h1 = soup.find('h1')
        if h1 and h1.text:
            return h1.text.strip()
        
        # Extract from URL as fallback
        domain = urlparse(url).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.replace('.', ' ').title()
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract organization description/mission."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Look for mission statement patterns
        mission_patterns = [
            'mission',
            'about us',
            'who we are',
            'our story',
            'purpose',
            'vision'
        ]
        
        for pattern in mission_patterns:
            # Look for headings containing these words
            for tag in ['h1', 'h2', 'h3', 'h4']:
                for heading in soup.find_all(tag):
                    if pattern.lower() in heading.text.lower():
                        # Get the next paragraph or div
                        next_elem = heading.find_next_sibling(['p', 'div'])
                        if next_elem and next_elem.text.strip():
                            return next_elem.text.strip()[:500]  # Limit length
        
        # Try to find the first substantial paragraph
        for p in soup.find_all('p'):
            text = p.text.strip()
            if len(text) > 50 and len(text) < 500:
                return text
        
        return None
    
    def _identify_focus_areas(self, soup: BeautifulSoup) -> List[str]:
        """Identify focus areas based on content analysis."""
        text_content = soup.get_text().lower()
        identified_areas = []
        
        for focus_area, keywords in self.focus_keywords.items():
            for keyword in keywords:
                if keyword in text_content:
                    identified_areas.append(focus_area.value)
                    break
        
        return identified_areas
    
    def _identify_program_types(self, soup: BeautifulSoup) -> List[str]:
        """Identify program types based on content analysis."""
        text_content = soup.get_text().lower()
        identified_programs = []
        
        for program_type, keywords in self.program_keywords.items():
            for keyword in keywords:
                if keyword in text_content:
                    identified_programs.append(program_type.value)
                    break
        
        return identified_programs
    
    def _extract_target_demographics(self, soup: BeautifulSoup) -> List[str]:
        """Extract target demographics from content."""
        text_content = soup.get_text().lower()
        demographics = []
        
        demographic_keywords = [
            'youth', 'teen', 'adolescent', 'young people', 'children', 'kids',
            'senior', 'elderly', 'older adults', 'aging population',
            'family', 'families', 'parents',
            'student', 'students', 'learner', 'learners',
            'community', 'residents', 'citizens',
            'veteran', 'veterans', 'military',
            'disability', 'disabled', 'special needs',
            'minority', 'underrepresented', 'marginalized',
            'low-income', 'economically disadvantaged',
            'rural', 'urban', 'suburban'
        ]
        
        for keyword in demographic_keywords:
            if keyword in text_content:
                demographics.append(keyword.title())
        
        return list(set(demographics))  # Remove duplicates
    
    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract organization location."""
        # Look for address patterns
        text_content = soup.get_text()
        address_match = re.search(self.patterns['address'], text_content)
        if address_match:
            return address_match.group(0)
        
        # Look for location in contact information
        contact_sections = soup.find_all(['div', 'section'], class_=re.compile(r'contact|location|address', re.I))
        for section in contact_sections:
            text = section.get_text()
            # Look for city, state patterns
            city_state = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', text)
            if city_state:
                return city_state.group(0)
        
        return None
    
    def _extract_contact_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract primary contact person name."""
        # Look for common patterns in contact sections
        contact_sections = soup.find_all(['div', 'section'], class_=re.compile(r'contact|staff|team|leadership', re.I))
        
        for section in contact_sections:
            text = section.get_text()
            # Look for "Contact:" or "Director:" patterns
            contact_match = re.search(r'(?:Contact|Director|Executive|President):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
            if contact_match:
                return contact_match.group(1)
        
        return None
    
    def _extract_contact_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contact email address."""
        text_content = soup.get_text()
        email_match = re.search(self.patterns['email'], text_content)
        if email_match:
            return email_match.group(0)
        
        # Look for mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        for link in mailto_links:
            email = link['href'].replace('mailto:', '')
            if '@' in email:
                return email
        
        return None
    
    def _extract_contact_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contact phone number."""
        text_content = soup.get_text()
        phone_match = re.search(self.patterns['phone'], text_content)
        if phone_match:
            return phone_match.group(0)
        
        # Look for tel links
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        for link in tel_links:
            phone = link['href'].replace('tel:', '')
            return phone
        
        return None
    
    def _extract_ein(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract EIN (Employer Identification Number)."""
        text_content = soup.get_text()
        ein_match = re.search(self.patterns['ein'], text_content)
        if ein_match:
            return ein_match.group(0)
        return None
    
    def _extract_founded_year(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract organization founding year."""
        text_content = soup.get_text()
        year_matches = re.findall(self.patterns['year'], text_content)
        
        # Look for founding-related context
        founding_keywords = ['founded', 'established', 'started', 'created', 'incorporated']
        
        for keyword in founding_keywords:
            if keyword in text_content.lower():
                # Find years near the founding keyword
                keyword_index = text_content.lower().find(keyword)
                for year_match in year_matches:
                    year_index = text_content.find(year_match)
                    if abs(keyword_index - year_index) < 100:  # Within 100 characters
                        try:
                            return int(year_match)
                        except ValueError:
                            continue
        
        # If no founding context found, return the earliest year (likely founding year)
        if year_matches:
            try:
                return min(int(year) for year in year_matches)
            except ValueError:
                pass
        
        return None
    
    def fill_questionnaire_from_website(self, website_url: str, questionnaire: Questionnaire) -> QuestionnaireResponse:
        """
        Fill a questionnaire with data scraped from an organization website.
        
        Args:
            website_url: The organization's website URL
            questionnaire: The questionnaire to fill
            
        Returns:
            QuestionnaireResponse with scraped data
        """
        # Scrape the website
        scraped_data = self.scrape_organization(website_url)
        
        # Create questionnaire response
        response = QuestionnaireResponse(
            questionnaire_id=questionnaire.id,
            responses={},
            completed=False,
            created_at=time.strftime('%Y-%m-%dT%H:%M:%S'),
            updated_at=time.strftime('%Y-%m-%dT%H:%M:%S')
        )
        
        # Map scraped data to questionnaire responses
        for question in questionnaire.questions:
            if question.field_mapping:
                field_name = question.field_mapping
                if field_name in scraped_data and scraped_data[field_name] is not None:
                    response.responses[question.id] = scraped_data[field_name]
        
        # Mark as completed if we have the essential data
        essential_fields = ['name', 'description', 'location', 'contact_email']
        if all(field in response.responses for field in essential_fields):
            response.completed = True
        
        return response


def main():
    """Test the scraper with a real organization website."""
    scraper = OrganizationScraper()
    
    # Test with a real organization website
    test_url = input("Enter organization website URL: ")
    
    print(f"Scraping {test_url}...")
    scraped_data = scraper.scrape_organization(test_url)
    
    print("\nScraped Data:")
    for key, value in scraped_data.items():
        print(f"{key}: {value}")
    
    # Test questionnaire filling
    from ..utils.questionnaire_manager import QuestionnaireManager
    qm = QuestionnaireManager()
    questionnaire = qm.get_default_questionnaire()
    
    response = scraper.fill_questionnaire_from_website(test_url, questionnaire)
    
    print(f"\nQuestionnaire Response:")
    print(f"Completed: {response.completed}")
    print(f"Responses: {json.dumps(response.responses, indent=2)}")


if __name__ == "__main__":
    main() 