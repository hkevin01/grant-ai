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

# Keep package import lightweight. Avoid importing heavy optional deps at
# import time (e.g., analytics pulling in matplotlib). Expose core via lazy
# __getattr__.

# Remove direct imports to make package import lightweight
# from .models.ai_company import AICompany
# from .models.grant import Grant
# from .models.organization import OrganizationProfile

__all__ = [
    # Removed exports to keep package import lightweight
    # Items can be imported directly from submodules as needed
]

# Lazy attribute access for optional heavy modules


def __getattr__(name: str):  # pragma: no cover - simple lazy import shim
    if name == "cli":
        from .core import cli as _cli

        return _cli
    if name == "db":
        from .core import db as _db

        return _db
    raise AttributeError(f"module 'grant_ai' has no attribute {name!r}")
