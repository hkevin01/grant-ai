"""
User feedback and support system for Grant AI.
"""
from typing import List, Dict

class FeedbackSystem:
    """Collect and manage user feedback and support requests."""
    def __init__(self):
        """Initialize feedback system with empty feedback list."""
        self.feedback: List[Dict] = []

    def submit_feedback(self, user_id: str, message: str):
        """Submit user feedback.
        Args:
            user_id: ID of the user submitting feedback.
            message: Feedback message.
        """
        self.feedback.append({'user_id': user_id, 'message': message})

    def get_feedback(self) -> List[Dict]:
        """Get all submitted feedback.
        Returns:
            List of feedback dictionaries.
        """
        return list(self.feedback)
