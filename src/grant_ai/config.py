"""
Central configuration for Grant AI project.
"""

import os
from typing import Any, Dict


class Config:
    """Project-wide configuration settings."""
    DEBUG: bool = os.getenv("GRANT_AI_DEBUG", "False") == "True"
    DATABASE_URL: str = os.getenv("GRANT_AI_DATABASE_URL", "sqlite:///data/grants.db")
    LOG_LEVEL: str = os.getenv("GRANT_AI_LOG_LEVEL", "INFO")

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }


config = Config()
