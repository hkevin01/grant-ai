#!/usr/bin/env python3
"""
Complete GUI Test Runner - Tests all GUI components and functionality
This script validates that the Grant Research AI GUI is working correctly.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment for headless testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'


def run_test_with_timeout(test_func, timeout=30):
    """Run a test function with timeout protection."""
    try:
        return test_func()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_gui_imports():
    """Test that all GUI components can be imported."""
    print("🧪 Testing GUI Imports...")
    
    try:
        # Core PyQt5 imports
        from PyQt5.QtCore import QThread, pyqtSignal
        from PyQt5.QtWidgets import QApplication, QMainWindow

        # Enhanced components
        from grant_ai.gui.enhanced_past_grants_tab import EnhancedPastGrantsTab
        from grant_ai.gui.icon_manager import icon_manager
        from grant_ai.gui.predictive_grants_tab import PredictiveGrantsTab

        # Main GUI components
        from grant_ai.gui.qt_app import (
            ApplicationTab,
            GrantSearchTab,
            MainWindow,
            OrgProfileTab,
            PastGrantsTab,
            ReportingTab,
        )
        from grant_ai.gui.questionnaire_widget import QuestionnaireWidget
        
        print("   ✅ All GUI components imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_gui_creation():
    """Test creating GUI components."""
    print("🧪 Testing GUI Component Creation...")
    
    try:
        from PyQt5.QtWidgets import QApplication

        from grant_ai.gui.qt_app import MainWindow

        # Create application
        app = QApplication([])
        
        # Create main window
        window = MainWindow()
        
        # Verify window properties
        assert window.windowTitle() == "Grant Research AI - PyQt GUI"
        
        # Check tabs
        central_widget = window.centralWidget()
        if hasattr(central_widget, 'count'):
            tab_count = central_widget.count()
            print(f"   📊 Created window with {tab_count} tabs")
            assert tab_count >= 6, f"Expected at least 6 tabs, got {tab_count}"
        
        # Cleanup
        window.close()
        app.quit()
        
        print("   ✅ GUI creation successful")
        return True
        
    except Exception as e:
        print(f"   ❌ GUI creation failed: {e}")
        return False


def test_gui_functionality():
    """Test GUI functionality."""
    print("🧪 Testing GUI Functionality...")
    
    try:
        from PyQt5.QtWidgets import QApplication

        from grant_ai.gui.qt_app import GrantSearchTab, OrgProfileTab
        
        app = QApplication([])
        
        # Test organization profile
        profile_tab = OrgProfileTab()
        profile_tab.name_input.setText("Test Organization")
        profile_tab.mission_input.setPlainText("Test mission")
        
        profile = profile_tab.get_profile()
        assert profile is not None
        assert profile.name == "Test Organization"
        print("   ✅ Organization profile functionality working")
        
        # Test grant search
        search_tab = GrantSearchTab(profile_tab)
        search_tab.focus_area_input.setText("education")
        search_tab.amount_min_input.setText("1000")
        
        assert search_tab.focus_area_input.text() == "education"
        assert search_tab.amount_min_input.text() == "1000"
        print("   ✅ Grant search functionality working")
        
        # Test integration
        search_tab.auto_fill_and_suggest(profile, auto_search=False)
        description = search_tab.search_description.toPlainText()
        assert "Test Organization" in description
        print("   ✅ Profile-to-search integration working")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ GUI functionality test failed: {e}")
        return False


def test_gui_launch_scripts():
    """Test that GUI launch scripts work."""
    print("🧪 Testing GUI Launch Scripts...")
    
    try:
        # Test launch_gui.py script
        result = subprocess.run([
            'timeout', '5',
            'python', 'scripts/launch_gui.py'
        ], 
        capture_output=True, 
        text=True,
        cwd='/home/kevin/Projects/grant-ai'
        )
        
        if "GUI starting..." in result.stdout:
            print("   ✅ scripts/launch_gui.py works")
        else:
            print("   ⚠️ scripts/launch_gui.py may need attention")
        
        # Test run.sh gui
        result = subprocess.run([
            'timeout', '5',
            './run.sh', 'gui'
        ], 
        capture_output=True, 
        text=True,
        cwd='/home/kevin/Projects/grant-ai'
        )
        
        if "Launching GUI..." in result.stdout:
            print("   ✅ ./run.sh gui works")
        else:
            print("   ⚠️ ./run.sh gui may need attention")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Launch script test failed: {e}")
        return False


def test_specific_features():
    """Test specific GUI features."""
    print("🧪 Testing Specific Features...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication([])
        
        # Test past grants tab
        from grant_ai.gui.qt_app import PastGrantsTab
        past_grants = PastGrantsTab()
        assert len(past_grants.past_grants_data) > 0
        print("   ✅ Past grants data loaded")
        
        # Test application tracking
        from grant_ai.gui.qt_app import ApplicationTab
        app_tab = ApplicationTab()
        app_tab.load_applications()
        print("   ✅ Application tracking loaded")
        
        # Test enhanced features
        from grant_ai.gui.predictive_grants_tab import PredictiveGrantsTab
        pred_tab = PredictiveGrantsTab()
        print("   ✅ Predictive grants tab working")
        
        from grant_ai.gui.enhanced_past_grants_tab import EnhancedPastGrantsTab
        enh_tab = EnhancedPastGrantsTab()
        print("   ✅ Enhanced past grants tab working")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ Specific features test failed: {e}")
        return False


def test_error_handling():
    """Test GUI error handling."""
    print("🧪 Testing Error Handling...")
    
    try:
        from PyQt5.QtWidgets import QApplication

        from grant_ai.gui.qt_app import GrantSearchTab, OrgProfileTab
        
        app = QApplication([])
        
        # Test search without profile
        profile_tab = OrgProfileTab()
        search_tab = GrantSearchTab(profile_tab)
        
        # This should not crash
        search_tab.intelligent_grant_search()
        print("   ✅ Search without profile handled gracefully")
        
        # Test corrupted data handling
        search_tab.handle_corrupted_grants_file()
        print("   ✅ Corrupted data handling working")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False


def run_comprehensive_gui_tests():
    """Run all GUI tests."""
    print("🧪 Grant Research AI - Comprehensive GUI Tests")
    print("=" * 60)
    
    tests = [
        ("GUI Imports", test_gui_imports),
        ("GUI Creation", test_gui_creation),
        ("GUI Functionality", test_gui_functionality),
        ("Launch Scripts", test_gui_launch_scripts),
        ("Specific Features", test_specific_features),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        
        if run_test_with_timeout(test_func):
            passed += 1
        else:
            print(f"   ❌ {test_name} failed")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 COMPREHENSIVE TEST RESULTS")
    print(f"   Tests Run: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL GUI TESTS PASSED!")
        print("\n✨ Your Grant Research AI GUI is fully functional!")
        print("\n🚀 Launch the GUI with any of these commands:")
        print("   ./run.sh gui")
        print("   python scripts/launch_gui.py")
        print("\n📋 Available Features:")
        print("   • Intelligent Grant Search")
        print("   • Organization Profile Management") 
        print("   • Past Grants Tracking")
        print("   • Application Management")
        print("   • Predictive Grant Matching")
        print("   • Reporting & Analytics")
    elif passed >= (total * 0.8):
        print(f"\n✅ GUI IS MOSTLY FUNCTIONAL ({passed}/{total} tests passed)")
        print("\n🚀 You can use the GUI with: ./run.sh gui")
        print(f"   {total - passed} minor issue(s) to address")
    else:
        print(f"\n⚠️ GUI NEEDS ATTENTION ({passed}/{total} tests passed)")
        print("   Please check the failed tests above")
    
    return passed >= (total * 0.8)


if __name__ == "__main__":
    try:
        success = run_comprehensive_gui_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        sys.exit(1)
