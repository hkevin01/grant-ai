"""Mobile-friendly web interface for Grant Research AI."""

# TODO: Implement responsive web UI and mobile navigation

class MobileWebUI:
    """Mobile web UI enhancements for Grant AI."""
    def __init__(self):
        self.supported = True
    def is_mobile_supported(self) -> bool:
        return self.supported
    def get_navigation_structure(self) -> dict:
        return {"screens": ["home", "search", "details", "profile"]}
