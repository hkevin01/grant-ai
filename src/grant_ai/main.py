"""
Main application entry point for Grant AI.
"""

from grant_ai.config import config
from grant_ai.analytics import analytics
from grant_ai.security import security
from grant_ai.community import community
from grant_ai.i18n import i18n
from grant_ai.mobile import mobile
from grant_ai.accessibility import accessibility


def main():
    print("Grant AI Main Application Starting...")
    print(f"Config: {config.as_dict()}")
    print(
        f"Analytics module available: {hasattr(analytics, 'analyze_grant_success')}"
    )
    print(
        f"Security module available: {hasattr(security, 'check_permissions')}"
    )
    print(
        f"Community module available: {hasattr(community, 'get_community_signals')}"
    )
    print(f"i18n module available: {hasattr(i18n, 'translate')}")
    print(f"Mobile module available: {hasattr(mobile, 'is_mobile_supported')}")
    print(
        f"Accessibility module available: {hasattr(accessibility, 'check_accessibility')}"
    )


if __name__ == "__main__":
    main()
