"""Rate limiter for controlling request frequency."""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Optional

from grant_ai.core.exceptions import RateLimitError


class RateLimiter:
    """
    Thread-safe rate limiter with per-domain control.

    Features:
    - Per-domain rate limiting with configurable rates
    - Global rate limiting across all domains
    - Automatic cooldown for rate-limited domains
    - Dynamic rate adjustment based on response codes
    """

    def __init__(
        self,
        requests_per_second: float = 2.0,
        burst_size: int = 5,
        cooldown_period: int = 300
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Default requests per second per domain
            burst_size: Maximum burst size per domain
            cooldown_period: Cooldown period in seconds after rate limit
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.cooldown_period = cooldown_period

        # Thread safety
        self._lock = Lock()

        # Track request timestamps per domain
        self._requests: Dict[str, list] = defaultdict(list)

        # Track rate limits per domain
        self._rates: Dict[str, float] = defaultdict(
            lambda: self.requests_per_second
        )

        # Track cooldowns
        self._cooldowns: Dict[str, float] = {}

    def wait_if_needed(self, domain: str) -> None:
        """
        Wait if necessary to respect rate limits.

        Args:
            domain: Domain to check rate limit for

        Raises:
            RateLimitError: If domain is in cooldown
        """
        with self._lock:
            # Check cooldown first
            if domain in self._cooldowns:
                cooldown_end = self._cooldowns[domain]
                if time.time() < cooldown_end:
                    raise RateLimitError(
                        f"Domain {domain} in cooldown for "
                        f"{cooldown_end - time.time():.1f}s"
                    )
                else:
                    del self._cooldowns[domain]

            # Clean old requests
            now = time.time()
            window = 1.0 / self._rates[domain]
            self._requests[domain] = [
                t for t in self._requests[domain] if now - t <= window
            ]

            # Check burst limit
            if len(self._requests[domain]) >= self.burst_size:
                sleep_time = window
                time.sleep(sleep_time)

            # Check rate limit
            if self._requests[domain]:
                elapsed = now - self._requests[domain][0]
                if elapsed < window:
                    sleep_time = window - elapsed
                    time.sleep(sleep_time)

            # Record request
            self._requests[domain].append(time.time())

    def adjust_rate(self, domain: str, success: bool) -> None:
        """
        Adjust rate limit based on success/failure.

        Args:
            domain: Domain to adjust rate for
            success: Whether request was successful
        """
        with self._lock:
            current_rate = self._rates[domain]
            if success:
                # Gradually increase rate on success
                new_rate = min(current_rate * 1.1, self.requests_per_second)
            else:
                # Sharply decrease rate on failure
                new_rate = max(current_rate * 0.5, 0.1)
            self._rates[domain] = new_rate

    def add_cooldown(
        self,
        domain: str,
        duration: Optional[int] = None
    ) -> None:
        """
        Add domain to cooldown.

        Args:
            domain: Domain to cooldown
            duration: Cooldown duration in seconds, default to cooldown_period
        """
        with self._lock:
            duration = duration or self.cooldown_period
            self._cooldowns[domain] = time.time() + duration
            # Reset rate to default after cooldown
            self._rates[domain] = self.requests_per_second

    def get_domain_status(self, domain: str) -> Dict:
        """
        Get current status for domain.

        Args:
            domain: Domain to get status for

        Returns:
            Dictionary with domain status
        """
        with self._lock:
            return {
                'current_rate': self._rates[domain],
                'request_count': len(self._requests[domain]),
                'in_cooldown': domain in self._cooldowns,
                'cooldown_remaining': max(
                    0,
                    self._cooldowns.get(domain, 0) - time.time()
                )
            }
