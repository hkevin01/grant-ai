"""
Centralized logging utility for Grant AI.
"""
import logging
import os

LOG_FILE = os.getenv("GRANT_AI_LOG_FILE", "logs/app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module."""
    return logging.getLogger(name)
