"""
Patch to apply threading and AI enhancements to existing Grant AI GUI.
This module safely upgrades the existing Qt application without breaking it.
"""
import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def apply_gui_enhancements():
    """Apply threading and AI enhancements to the existing GUI."""
    try:
        # Import the existing GUI modules
        from grant_ai.gui.enhanced_threading import (
            apply_threading_to_existing_gui,
            setup_qt_error_handling,
        )
        from grant_ai.gui.qt_app import GrantSearchTab, MainWindow
        
        logger.info("Applying GUI enhancements...")
        
        # Set up global error handling
        setup_qt_error_handling()
        
        # Patch the MainWindow class
        original_init = MainWindow.__init__
        
        def enhanced_init(self, *args, **kwargs):
            # Call original initialization
            original_init(self, *args, **kwargs)
            
            try:
                # Apply threading enhancements
                apply_threading_to_existing_gui(self)
                
                # Add AI status indicator
                self._add_ai_status_indicator()
                
                # Add enhanced progress tracking
                self._add_progress_tracking()
                
                logger.info("Successfully enhanced GUI with threading and AI")
                
            except Exception as e:
                logger.error(f"Failed to apply enhancements: {e}")
                # Continue with basic functionality
        
        # Replace the __init__ method
        MainWindow.__init__ = enhanced_init
        
        # Add helper methods to MainWindow
        def _add_ai_status_indicator(self):
            """Add AI status indicator to the GUI."""
            try:
                from PyQt5.QtWidgets import QLabel

                from grant_ai.services.ai_assistant import AIAssistant

                # Create AI assistant and check status
                ai_assistant = AIAssistant()
                
                # Add status label to the main layout if possible
                if hasattr(self, 'statusBar'):
                    if ai_assistant.is_available():
                        status_text = "🤖 AI Assistant: Available"
                    else:
                        status_text = "⚠️ AI Assistant: Limited (install requirements-ai.txt)"
                    
                    ai_status_label = QLabel(status_text)
                    self.statusBar().addPermanentWidget(ai_status_label)
                    
            except Exception as e:
                logger.warning(f"Could not add AI status indicator: {e}")
        
        def _add_progress_tracking(self):
            """Add progress tracking to the GUI."""
            try:
                from PyQt5.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout

                # Add progress bar if not exists
                if not hasattr(self, 'progress_bar'):
                    self.progress_bar = QProgressBar()
                    self.progress_bar.setVisible(False)
                    
                    # Try to add to main layout
                    if hasattr(self, 'main_layout'):
                        self.main_layout.addWidget(self.progress_bar)
                
                # Add status text area if not exists
                if not hasattr(self, 'status_text'):
                    self.status_text = QTextEdit()
                    self.status_text.setMaximumHeight(150)
                    self.status_text.setPlaceholderText("Search status will appear here...")
                    self.status_text.setReadOnly(True)
                    
                    # Try to add to search tab
                    if hasattr(self, 'search_tab') and hasattr(self.search_tab, 'layout'):
                        self.search_tab.layout().addWidget(self.status_text)
                        
            except Exception as e:
                logger.warning(f"Could not add progress tracking: {e}")
        
        # Add the helper methods to MainWindow
        MainWindow._add_ai_status_indicator = _add_ai_status_indicator
        MainWindow._add_progress_tracking = _add_progress_tracking
        
        logger.info("GUI enhancement patch applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to apply GUI enhancements: {e}")
        return False


def install_ai_dependencies():
    """Install AI dependencies if not already installed."""
    try:
        import subprocess
        import sys

        # Check if AI dependencies are available
        try:
            import sentence_transformers
            import spacy
            logger.info("AI dependencies already available")
            return True
        except ImportError:
            logger.info("AI dependencies not found, attempting to install...")
        
        # Try to install from requirements-ai.txt if it exists
        requirements_ai = Path(__file__).parent.parent / "requirements-ai.txt"
        if requirements_ai.exists():
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_ai)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("AI dependencies installed successfully")
                return True
            else:
                logger.warning(f"Failed to install AI dependencies: {result.stderr}")
                return False
        else:
            logger.warning("requirements-ai.txt not found, creating minimal version...")
            
            # Create basic requirements file
            basic_requirements = [
                "sentence-transformers>=2.2.0",
                "spacy>=3.4.0",
                "textblob>=0.17.0"
            ]
            
            for package in basic_requirements:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True, capture_output=True)
                    logger.info(f"Installed {package}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to install {package}: {e}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error installing AI dependencies: {e}")
        return False


def main():
    """Main function to apply enhancements and launch GUI."""
    try:
        logger.info("Starting Grant AI with enhancements...")
        
        # Try to install AI dependencies
        if install_ai_dependencies():
            logger.info("AI dependencies check completed")
        
        # Apply GUI enhancements
        if apply_gui_enhancements():
            logger.info("GUI enhancements applied successfully")
        else:
            logger.warning("Running with basic GUI functionality")
        
        # Launch the original GUI
        from grant_ai.gui.qt_app import main as original_main
        logger.info("Launching enhanced GUI...")
        original_main()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to launch enhanced GUI: {e}")
        logger.info("Attempting to launch basic GUI...")
        
        try:
            from grant_ai.gui.qt_app import main as original_main
            original_main()
        except Exception as e2:
            logger.error(f"Failed to launch basic GUI: {e2}")
            sys.exit(1)


if __name__ == "__main__":
    main()
    main()
