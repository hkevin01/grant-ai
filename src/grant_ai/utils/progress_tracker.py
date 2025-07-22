"""
Progress tracking utilities for Grant AI.
"""
from typing import Dict

class ProgressTracker:
    """Track progress for grant applications and tasks."""
    def __init__(self):
        self.progress: Dict[str, int] = {}
    def update(self, task: str, percent: int):
        self.progress[task] = percent
    def get(self, task: str) -> int:
        return self.progress.get(task, 0)
    def summary(self) -> Dict[str, int]:
        return dict(self.progress)
