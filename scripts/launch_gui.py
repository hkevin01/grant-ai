#!/usr/bin/env python3
"""
Simple launcher script for the Grant AI GUI application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Launch the Grant AI GUI application."""
    try:
        from grant_ai.gui.qt_app import main as gui_main
        
        print("🚀 Launching Grant AI GUI...")
        print("\nFeatures available:")
        print("  📊 Grant Search & Filtering")
        print("  🏢 Organization Profile Management")
        print("  📝 Profile Questionnaire System")
        print("  📋 Application Tracking Dashboard")
        print("\nGUI starting...")
        
        gui_main()
        
    except ImportError as e:
        print(f"❌ Error importing GUI modules: {e}")
        print("💡 Make sure PyQt5 is installed: pip install PyQt5")
        sys.exit(1)
    except (RuntimeError, OSError) as e:
        print(f"❌ Error launching GUI: {e}")
        print("💡 Make sure you have a display available (X11/Wayland)")
        sys.exit(1)


if __name__ == "__main__":
    main()
