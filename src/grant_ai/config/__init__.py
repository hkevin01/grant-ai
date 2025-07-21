"""
Config package for Grant Research AI.
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
PROFILES_DIR = DATA_DIR / "profiles"
GRANTS_DIR = DATA_DIR / "grants"
COMPANIES_DIR = DATA_DIR / "companies"
APPLICATIONS_DIR = DATA_DIR / "applications"
TEMPLATES_DIR = DATA_DIR / "templates"

# Ensure directories exist
directories = [PROFILES_DIR, GRANTS_DIR, COMPANIES_DIR, APPLICATIONS_DIR, TEMPLATES_DIR]
for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_URL = os.getenv("GRANT_AI_DB_URL", "sqlite:///grant_ai.db")

# API configurations
GRANTS_GOV_API_KEY = os.getenv("GRANTS_GOV_API_KEY", "")
GRANTS_GOV_BASE_URL = "https://www.grants.gov/api"

# Default file paths
DEFAULT_PROFILES = {
    "coda": PROFILES_DIR / "coda_profile.json",
    "nrg": PROFILES_DIR / "nrg_profile.json",
}

DEFAULT_DATA = {
    "grants": GRANTS_DIR / "sample_grants.json",
    "companies": COMPANIES_DIR / "sample_ai_companies.json",
}
