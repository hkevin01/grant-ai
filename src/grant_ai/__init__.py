"""
Grant AI - AI-powered grant research and application management.

This package provides tools for non-profit organizations to research grants,
analyze AI companies, and manage grant applications efficiently.
"""

__version__ = "0.1.0"

from .analysis.grant_researcher import GrantResearcher
from .models.organization import OrganizationProfile

__all__ = ["__version__", "OrganizationProfile", "GrantResearcher"]
