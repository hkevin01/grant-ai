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
from grant_ai.ai.advanced_matching import AdvancedGrantMatcher
from grant_ai.ai.nlp_search import NLPGrantSearch
from grant_ai.analytics.dashboard import AnalyticsDashboard
from grant_ai.scrapers.foundation_scraper import FoundationScraper
from grant_ai.scrapers.realtime_monitor import RealTimeGrantMonitor
from grant_ai.scrapers.rss_feeds import RSSFeedGrantMonitor
from grant_ai.community.community import CommunitySignalIntegrator
from grant_ai.mobile.web import MobileWebUI
from grant_ai.i18n.localization import LocalizationManager
from grant_ai.utils.data_validator import validate_required_fields, validate_email
from grant_ai.utils.file_ops import read_json, write_json
from grant_ai.utils.progress_tracker import ProgressTracker
from grant_ai.marketplace.marketplace import GrantMarketplace
from grant_ai.integrations.google import GoogleIntegration
from grant_ai.integrations.salesforce import SalesforceIntegration
from grant_ai.analytics.advanced_dashboard import AdvancedAnalyticsDashboard
from grant_ai.community.feedback_system import FeedbackSystem


def main():
    # Initialize modules
    matcher = AdvancedGrantMatcher()
    nlp_search = NLPGrantSearch()
    dashboard = AnalyticsDashboard()
    foundation_scraper = FoundationScraper()
    realtime_monitor = RealTimeGrantMonitor()
    rss_monitor = RSSFeedGrantMonitor()
    community_signals = CommunitySignalIntegrator()
    mobile_ui = MobileWebUI()
    i18n = LocalizationManager()
    progress = ProgressTracker()
    marketplace = GrantMarketplace()
    google = GoogleIntegration()
    salesforce = SalesforceIntegration()
    advanced_dashboard = AdvancedAnalyticsDashboard()
    feedback_system = FeedbackSystem()

    # Example integration logic
    print("Grant AI Main Application Initialized.")
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

    # Example usage of utilities
    sample_data = {'email': 'test@example.com'}
    missing = validate_required_fields(sample_data, ['email', 'name'])
    print(f"Missing fields: {missing}")
    print(f"Email valid: {validate_email(sample_data['email'])}")

    # Example usage
    marketplace.add_listing({'title': 'AI Grant', 'amount': 50000})
    print('Marketplace listings:', marketplace.search_listings(['AI']))
    print('Google sync:', google.sync_drive({'data': 'sample'}))
    print('Salesforce sync:', salesforce.sync_contacts({'contacts': []}))
    advanced_dashboard.update_metrics({'total_grants': 10, 'success_rate': 0.8})
    print('Analytics summary:', advanced_dashboard.get_summary())
    feedback_system.submit_feedback('user1', 'Great platform!')
    print('Feedback:', feedback_system.get_feedback())


if __name__ == "__main__":
    main()
