#!/usr/bin/env python3
"""
Clean launcher for the Grant AI GUI application.
This script handles Qt warnings and provides a better user experience.
"""
import os
import sys
from pathlib import Path


def launch_gui():
    """Launch the GUI with proper environment setup."""
    
    # Set environment variables to suppress Qt warnings
    env = os.environ.copy()
    env['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
    env['QT_QPA_PLATFORM'] = 'xcb'
    
    # Add the src directory to Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    print("🚀 Launching Grant AI GUI...")
    print("📝 Setting up environment...")
    
    try:
        # Import and run the GUI
        from grant_ai.gui.qt_app import main
        
        print("✅ Environment configured successfully")
        print("🖥️  Starting GUI application...")
        print()
        print("💡 Tips:")
        print("   • Go to 'Organization Profile' tab")
        print("   • Select 'Coda Mountain Academy' from dropdown")
        print("   • The profile should load without crashes")
        print("   • Use Ctrl+C in terminal to close the GUI")
        print()
        
        # Run the main function
        main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = launch_gui()
    sys.exit(exit_code) 