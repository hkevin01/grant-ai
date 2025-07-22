"""
File operations utilities for Grant AI.
"""
from pathlib import Path
from typing import Any, Dict
import json

def read_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(data: Dict[str, Any], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
