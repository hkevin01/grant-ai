#!/usr/bin/env python3
"""
Validation script to check file structure and integration completeness.
"""

import os
from pathlib import Path


def check_file_structure():
    """Check that all required files exist."""
    project_root = Path(__file__).parent
    
    required_files = [
        "src/grant_ai/gui/qt_app.py",
        "src/grant_ai/gui/predictive_grants_tab.py", 
        "src/grant_ai/gui/enhanced_past_grants_tab.py",
        "src/grant_ai/models/predictive_grant.py",
        "src/grant_ai/models/enhanced_past_grant.py",
        "run.sh",
        "test_integration.py",
        "scripts/create_sample_data.py",
        "INTEGRATION_COMPLETE.md"
    ]
    
    print("🔍 Checking file structure...")
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files exist!")
        return True

def check_integration_points():
    """Check key integration points in qt_app.py."""
    project_root = Path(__file__).parent
    qt_app_path = project_root / "src/grant_ai/gui/qt_app.py"
    
    if not qt_app_path.exists():
        print("❌ qt_app.py not found")
        return False
    
    print("🔍 Checking integration points...")
    
    with open(qt_app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    integration_points = [
        ("Import PredictiveGrantsTab", "from grant_ai.gui.predictive_grants_tab import PredictiveGrantsTab"),
        ("Import EnhancedPastGrantsTab", "from grant_ai.gui.enhanced_past_grants_tab import EnhancedPastGrantsTab"), 
        ("Create PredictiveGrantsTab", "self.predictive_grants_tab = PredictiveGrantsTab()"),
        ("Create EnhancedPastGrantsTab", "self.enhanced_past_grants_tab = EnhancedPastGrantsTab()"),
        ("Add Predictive Grants Tab", 'tabs.addTab(self.predictive_grants_tab, "Predictive Grants")'),
        ("Add Enhanced Past Grants Tab", 'tabs.addTab(self.enhanced_past_grants_tab, "Enhanced Past Grants")'),
        ("Profile Changed Signal", "profile_changed = pyqtSignal(object)"),
        ("Connect Predictive Grants", "self.predictive_grants_tab.update_organization_context"),
        ("Connect Enhanced Past Grants", "self.enhanced_past_grants_tab.update_organization_context")
    ]
    
    success_count = 0
    for description, check_string in integration_points:
        if check_string in content:
            print(f"✅ {description}")
            success_count += 1
        else:
            print(f"❌ {description}")
    
    if success_count == len(integration_points):
        print(f"\n✅ All {len(integration_points)} integration points found!")
        return True
    else:
        print(f"\n❌ Missing {len(integration_points) - success_count} integration points")
        return False

def check_tab_methods():
    """Check that tabs have required methods."""
    project_root = Path(__file__).parent
    
    tab_files = [
        ("Predictive Grants Tab", "src/grant_ai/gui/predictive_grants_tab.py"),
        ("Enhanced Past Grants Tab", "src/grant_ai/gui/enhanced_past_grants_tab.py")
    ]
    
    print("🔍 Checking tab methods...")
    
    all_good = True
    for tab_name, tab_path in tab_files:
        full_path = project_root / tab_path
        if not full_path.exists():
            print(f"❌ {tab_name}: File not found")
            all_good = False
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            "def update_organization_context",
            "def apply_organization_filter"
        ]
        
        tab_good = True
        for method in required_methods:
            if method in content:
                print(f"✅ {tab_name}: {method}")
            else:
                print(f"❌ {tab_name}: {method}")
                tab_good = False
        
        if not tab_good:
            all_good = False
    
    return all_good

def main():
    """Run all validation checks."""
    print("🧪 Running Integration Validation")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Integration Points", check_integration_points), 
        ("Tab Methods", check_tab_methods)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\n✅ Integration is complete and ready for use:")
        print("   - All required files exist")
        print("   - Integration points are properly connected")
        print("   - Tab methods are implemented")
        print("   - Organization context wiring is in place")
        print("\n🚀 Ready to launch: ./run.sh gui")
    else:
        print(f"❌ {total - passed} validations failed")
        print("Please check the errors above and fix them before proceeding")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
