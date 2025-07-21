"""
Grant Platform Integration Manager

This module provides a unified interface for integrating with external grant
discovery platforms while maintaining compliance and attribution.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from grant_ai.models import Grant, OrganizationProfile


@dataclass
class IntegrationResult:
    """Result from a platform integration."""

    platform: str
    grants: list[Grant]
    success: bool
    message: str
    timestamp: datetime
    confidence_score: float = 0.0


class PlatformIntegration(ABC):
    """Abstract base class for platform integrations."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.logger = logging.getLogger(f"integration.{name}")

    @abstractmethod
    async def discover_grants(
        self, organization: OrganizationProfile, criteria: dict[str, Any]
    ) -> IntegrationResult:
        """Discover grants from this platform."""
        pass

    @abstractmethod
    def get_platform_info(self) -> dict[str, Any]:
        """Get information about this platform."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "description": getattr(self, "description", "No description available."),
            "features": getattr(self, "features", []),
            "api_version": getattr(self, "api_version", "N/A"),
        }

    def is_available(self) -> bool:
        """Check if this integration is available."""
        return self.enabled


class GrantPlatformIntegrationManager:
    """Manager for all grant platform integrations."""

    def __init__(self):
        self.platforms: dict[str, PlatformIntegration] = {}
        self.logger = logging.getLogger("integration_manager")
        self._initialize_platforms()

    def _initialize_platforms(self):
        """Initialize all available platform integrations."""
        try:
            # Import and register platforms
            from grant_ai.integrations.simple_open_grants import SimpleOpenGrantsIntegration

            self.register_platform(SimpleOpenGrantsIntegration())

            # Try to import other integrations if available
            try:
                from grant_ai.integrations.granter_ai import GranterAIIntegration

                self.register_platform(GranterAIIntegration())
            except ImportError:
                self.logger.info("Granter.ai integration not available")

            try:
                from grant_ai.integrations.community_force import CommunityForceIntegration

                self.register_platform(CommunityForceIntegration())
            except ImportError:
                self.logger.info("CommunityForce integration not available")

            try:
                from grant_ai.integrations.instrumentl import InstrumentlIntegration

                self.register_platform(InstrumentlIntegration())
            except ImportError:
                self.logger.info("Instrumentl integration not available")

        except Exception as e:
            self.logger.error(f"Error initializing platforms: {e}")

    def register_platform(self, platform: PlatformIntegration):
        """Register a platform integration."""
        self.platforms[platform.name] = platform
        self.logger.info(f"Registered platform: {platform.name}")

    def get_available_platforms(self) -> list[str]:
        """Get list of available platform names."""
        return [name for name, platform in self.platforms.items() if platform.is_available()]

    async def discover_grants_multi_platform(
        self,
        organization: OrganizationProfile,
        platforms: Optional[list[str]] = None,
        criteria: Optional[dict[str, Any]] = None,
    ) -> list[IntegrationResult]:
        """
        Discover grants across multiple platforms.

        Args:
            organization: Organization profile for matching
            platforms: List of platform names to use (None for all available)
            criteria: Additional search criteria

        Returns:
            List of integration results from each platform
        """
        if platforms is None:
            platforms = self.get_available_platforms()

        if criteria is None:
            criteria = {}

        # Prepare search criteria from organization profile
        search_criteria = {
            "focus_areas": organization.focus_areas,
            "organization_type": "nonprofit",  # Default for all orgs
            "geographic_scope": getattr(organization, "location", ""),
            "funding_range": getattr(organization, "preferred_grant_size", (10000, 100000)),
            **criteria,
        }

        # Run all platform searches concurrently
        tasks = []
        for platform_name in platforms:
            if platform_name in self.platforms:
                platform = self.platforms[platform_name]
                if platform.is_available():
                    task = platform.discover_grants(organization, search_criteria)
                    tasks.append(task)

        if not tasks:
            self.logger.warning("No available platforms for grant discovery")
            return []

        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        integration_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Platform {platforms[i]} failed: {result}")
                integration_results.append(
                    IntegrationResult(
                        platform=platforms[i],
                        grants=[],
                        success=False,
                        message=str(result),
                        timestamp=datetime.now(),
                    )
                )
            else:
                integration_results.append(result)

        return integration_results

    def merge_grant_results(self, results: list[IntegrationResult]) -> list[Grant]:
        """
        Merge grants from multiple platforms, removing duplicates and ranking.

        Args:
            results: List of integration results

        Returns:
            Merged and ranked list of unique grants
        """
        all_grants = []
        seen_grants = set()  # Track by title + funder to avoid duplicates

        for result in results:
            if result.success:
                for grant in result.grants:
                    # Create unique identifier for deduplication
                    grant_id = f"{grant.title.lower().strip()}_{grant.funder_name.lower().strip()}"

                    if grant_id not in seen_grants:
                        # Track this grant as seen
                        all_grants.append(grant)
                        seen_grants.add(grant_id)
                    # If grant already exists, skip it (simple deduplication)

        # Sort by grant title for consistent ordering
        all_grants.sort(key=lambda g: g.title)

        self.logger.info(f"Merged {len(all_grants)} unique grants from {len(results)} platforms")
        return all_grants

    def get_platform_statistics(self) -> dict[str, Any]:
        """Get statistics about platform performance."""
        stats = {
            "available_platforms": len(self.get_available_platforms()),
            "total_platforms": len(self.platforms),
            "platform_status": {},
        }

        for name, platform in self.platforms.items():
            stats["platform_status"][name] = {
                "available": platform.is_available(),
                "info": platform.get_platform_info(),
            }

        return stats

    async def test_platform_integrations(self) -> dict[str, bool]:
        """Test all platform integrations."""
        test_org = OrganizationProfile(
            name="Test Organization",
            organization_type="nonprofit",
            focus_areas=["education", "community"],
        )

        test_results = {}
        for name, platform in self.platforms.items():
            try:
                if platform.is_available():
                    result = await platform.discover_grants(test_org, {"test": True})
                    test_results[name] = result.success
                else:
                    test_results[name] = False
            except Exception as e:
                self.logger.error(f"Test failed for {name}: {e}")
                test_results[name] = False

        return test_results


# Global instance
integration_manager = GrantPlatformIntegrationManager()
