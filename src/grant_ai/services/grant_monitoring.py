"""
Real-time Grant Monitoring Service.

This service continuously monitors grant databases (NASA, ESA,
Grants.gov, NSF, DOE) for new opportunities and sends notifications
when matches are found.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer
from grant_ai.core.exceptions import NetworkError, RateLimitError
from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile
from grant_ai.services.robust_scraper import RobustWebScraper


class GrantMonitoringService:
    """Real-time monitoring service for grant opportunities."""

    def __init__(
        self,
        data_dir: str = "data",
        min_relevance_score: float = 0.6
    ):
        """Initialize the monitoring service."""
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.min_relevance_score = min_relevance_score

        # Create monitoring data directory
        self.monitoring_dir = self.data_dir / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)

        # Cache files
        self.cache_file = self.monitoring_dir / "grant_cache.json"
        self.seen_grants_file = self.monitoring_dir / "seen_grants.json"
        self.subscriptions_file = self.monitoring_dir / "subscriptions.json"

        # Initialize components
        self.scraper = RobustWebScraper()
        self.scorer = GrantRelevanceScorer()

        # Monitoring state
        self.seen_grants: Set[str] = self._load_seen_grants()
        self.subscriptions: Dict[str, OrganizationProfile] = (
            self._load_subscriptions()
        )
        self.is_running = False

        # Grant source configurations
        self.grant_sources = {
            'nasa': {
                'url': 'https://nspires.nasaprs.com/external/',
                'check_interval': 3600,  # 1 hour
                'selectors': {
                    'container': ['.opportunity-item', '.grant-listing'],
                    'title': ['h2', 'h3', '.title'],
                    'description': ['.description', '.summary'],
                    'deadline': ['.deadline', '.due-date'],
                    'link': ['a[href]']
                }
            },
            'esa': {
                'url': 'https://www.esa.int/Applications/Observing_the_Earth',
                'check_interval': 3600,
                'selectors': {
                    'container': ['.news-item', '.opportunity'],
                    'title': ['h2', 'h3'],
                    'description': ['.content', '.summary'],
                    'link': ['a[href]']
                }
            },
            'grants_gov': {
                'url': 'https://www.grants.gov/web/grants/search-grants.html',
                'check_interval': 1800,  # 30 minutes
                'selectors': {
                    'container': ['.search-result-item'],
                    'title': ['.opportunity-title'],
                    'description': ['.opportunity-description'],
                    'deadline': ['.close-date'],
                    'amount': ['.award-ceiling'],
                    'link': ['a[href]']
                }
            },
            'nsf': {
                'url': 'https://www.nsf.gov/funding/',
                'check_interval': 3600,
                'selectors': {
                    'container': ['.funding-opportunity'],
                    'title': ['h3', '.title'],
                    'description': ['.description'],
                    'deadline': ['.deadline'],
                    'link': ['a[href]']
                }
            },
            'doe': {
                'url': 'https://www.energy.gov/science/grants-and-contracts',
                'check_interval': 3600,
                'selectors': {
                    'container': ['.funding-opportunity'],
                    'title': ['h2', 'h3'],
                    'description': ['.summary'],
                    'deadline': ['.deadline'],
                    'link': ['a[href]']
                }
            }
        }

        self.logger.info("Grant monitoring service initialized")

    def add_subscription(
        self,
        organization: OrganizationProfile,
        notification_settings: Optional[Dict] = None
    ) -> bool:
        """Add an organization subscription for monitoring."""
        try:
            org_id = self._generate_org_id(organization)
            self.subscriptions[org_id] = organization

            # Save subscription settings
            if notification_settings:
                settings_file = self.monitoring_dir / f"{org_id}_settings.json"
                with open(settings_file, 'w') as f:
                    json.dump(notification_settings, f, indent=2)

            self._save_subscriptions()

            self.logger.info(
                "Added subscription for organization: %s",
                organization.name
            )
            return True

        except Exception as e:
            self.logger.error(
                "Error adding subscription: %s", str(e)
            )
            return False

    def remove_subscription(self, organization_name: str) -> bool:
        """Remove an organization subscription."""
        try:
            org_id = None
            for oid, org in self.subscriptions.items():
                if org.name == organization_name:
                    org_id = oid
                    break

            if org_id:
                del self.subscriptions[org_id]
                self._save_subscriptions()

                # Remove settings file
                settings_file = self.monitoring_dir / f"{org_id}_settings.json"
                if settings_file.exists():
                    settings_file.unlink()

                self.logger.info(
                    "Removed subscription for: %s", organization_name
                )
                return True

            return False

        except Exception as e:
            self.logger.error(
                "Error removing subscription: %s", str(e)
            )
            return False

    async def start_monitoring(self) -> None:
        """Start the real-time monitoring service."""
        if self.is_running:
            self.logger.warning("Monitoring service is already running")
            return

        self.is_running = True
        self.logger.info("Starting grant monitoring service...")

        if not self.subscriptions:
            self.logger.warning("No subscriptions found - adding sample data")
            await self._add_sample_subscriptions()

        # Create monitoring tasks for each source
        tasks = []
        for source_name, config in self.grant_sources.items():
            task = asyncio.create_task(
                self._monitor_source(source_name, config)
            )
            tasks.append(task)

        # Create notification processing task
        notification_task = asyncio.create_task(
            self._process_notifications()
        )
        tasks.append(notification_task)

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("Monitoring service interrupted by user")
        except Exception as e:
            self.logger.error("Error in monitoring service: %s", str(e))
        finally:
            self.is_running = False
            self.logger.info("Grant monitoring service stopped")

    async def stop_monitoring(self) -> None:
        """Stop the monitoring service."""
        self.is_running = False
        self.logger.info("Stopping grant monitoring service...")

    async def _monitor_source(self, source_name: str, config: Dict) -> None:
        """Monitor a specific grant source for new opportunities."""
        check_interval = config['check_interval']

        while self.is_running:
            try:
                self.logger.info(
                    "Checking %s for new grants...", source_name
                )

                # Scrape grants from source
                new_grants = await self._scrape_source(source_name, config)

                if new_grants:
                    self.logger.info(
                        "Found %d new grants from %s",
                        len(new_grants), source_name
                    )

                    # Process new grants for all subscriptions
                    await self._process_new_grants(new_grants, source_name)

                # Wait before next check
                await asyncio.sleep(check_interval)

            except RateLimitError:
                self.logger.warning(
                    "Rate limited by %s, waiting longer...", source_name
                )
                await asyncio.sleep(check_interval * 2)
            except NetworkError as e:
                self.logger.warning(
                    "Network error with %s: %s", source_name, str(e)
                )
                await asyncio.sleep(check_interval)
            except Exception as e:
                self.logger.error(
                    "Error monitoring %s: %s", source_name, str(e)
                )
                await asyncio.sleep(check_interval)

    async def _scrape_source(
        self, source_name: str, config: Dict
    ) -> List[Grant]:
        """Scrape grants from a specific source."""
        try:
            # Use the robust scraper to get grants
            grants = self.scraper.scrape_grants(
                config['url'],
                config['selectors']
            )

            # Filter out grants we've already seen
            new_grants = []
            for grant in grants:
                grant_id = self._generate_grant_id(grant)
                if grant_id not in self.seen_grants:
                    grant.source = source_name
                    grant.source_url = config['url']
                    new_grants.append(grant)
                    self.seen_grants.add(grant_id)

            if new_grants:
                self._save_seen_grants()

            return new_grants

        except Exception as e:
            self.logger.error(
                "Error scraping %s: %s", source_name, str(e)
            )
            return []

    async def _process_new_grants(
        self, grants: List[Grant], source: str
    ) -> None:
        """Process new grants against all subscriptions."""
        for org_id, organization in self.subscriptions.items():
            try:
                # Score grants for this organization
                relevant_grants = []

                for grant in grants:
                    score_breakdown = self.scorer.calculate_relevance_score(
                        grant, organization
                    )

                    if score_breakdown['final_score'] >= self.min_relevance_score:
                        grant.relevance_score = score_breakdown['final_score']
                        grant.score_breakdown = score_breakdown
                        relevant_grants.append(grant)

                if relevant_grants:
                    # Create notification
                    await self._create_notification(
                        organization, relevant_grants, source
                    )

                    self.logger.info(
                        "Found %d relevant grants for %s from %s",
                        len(relevant_grants), organization.name, source
                    )

            except Exception as e:
                self.logger.error(
                    "Error processing grants for %s: %s",
                    organization.name, str(e)
                )

    async def _create_notification(
        self,
        organization: OrganizationProfile,
        grants: List[Grant],
        source: str
    ) -> None:
        """Create and queue a notification for new relevant grants."""
        try:
            notification = {
                'timestamp': datetime.now().isoformat(),
                'organization': organization.name,
                'organization_id': self._generate_org_id(organization),
                'source': source,
                'grant_count': len(grants),
                'grants': [
                    {
                        'title': grant.title,
                        'description': grant.description[:200] + '...'
                                     if len(grant.description) > 200
                                     else grant.description,
                        'relevance_score': grant.relevance_score,
                        'deadline': grant.application_deadline.isoformat()
                                  if grant.application_deadline else None,
                        'amount': grant.amount_typical,
                        'url': grant.application_url or grant.information_url,
                        'score_breakdown': getattr(grant, 'score_breakdown', {})
                    }
                    for grant in grants
                ]
            }

            # Save notification to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            org_id = self._generate_org_id(organization)
            notification_file = (
                self.monitoring_dir /
                f"notification_{org_id}_{timestamp}.json"
            )

            with open(notification_file, 'w') as f:
                json.dump(notification, f, indent=2)

            self.logger.info(
                "Created notification for %s: %d grants from %s",
                organization.name, len(grants), source
            )

        except Exception as e:
            self.logger.error(
                "Error creating notification: %s", str(e)
            )

    async def _process_notifications(self) -> None:
        """Process and send pending notifications."""
        while self.is_running:
            try:
                # Check for notification files
                notification_files = list(
                    self.monitoring_dir.glob("notification_*.json")
                )

                for notification_file in notification_files:
                    try:
                        with open(notification_file, 'r') as f:
                            notification = json.load(f)

                        # Process notification (email, webhook, etc.)
                        await self._send_notification(notification)

                        # Move processed notification to archive
                        archive_dir = self.monitoring_dir / "archive"
                        archive_dir.mkdir(exist_ok=True)

                        archive_path = archive_dir / notification_file.name
                        notification_file.rename(archive_path)

                    except Exception as e:
                        self.logger.error(
                            "Error processing notification file %s: %s",
                            notification_file, str(e)
                        )

                # Wait before checking again
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(
                    "Error in notification processing: %s", str(e)
                )
                await asyncio.sleep(60)

    async def _send_notification(self, notification: Dict) -> None:
        """Send notification via configured channels."""
        try:
            org_id = notification['organization_id']

            # Load notification settings
            settings_file = self.monitoring_dir / f"{org_id}_settings.json"
            settings = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)

            # Log notification (always enabled)
            self.logger.info(
                "GRANT ALERT: %d new grants found for %s from %s",
                notification['grant_count'],
                notification['organization'],
                notification['source']
            )

            # Email notification (if configured)
            if settings.get('email_enabled', False):
                await self._send_email_notification(notification, settings)

            # Webhook notification (if configured)
            if settings.get('webhook_enabled', False):
                await self._send_webhook_notification(notification, settings)

            # Console notification (for testing)
            if settings.get('console_enabled', True):
                self._print_console_notification(notification)

        except Exception as e:
            self.logger.error(
                "Error sending notification: %s", str(e)
            )

    async def _send_email_notification(
        self, notification: Dict, settings: Dict
    ) -> None:
        """Send email notification (placeholder for actual implementation)."""
        # TODO: Implement email sending with SMTP
        self.logger.info(
            "Email notification would be sent to: %s",
            settings.get('email_address', 'not_configured')
        )

    async def _send_webhook_notification(
        self, notification: Dict, settings: Dict
    ) -> None:
        """Send webhook notification (placeholder for actual implementation)."""
        # TODO: Implement webhook sending with HTTP POST
        self.logger.info(
            "Webhook notification would be sent to: %s",
            settings.get('webhook_url', 'not_configured')
        )

    def _print_console_notification(self, notification: Dict) -> None:
        """Print notification to console."""
        print("\n" + "="*60)
        print(f"🚨 GRANT ALERT for {notification['organization']}")
        print("="*60)
        print(f"Source: {notification['source']}")
        print(f"New Grants Found: {notification['grant_count']}")
        print(f"Timestamp: {notification['timestamp']}")
        print("\nGrant Details:")

        for i, grant in enumerate(notification['grants'], 1):
            print(f"\n{i}. {grant['title']}")
            print(f"   Relevance Score: {grant['relevance_score']:.2f}")
            if grant['deadline']:
                print(f"   Deadline: {grant['deadline']}")
            if grant['amount']:
                print(f"   Amount: ${grant['amount']:,}")
            if grant['url']:
                print(f"   URL: {grant['url']}")
            print(f"   Description: {grant['description']}")

        print("\n" + "="*60 + "\n")

    def _generate_grant_id(self, grant: Grant) -> str:
        """Generate unique ID for grant to track if we've seen it."""
        content = f"{grant.title}_{grant.description[:100]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _generate_org_id(self, organization: OrganizationProfile) -> str:
        """Generate unique ID for organization."""
        content = f"{organization.name}_{organization.description[:50]}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _load_seen_grants(self) -> Set[str]:
        """Load previously seen grant IDs."""
        if self.seen_grants_file.exists():
            try:
                with open(self.seen_grants_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                self.logger.warning(
                    "Error loading seen grants: %s", str(e)
                )
        return set()

    def _save_seen_grants(self) -> None:
        """Save seen grant IDs to file."""
        try:
            with open(self.seen_grants_file, 'w') as f:
                json.dump(list(self.seen_grants), f)
        except Exception as e:
            self.logger.error(
                "Error saving seen grants: %s", str(e)
            )

    def _load_subscriptions(self) -> Dict[str, OrganizationProfile]:
        """Load organization subscriptions."""
        if self.subscriptions_file.exists():
            try:
                with open(self.subscriptions_file, 'r') as f:
                    data = json.load(f)

                subscriptions = {}
                for org_id, org_data in data.items():
                    subscriptions[org_id] = OrganizationProfile(**org_data)

                return subscriptions
            except Exception as e:
                self.logger.warning(
                    "Error loading subscriptions: %s", str(e)
                )
        return {}

    def _save_subscriptions(self) -> None:
        """Save subscriptions to file."""
        try:
            data = {}
            for org_id, org in self.subscriptions.items():
                data[org_id] = org.dict()

            with open(self.subscriptions_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(
                "Error saving subscriptions: %s", str(e)
            )

    async def _add_sample_subscriptions(self) -> None:
        """Add sample organization subscriptions for testing."""
        from grant_ai.utils.generate_sample_data import create_sample_organizations

        sample_orgs = create_sample_organizations()
        for org in sample_orgs:
            self.add_subscription(org, {
                'console_enabled': True,
                'email_enabled': False,
                'webhook_enabled': False
            })

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring service status."""
        return {
            'is_running': self.is_running,
            'subscriptions_count': len(self.subscriptions),
            'seen_grants_count': len(self.seen_grants),
            'sources': list(self.grant_sources.keys()),
            'min_relevance_score': self.min_relevance_score,
            'data_directory': str(self.data_dir)
        }
