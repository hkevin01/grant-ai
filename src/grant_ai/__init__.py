"""
Grant Research AI - AI-powered grant research and management system.

This package provides tools for researching grants, managing organization
profiles, and matching organizations with suitable funding opportunities.
"""

__version__ = "0.1.0"
__author__ = "Grant AI Team"

# Configuration and utilities
# Core modules
# from . import analysis, config, gui, models, scrapers, utils
# from .analysis.grant_researcher import GrantResearcher  # Commented out to avoid circular import

# Core functionality
from .core import cli, db
from .models.ai_company import AICompany
from .models.grant import Grant

# Main classes for easy access
from .models.organization import OrganizationProfile

__all__ = [
    "models",
    "analysis",
    "scrapers",
    "gui",
    "config",
    "utils",
    "cli",
    "db",
    "OrganizationProfile",
    "Grant",
    "AICompany",
]
