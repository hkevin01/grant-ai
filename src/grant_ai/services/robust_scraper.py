"""
Robust web scraping service with comprehensive error handling.
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

from grant_ai.core.exceptions import NetworkError, ParsingError, RateLimitError
from grant_ai.models.grant import Grant
from grant_ai.services.rate_limiter import RateLimiter


class RobustWebScraper:
    """Web scraper with advanced error handling and rate limiting."""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        """Initialize scraper with configurable settings."""
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_second=2.0,
            burst_size=5,
            cooldown_period=300
        )

        # Track failed domains
        self.failed_domains: Set[str] = set()

        # Initialize session
        self.session = self._create_robust_session()

        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0) Chrome/120.0',
            'Mozilla/5.0 (Macintosh) Chrome/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0',
            'Mozilla/5.0 (Windows NT 10.0) Firefox/121.0',
            'Mozilla/5.0 (Macintosh) Firefox/121.0'
        ]

    def _create_robust_session(self) -> requests.Session:
        """Create requests session with retry and timeout config."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.timeout = (10, 30)

        return session

    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection."""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': user_agent})

    def _check_domain_availability(self, url: str) -> bool:
        """Check if domain is accessible."""
        try:
            domain = urlparse(url).netloc

            if domain in self.failed_domains:
                return False

            socket.gethostbyname(domain)
            return True

        except Exception as e:
            self.logger.warning(
                "Domain check failed for %s: %s",
                url, str(e)
            )
            return False

    def _handle_request_error(
        self,
        url: str,
        error: Exception,
        attempt: int
    ) -> bool:
        """Handle request errors with appropriate strategies."""
        domain = urlparse(url).netloc

        if isinstance(error, requests.exceptions.ConnectionError):
            self.logger.warning(
                "Connection error for %s (attempt %d): %s",
                url, attempt, error
            )
            if attempt >= self.max_retries:
                self.failed_domains.add(domain)
                self.rate_limiter.add_cooldown(domain)
            return attempt < self.max_retries

        elif isinstance(error, requests.exceptions.Timeout):
            self.logger.warning(
                "Timeout for %s (attempt %d): %s",
                url, attempt, error
            )
            # Increase timeout for retry
            self.session.timeout = (
                self.session.timeout[0] * 1.5,
                self.session.timeout[1] * 1.5
            )
            return attempt < self.max_retries

        elif isinstance(error, requests.exceptions.HTTPError):
            status_code = getattr(error.response, 'status_code', None)
            self.logger.warning(
                "HTTP error %s for %s (attempt %d): %s",
                status_code, url, attempt, error
            )

            if status_code == 403:
                self._rotate_user_agent()
                time.sleep(random.uniform(2, 5))
                return attempt < self.max_retries

            elif status_code == 404:
                self.logger.info("URL not found: %s", url)
                return False

            elif status_code in [429, 503]:
                # Rate limited - add cooldown
                self.rate_limiter.add_cooldown(
                    domain,
                    duration=60 * (2 ** attempt)
                )
                return attempt < self.max_retries

            return attempt < self.max_retries

        else:
            self.logger.error(
                "Unexpected error for %s (attempt %d): %s",
                url, attempt, error
            )
            return attempt < self.max_retries

    def fetch_with_fallbacks(
        self,
        url: str,
        fallback_urls: Optional[List[str]] = None
    ) -> Optional[BeautifulSoup]:
        """Fetch URL content with error handling and fallbacks."""
        urls_to_try = [url] + (fallback_urls or [])

        for current_url in urls_to_try:
            domain = urlparse(current_url).netloc

            if not self._check_domain_availability(current_url):
                self.logger.info("Skipping unavailable: %s", current_url)
                continue

            for attempt in range(1, self.max_retries + 1):
                try:
                    # Wait for rate limit
                    self.rate_limiter.wait_if_needed(domain)

                    # Rotate user agent
                    self._rotate_user_agent()

                    # Add random delay for retries
                    if attempt > 1:
                        delay = random.uniform(1, 3) * attempt
                        time.sleep(delay)

                    self.logger.info(
                        "Fetching %s (attempt %d)",
                        current_url, attempt
                    )

                    response = self.session.get(current_url)
                    response.raise_for_status()

                    if response.content:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        self.logger.info(
                            "Successfully fetched %s",
                            current_url
                        )
                        self.rate_limiter.adjust_rate(domain, True)
                        return soup
                    else:
                        self.logger.warning(
                            "Empty response from %s",
                            current_url
                        )
                        continue

                except Exception as error:
                    self.rate_limiter.adjust_rate(domain, False)
                    should_retry = self._handle_request_error(
                        current_url, error, attempt
                    )
                    if not should_retry:
                        break

            # Reset session timeout
            self.session.timeout = (10, 30)

        self.logger.error("Failed to fetch any URL: %s", urls_to_try)
        return None

    def extract_grants_with_selectors(
        self,
        soup: BeautifulSoup,
        selectors: Dict[str, List[str]]
    ) -> List[Grant]:
        """Extract grants using multiple CSS selectors."""
        grants = []

        try:
            # Find all potential grant containers
            containers = []
            for container_selector in selectors.get('container', []):
                containers.extend(soup.select(container_selector))

            # Process each container
            for container in containers[:10]:  # Limit to avoid overload
                try:
                    grant = self._extract_single_grant(
                        container, selectors
                    )
                    if grant:
                        grants.append(grant)
                except Exception as e:
                    self.logger.warning(
                        "Failed to extract grant: %s",
                        str(e)
                    )
                    continue

        except Exception as e:
            self.logger.error("Error extracting grants: %s", str(e))
            raise ParsingError(f"Failed to extract grants: {e}")

        return grants

    def _extract_field(
        self,
        container: BeautifulSoup,
        selectors: List[str],
        get_href: bool = False
    ) -> Optional[str]:
        """Extract a field using multiple selectors."""
        for selector in selectors:
            elem = container.select_one(selector)
            if elem:
                if get_href and elem.get('href'):
                    return elem['href']
                return elem.get_text(strip=True)
        return None

    def _extract_single_grant(
        self,
        container: BeautifulSoup,
        selectors: Dict[str, List[str]]
    ) -> Optional[Grant]:
        """Extract grant details from a single container element."""
        try:
            title = self._extract_field(
                container,
                selectors.get('title', [])
            )

            if not title:
                return None

            description = self._extract_field(
                container,
                selectors.get('description', [])
            )

            amount = self._extract_field(
                container,
                selectors.get('amount', [])
            )

            deadline = self._extract_field(
                container,
                selectors.get('deadline', [])
            )

            link = self._extract_field(
                container,
                selectors.get('link', []),
                get_href=True
            )

            return Grant(
                title=title,
                description=description or "",
                amount=amount,
                deadline=deadline,
                url=link
            )

        except Exception as e:
            self.logger.warning(
                "Error extracting grant details: %s",
                str(e)
            )
            return None

    def scrape_grants(
        self,
        url: str,
        selectors: Optional[Dict[str, List[str]]] = None
    ) -> List[Grant]:
        """Scrape grants with intelligent extraction."""
        try:
            soup = self.fetch_with_fallbacks(url)
            if not soup:
                self.logger.warning("Failed to fetch: %s", url)
                return []

            # Use provided or default selectors
            if selectors:
                return self.extract_grants_with_selectors(
                    soup, selectors
                )
            else:
                # Default selectors for common patterns
                default_selectors = {
                    'container': [
                        '.grant', '.funding', '.opportunity',
                        '.award', '[class*="grant"]',
                        '[class*="funding"]', '[class*="opportunity"]',
                        'article', '.content-item', '.listing-item'
                    ],
                    'title': [
                        'h1', 'h2', 'h3', 'h4', '.title',
                        '.name', '.heading', '[class*="title"]'
                    ],
                    'description': [
                        'p', '.description', '.summary',
                        '.excerpt', '.content', '[class*="description"]'
                    ],
                    'amount': [
                        '.amount', '.funding', '.award',
                        '[class*="amount"]', '[class*="funding"]'
                    ],
                    'deadline': [
                        '.deadline', '.due', '.expires',
                        '[class*="deadline"]', '[class*="due"]'
                    ],
                    'link': ['a[href]', '.link', '[class*="link"]']
                }
                return self.extract_grants_with_selectors(
                    soup, default_selectors
                )

        except RateLimitError as e:
            self.logger.warning("Rate limited: %s", str(e))
            return []

        except NetworkError as e:
            self.logger.error("Network error: %s", str(e))
            return []

        except Exception as e:
            self.logger.error("Error scraping grants: %s", str(e))
            return []

    def health_check(self) -> Dict:
        """Get health status of scraper."""
        return {
            'failed_domains_count': len(self.failed_domains),
            'failed_domains': list(self.failed_domains),
            'session_active': bool(self.session),
            'rate_limiter_status': {
                domain: self.rate_limiter.get_domain_status(domain)
                for domain in self.failed_domains
            }
        }

    def reset_failed_domains(self):
        """Reset failed domains list and rate limiter."""
        self.failed_domains.clear()
        for domain in self.failed_domains:
            self.rate_limiter.adjust_rate(domain, True)
