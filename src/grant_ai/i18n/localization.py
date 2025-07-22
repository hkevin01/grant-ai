"""Internationalization and localization logic for Grant Research AI."""

from typing import Dict

class LocalizationManager:
    """Manage translations and multi-language support."""
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
    def translate(self, text: str, lang: str = None) -> str:
        lang = lang or self.default_lang
        return self.translations.get(lang, {}).get(text, text)
    def add_translation(self, lang: str, text: str, translation: str):
        if lang not in self.translations:
            self.translations[lang] = {}
        self.translations[lang][text] = translation
