"""
Configuration settings for Grant Research AI.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """App configuration settings."""

    app_name: str = "Grant Research AI"
    debug: bool = False
    database_url: str = "sqlite:///data/grants.db"
    # Add more settings as needed


settings = Settings()
