"""
Utility functions for Grant AI project.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..config import COMPANIES_DIR, GRANTS_DIR, PROFILES_DIR


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")


def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def list_profiles() -> List[Path]:
    """List all available organization profiles."""
    return list(PROFILES_DIR.glob("*.json"))


def list_grants() -> List[Path]:
    """List all available grant files."""
    return list(GRANTS_DIR.glob("*.json"))


def list_companies() -> List[Path]:
    """List all available company files."""
    return list(COMPANIES_DIR.glob("*.json"))
