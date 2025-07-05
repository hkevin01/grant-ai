#!/usr/bin/env python3
"""
Direct test of WV grant scraper without package imports.
"""

import re
import socket
import time
from datetime import datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# Define minimal Grant and enum classes for testing
class GrantStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"

class FundingType(Enum):
    GRANT = "grant"
    LOAN = "loan"
    SCHOLARSHIP = "scholarship"

class EligibilityType(Enum):
    NONPROFIT = "nonprofit"
    EDUCATION = "education"
    MUNICIPALITY = "municipality"

class Grant:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Test WV Grant Scraper directly
def test_wv_scraper():
    """Test the WV grant scraper directly."""
    print("🧪 Testing WV Grant Scraper (Direct)")
    print("=" * 40)
    
    # Import WV scraper class code directly here
    class TestWVGrantScraper:
        def __init__(self):
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            self.session.timeout = (5, 15)
            
            # Define a few key sources for testing
            self.sources = {
                'wv_education': {
                    'url': 'https://wvde.us/',
                    'name': 'WV Department of Education',
                    'fallbacks': [
                        'https://www.wv.gov/education',
                        'https://wvde.us/teaching-and-learning/',
                    ]
                },
                'federal_education': {
                    'url': 'https://www.ed.gov/grants',
                    'name': 'US Department of Education',
                    'fallbacks': [
                        'https://www.ed.gov/fund/grants-apply.html'
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
        
        def _get_sample_education_grants(self, source_info):
            """Generate sample education grants."""
            sample_grants = [
                Grant(
                    id=f"sample_{int(time.time())}",
                    title="Title I School Improvement Grant",
                    description="Federal funding for schools with high percentages of low-income students",
                    funder_name=source_info['name'],
                    funder_type="Federal Government",
                    funding_type=FundingType.GRANT,
                    amount_typical=50000,
                    amount_min=25000,
                    amount_max=150000,
                    status=GrantStatus.OPEN,
                    eligibility_types=[EligibilityType.EDUCATION],
                    focus_areas=['education', 'school_improvement'],
                    source=source_info['name'],
                    source_url=source_info['url'],
                    application_url=source_info['url'],
                    last_updated=datetime.now(),
                    created_at=datetime.now()
                ),
                Grant(
                    id=f"sample_{int(time.time())}_2",
                    title="STEM Education Enhancement Grant",
                    description="Support for science, technology, engineering, and mathematics education programs",
                    funder_name=source_info['name'],
                    funder_type="Federal Government",
                    funding_type=FundingType.GRANT,
                    amount_typical=35000,
                    amount_min=15000,
                    amount_max=75000,
                    status=GrantStatus.OPEN,
                    eligibility_types=[EligibilityType.EDUCATION, EligibilityType.NONPROFIT],
                    focus_areas=['stem_education', 'technology'],
                    source=source_info['name'],
                    source_url=source_info['url'],
                    application_url=source_info['url'],
                    last_updated=datetime.now(),
                    created_at=datetime.now()
                )
            ]
            return sample_grants
        
        def test_single_source(self, source_id):
            """Test a single source."""
            source_info = self.sources[source_id]
            print(f"Testing: {source_info['name']}")
            print(f"URL: {source_info['url']}")
            
            # Check DNS resolution
            can_resolve = self._check_dns_resolution(source_info['url'])
            print(f"DNS Resolution: {'✅ Success' if can_resolve else '❌ Failed'}")
            
            if can_resolve:
                try:
                    response = self.session.get(source_info['url'], timeout=(5, 10))
                    print(f"HTTP Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        title = soup.find('title')
                        print(f"Page Title: {title.get_text().strip() if title else 'No title'}")
                        
                        # Look for grant-related content
                        grant_keywords = ['grant', 'funding', 'financial', 'assistance']
                        page_text = soup.get_text().lower()
                        found_keywords = [kw for kw in grant_keywords if kw in page_text]
                        print(f"Grant keywords found: {found_keywords}")
                        
                    else:
                        print(f"❌ HTTP Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Request Error: {e}")
            
            # Always return sample grants
            print("📝 Generating sample grants...")
            grants = self._get_sample_education_grants(source_info)
            print(f"✅ Generated {len(grants)} sample grants")
            
            for grant in grants:
                print(f"  - {grant.title}")
                print(f"    Amount: ${grant.amount_typical:,}")
                print(f"    Focus: {', '.join(grant.focus_areas)}")
            
            return grants
    
    # Run the test
    scraper = TestWVGrantScraper()
    
    print(f"📋 Available sources: {len(scraper.sources)}")
    for source_id, source_info in scraper.sources.items():
        print(f"  - {source_id}: {source_info['name']}")
    
    print("\n" + "="*50)
    
    # Test each source
    all_grants = []
    for source_id in scraper.sources:
        print(f"\n🔍 Testing {source_id}:")
        print("-" * 30)
        grants = scraper.test_single_source(source_id)
        all_grants.extend(grants)
        print()
    
    print(f"🏆 Test Complete!")
    print(f"Total grants generated: {len(all_grants)}")
    
    # Check for CODA-relevant grants
    coda_keywords = ['education', 'arts', 'youth', 'stem', 'music']
    coda_relevant = []
    
    for grant in all_grants:
        grant_text = (grant.title + " " + grant.description).lower()
        if any(keyword in grant_text for keyword in coda_keywords):
            coda_relevant.append(grant)
    
    print(f"CODA-relevant grants: {len(coda_relevant)}")
    for grant in coda_relevant:
        print(f"  - {grant.title}")

if __name__ == "__main__":
    test_wv_scraper()
