"""
Robust web scraping service with comprehensive error handling and recovery.
"""
import logging
import random
import socket
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from grant_ai.models.grant import Grant


class RobustWebScraper:
    """Enhanced web scraper with robust error handling, retry logic, and fallbacks."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        """
        Initialize the robust scraper with configurable retry settings.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for delay between retries
        """
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Track failed domains to avoid repeated attempts
        self.failed_domains: Set[str] = set()
        self.domain_cooldown: Dict[str, float] = {}
        
        # Initialize session with robust configuration
        self.session = self._create_robust_session()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
    
    def _create_robust_session(self) -> requests.Session:
        """Create a requests session with robust retry and timeout configuration."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        
        # Mount adapters with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set reasonable timeouts
        session.timeout = (10, 30)  # (connect_timeout, read_timeout)
        
        return session
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})
    
    def _check_domain_availability(self, url: str) -> bool:
        """
        Check if a domain is accessible and not in cooldown.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if domain is accessible, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check if domain is in failed list
            if domain in self.failed_domains:
                return False
            
            # Check cooldown period
            if domain in self.domain_cooldown:
                if time.time() - self.domain_cooldown[domain] < 300:  # 5 min cooldown
                    return False
                else:
                    # Remove from cooldown
                    del self.domain_cooldown[domain]
            
            # Test DNS resolution
            socket.gethostbyname(domain)
            return True
            
        except (socket.gaierror, socket.error, Exception) as e:
            self.logger.warning(f"Domain check failed for {url}: {e}")
            return False
    
    def _handle_request_error(self, url: str, error: Exception, attempt: int) -> bool:
        """
        Handle request errors with appropriate recovery strategies.
        
        Args:
            url: URL that failed
            error: Exception that occurred
            attempt: Current attempt number
            
        Returns:
            bool: True if should retry, False otherwise
        """
        domain = urlparse(url).netloc
        
        if isinstance(error, requests.exceptions.ConnectionError):
            self.logger.warning(f"Connection error for {url} (attempt {attempt}): {error}")
            if attempt >= self.max_retries:
                self.failed_domains.add(domain)
                self.domain_cooldown[domain] = time.time()
            return attempt < self.max_retries
        
        elif isinstance(error, requests.exceptions.Timeout):
            self.logger.warning(f"Timeout for {url} (attempt {attempt}): {error}")
            # Increase timeout for retry
            self.session.timeout = (self.session.timeout[0] * 1.5, self.session.timeout[1] * 1.5)
            return attempt < self.max_retries
        
        elif isinstance(error, requests.exceptions.HTTPError):
            status_code = getattr(error.response, 'status_code', None)
            self.logger.warning(f"HTTP error {status_code} for {url} (attempt {attempt}): {error}")
            
            if status_code == 403:
                # Forbidden - try rotating user agent
                self._rotate_user_agent()
                time.sleep(random.uniform(2, 5))  # Random delay
                return attempt < self.max_retries
            
            elif status_code == 404:
                # Not found - don't retry
                self.logger.info(f"URL not found: {url}")
                return False
            
            elif status_code in [429, 503]:
                # Rate limited or service unavailable - longer delay
                delay = (2 ** attempt) + random.uniform(1, 3)
                time.sleep(delay)
                return attempt < self.max_retries
            
            else:
                return attempt < self.max_retries
        
        else:
            self.logger.error(f"Unexpected error for {url} (attempt {attempt}): {error}")
            return attempt < self.max_retries
    
    def fetch_with_fallbacks(self, url: str, fallback_urls: Optional[List[str]] = None) -> Optional[BeautifulSoup]:
        """
        Fetch URL content with comprehensive error handling and fallbacks.
        
        Args:
            url: Primary URL to fetch
            fallback_urls: List of fallback URLs to try if primary fails
            
        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        urls_to_try = [url] + (fallback_urls or [])
        
        for current_url in urls_to_try:
            if not self._check_domain_availability(current_url):
                self.logger.info(f"Skipping unavailable domain: {current_url}")
                continue
            
            for attempt in range(1, self.max_retries + 1):
                try:
                    # Rotate user agent for each attempt
                    self._rotate_user_agent()
                    
                    # Add random delay to avoid being flagged
                    if attempt > 1:
                        delay = random.uniform(1, 3) * attempt
                        time.sleep(delay)
                    
                    self.logger.info(f"Fetching {current_url} (attempt {attempt})")
                    
                    response = self.session.get(current_url)
                    response.raise_for_status()
                    
                    # Successful response
                    if response.content:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        self.logger.info(f"Successfully fetched {current_url}")
                        return soup
                    else:
                        self.logger.warning(f"Empty response from {current_url}")
                        continue
                
                except Exception as error:
                    should_retry = self._handle_request_error(current_url, error, attempt)
                    if not should_retry:
                        break
            
            # Reset session timeout for next URL
            self.session.timeout = (10, 30)
        
        self.logger.error(f"Failed to fetch any URL: {urls_to_try}")
        return None
    
    def extract_grants_with_selectors(self, soup: BeautifulSoup, selectors: Dict[str, List[str]]) -> List[Grant]:
        """
        Extract grants using multiple CSS selectors with fallbacks.
        
        Args:
            soup: BeautifulSoup object to parse
            selectors: Dictionary of CSS selectors for different grant elements
            
        Returns:
            List of extracted grants
        """
        grants = []
        
        try:
            # Try multiple selectors for grant containers
            grant_containers = []
            for selector in selectors.get('containers', []):
                containers = soup.select(selector)
                if containers:
                    grant_containers.extend(containers)
                    break
            
            if not grant_containers:
                self.logger.warning("No grant containers found with provided selectors")
                return []
            
            for container in grant_containers[:20]:  # Limit to 20 grants
                try:
                    grant = self._extract_single_grant(container, selectors)
                    if grant:
                        grants.append(grant)
                except Exception as e:
                    self.logger.warning(f"Failed to extract grant from container: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error extracting grants: {e}")
        
        return grants
    
    def _extract_single_grant(self, container, selectors: Dict[str, List[str]]) -> Optional[Grant]:
        """Extract a single grant from a container element."""
        try:
            # Extract title
            title = self._extract_text_with_selectors(container, selectors.get('title', []))
            if not title:
                return None
            
            # Extract other fields with fallbacks
            description = self._extract_text_with_selectors(container, selectors.get('description', []))
            amount = self._extract_text_with_selectors(container, selectors.get('amount', []))
            deadline = self._extract_text_with_selectors(container, selectors.get('deadline', []))
            funder = self._extract_text_with_selectors(container, selectors.get('funder', []))
            
            # Create grant object
            grant = Grant(
                title=title,
                description=description or "No description available",
                funder_name=funder or "Unknown Funder",
                amount_min=self._parse_amount(amount),
                deadline=deadline,
                url="",  # Will be set by caller
                source="Web Scraping"
            )
            
            return grant
            
        except Exception as e:
            self.logger.warning(f"Error extracting single grant: {e}")
            return None
    
    def _extract_text_with_selectors(self, container, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple CSS selectors as fallbacks."""
        for selector in selectors:
            try:
                element = container.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        return None
    
    def _parse_amount(self, amount_text: Optional[str]) -> Optional[int]:
        """Parse amount from text, handling various formats."""
        if not amount_text:
            return None
        
        try:
            # Remove common currency symbols and text
            import re
            amount_clean = re.sub(r'[^\d,.]', '', amount_text.replace(',', ''))
            if amount_clean:
                return int(float(amount_clean))
        except (ValueError, TypeError):
            pass
        
        return None
    
    def health_check(self) -> Dict[str, any]:
        """
        Perform a health check of the scraper.
        
        Returns:
            Dictionary with health status information
        """
        return {
            'failed_domains_count': len(self.failed_domains),
            'failed_domains': list(self.failed_domains),
            'domains_in_cooldown': len(self.domain_cooldown),
            'session_active': self.session is not None,
            'max_retries': self.max_retries,
            'backoff_factor': self.backoff_factor
        }
    
    def reset_failed_domains(self):
        """Reset the failed domains list and cooldowns."""
        self.failed_domains.clear()
        self.domain_cooldown.clear()
        self.logger.info("Reset failed domains and cooldowns")
    
    def scrape_grants(
        self, url: str, selectors: Optional[Dict[str, List[str]]] = None
    ) -> List[Grant]:
        """
        Scrape grants from a URL using intelligent content extraction.
        
        Args:
            url: URL to scrape
            selectors: Optional custom selectors for grant extraction
            
        Returns:
            List of extracted grants
        """
        try:
            # Fetch the page content
            soup = self.fetch_with_fallbacks(url)
            if not soup:
                self.logger.warning(f"Failed to fetch content from {url}")
                return []
            
            # Use provided selectors or intelligent defaults
            if selectors:
                return self.extract_grants_with_selectors(soup, selectors)
            else:
                # Use intelligent content extraction with default selectors
                default_selectors = {
                    'container': [
                        '.grant', '.funding', '.opportunity', '.award',
                        '[class*="grant"]', '[class*="funding"]',
                        '[class*="opportunity"]',
                        'article', '.content-item', '.listing-item', '.card',
                        '.result-item', '.search-result'
                    ],
                    'title': [
                        'h1', 'h2', 'h3', 'h4', '.title', '.name', '.heading',
                        '[class*="title"]', '[class*="name"]',
                        '[class*="heading"]'
                    ],
                    'description': [
                        'p', '.description', '.summary', '.excerpt',
                        '.content',
                        '[class*="description"]', '[class*="summary"]', '.text'
                    ],
                    'amount': [
                        '.amount', '.funding', '.award', '[class*="amount"]',
                        '[class*="funding"]', '[class*="money"]',
                        '[class*="dollar"]'
                    ],
                    'deadline': [
                        '.deadline', '.due', '.expires', '[class*="deadline"]',
                        '[class*="due"]', '[class*="expire"]', 'time', '.date'
                    ],
                    'link': [
                        'a[href]', '.link', '[class*="link"]', '.read-more'
                    ]
                }
                return self.extract_grants_with_selectors(
                    soup, default_selectors
                )
                
        except Exception as e:
            self.logger.error(f"Error scraping grants from {url}: {e}")
            return []
