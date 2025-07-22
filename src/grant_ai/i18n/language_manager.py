"""
Grant AI - Language Manager
Handles internationalization and language switching for the platform.
"""

from typing import List

class LanguageManager:
    """
    Manages supported languages and provides translation utilities.
    """
    def __init__(self, supported_languages: List[str] = None, default_language: str = "en"):
        self.supported_languages = supported_languages or ["en", "es", "fr", "de"]
        self.default_language = default_language
        self.current_language = default_language

    def set_language(self, language: str) -> bool:
        """
        Set the current language if supported.
        Returns True if successful, False otherwise.
        """
        if language in self.supported_languages:
            self.current_language = language
            return True
        return False

    def get_language(self) -> str:
        """
        Get the current language.
        """
        return self.current_language

    def get_supported_languages(self) -> list:
        """
        Return the list of supported languages.
        """
        return self.supported_languages

    def translate(self, text: str) -> str:
        """
        Translate the given text to the current language (stub).
        """
        # Placeholder: Integrate with real translation service
        return f"[{self.current_language}] {text}"
