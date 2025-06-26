#!/usr/bin/env python3
"""
Test script to verify grant details dialog functionality.
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtWidgets import QApplication

    from grant_ai.gui.qt_app import GrantSearchTab, OrgProfileTab
    from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
    print("✓ PyQt5 and GUI modules imported successfully")
except ImportError as e:
    print(f"ERROR: Failed to import GUI modules: {e}")
    sys.exit(1)

def test_grant_details_dialog():
    """Test that grant details dialog shows comprehensive information."""
    try:
        # Create QApplication
        app = QApplication(sys.argv)
        print("✓ QApplication created successfully")
        
        # Create a sample grant for testing
        sample_grant = Grant(
            id="TEST-001",
            title="Sample Education Grant",
            funder_name="Test Foundation",
            amount_min=25000,
            amount_max=100000,
            description="This is a comprehensive grant for educational programs that support youth development through arts and technology.",
            application_url="https://example.com/apply",
            focus_areas=["education", "art_education"],
            eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
            status=GrantStatus.OPEN,
            funding_type=FundingType.GRANT,
            contact_email="grants@testfoundation.org",
            contact_phone="555-123-4567"
        )
        
        # Create OrgProfileTab (needed for GrantSearchTab)
        org_tab = OrgProfileTab()
        print("✓ OrgProfileTab created successfully")
        
        # Create GrantSearchTab
        search_tab = GrantSearchTab(org_tab)
        print("✓ GrantSearchTab created successfully")
        
        # Test the grant details dialog
        print("Testing grant details dialog...")
        
        # Create a mock item for testing
        class MockItem:
            def __init__(self, text):
                self.text = text
        
        # Set up the grant map
        search_tab.grant_map = {f"{sample_grant.title} ({sample_grant.funder_name})": sample_grant}
        
        # Test the dialog
        mock_item = MockItem(f"{sample_grant.title} ({sample_grant.funder_name})")
        search_tab.show_grant_details(mock_item)
        
        print("✓ Grant details dialog test completed")
        print("  - Dialog should have opened with comprehensive grant information")
        print("  - Should show all grant fields including contact information")
        print("  - Should have Copy to Clipboard and Close buttons")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Grant details dialog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grant_details_dialog()
    sys.exit(0 if success else 1) 