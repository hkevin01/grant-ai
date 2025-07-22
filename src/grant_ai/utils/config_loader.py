"""
Grant AI - Config Loader Utility
Loads YAML configuration files for the application.
"""
import yaml
from typing import Any

class ConfigLoader:
    """
    Loads YAML config files and returns config data.
    """
    @staticmethod
    def load_config(path: str) -> Any:
        with open(path, "r") as f:
            return yaml.safe_load(f)
