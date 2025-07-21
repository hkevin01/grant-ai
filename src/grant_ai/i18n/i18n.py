"""
Internationalization (i18n) module for Grant AI.
"""

def translate(text: str, lang: str = "en") -> str:
    """Translate text to the specified language."""
    # Simple mock translation for demonstration
    translations = {
        "en": text,
        "es": f"[ES] {text}",
        "fr": f"[FR] {text}",
        "de": f"[DE] {text}",
    }
    return translations.get(lang, text)
