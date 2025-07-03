#!/usr/bin/env python3
"""
Demonstration of enhanced web scraping with robust error handling.
This shows how the improvements fix the original Grant AI scraping issues.
"""
import logging
import random
import socket
import time
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DemoRobustScraper:
    """Demonstration of robust web scraping techniques."""
    
    def __init__(self):
        """Initialize the demo scraper."""
        self.session = requests.Session()
        self.failed_domains = set()
        self.domain_cooldown = {}
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def check_dns_resolution(self, url: str) -> bool:
        """Check if a domain can be resolved."""
        try:
            parsed = urlparse(url)
            socket.gethostbyname(parsed.netloc)
            return True
        except socket.gaierror:
            return False
    
    def rotate_user_agent(self):
        """Rotate user agent to avoid detection."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})
    
    def fetch_with_fallbacks(self, url: str, fallback_urls: list = None):
        """Fetch URL with comprehensive error handling and fallbacks."""
        urls_to_try = [url] + (fallback_urls or [])
        
        for current_url in urls_to_try:
            print(f"🔍 Trying: {current_url}")
            
            # Check DNS first
            if not self.check_dns_resolution(current_url):
                print(f"  ❌ DNS resolution failed, skipping...")
                continue
            
            # Try with retry logic
            for attempt in range(1, 4):  # 3 attempts
                try:
                    # Rotate user agent
                    self.rotate_user_agent()
                    
                    # Add delay for subsequent attempts
                    if attempt > 1:
                        delay = (2 ** attempt) + random.uniform(0.5, 1.5)
                        print(f"  ⏳ Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                    
                    print(f"  📡 Attempt {attempt}/3...")
                    response = self.session.get(current_url, timeout=(10, 30))
                    
                    if response.status_code == 200:
                        print(f"  ✅ Success! Status: {response.status_code}")
                        return response
                    elif response.status_code == 403:
                        print(f"  ⚠️  Forbidden (403) - trying user agent rotation...")
                        continue
                    elif response.status_code == 404:
                        print(f"  ❌ Not Found (404) - trying fallback URL...")
                        break  # Try next URL
                    else:
                        print(f"  ⚠️  Status {response.status_code} - retrying...")
                        continue
                        
                except requests.exceptions.ConnectionError:
                    print(f"  ❌ Connection error on attempt {attempt}")
                except requests.exceptions.Timeout:
                    print(f"  ⏰ Timeout on attempt {attempt}")
                except Exception as e:
                    print(f"  ❌ Unexpected error: {e}")
                
        print(f"  💀 All attempts failed for {url}")
        return None


def demo_enhanced_scraping():
    """Demonstrate enhanced scraping on the problematic WV grant URLs."""
    print("🚀 Enhanced Web Scraping Demo")
    print("=" * 50)
    print("This demonstrates how our improvements handle the original errors:")
    print("- 403 Forbidden errors with user agent rotation")
    print("- 404 Not Found errors with fallback URLs") 
    print("- DNS resolution failures with smart skipping")
    print("- Retry logic with exponential backoff")
    print()
    
    # Original problematic URLs
    test_cases = [
        {
            'name': 'WV Arts Commission',
            'url': 'https://wvculture.org/arts/grants/',
            'fallbacks': [
                'https://wvculture.org/arts/grants-funding/',
                'https://wvculture.org/grants/'
            ]
        },
        {
            'name': 'WV Department of Education',
            'url': 'https://wvde.us/grants/',
            'fallbacks': [
                'https://wvde.us/federal-programs/',
                'https://wvde.state.wv.us/grants/'
            ]
        },
        {
            'name': 'WV Department of Commerce',
            'url': 'https://wvcommerce.org/business/grants/',
            'fallbacks': [
                'https://wvcommerce.org/business/assistance/',
                'https://wvcommerce.org/programs/'
            ]
        },
        {
            'name': 'WV Department of Health',
            'url': 'https://dhhr.wv.gov/grants/',
            'fallbacks': [
                'https://dhhr.wv.gov/programs/',
                'https://dhhr.wv.gov/funding/'
            ]
        }
    ]
    
    scraper = DemoRobustScraper()
    
    for test_case in test_cases:
        print(f"📋 Testing: {test_case['name']}")
        print("-" * 40)
        
        response = scraper.fetch_with_fallbacks(
            test_case['url'], 
            test_case['fallbacks']
        )
        
        if response:
            print(f"  🎉 SUCCESS: Got {len(response.content)} bytes of content")
            print(f"  📊 Final URL: {response.url}")
        else:
            print(f"  😔 FAILED: No accessible URLs found")
        
        print()
        
        # Pause between requests
        time.sleep(2)
    
    print("🎯 Summary:")
    print("- Enhanced error handling prevents crashes")
    print("- Fallback URLs provide alternatives when primary sources fail")
    print("- User agent rotation helps bypass 403 Forbidden errors")
    print("- DNS checking prevents hanging on unreachable domains")
    print("- Retry logic with backoff handles temporary failures")
    print()
    print("✨ Result: Robust, crash-free grant searching!")


if __name__ == "__main__":
    demo_enhanced_scraping()
