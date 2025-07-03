"""
Emergency VS Code Force Quit Fix
This patches the existing GUI to use background threading immediately.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def apply_emergency_threading_fix():
    """Apply emergency threading fix to prevent VS Code crashes."""
    print("🚨 Applying Emergency VS Code Force Quit Fix...")
    
    try:
        # Import Qt components
        from PyQt5.QtCore import QObject, QThread, pyqtSignal
        from PyQt5.QtWidgets import QApplication

        # Import the existing GUI
        from grant_ai.gui.qt_app import GrantSearchTab
        
        print("✅ Successfully imported GUI components")
        
        # Create a threaded search worker
        class EmergencySearchWorker(QObject):
            """Emergency worker to run searches in background thread."""
            finished = pyqtSignal()
            error = pyqtSignal(str)
            progress = pyqtSignal(str)
            grants_found = pyqtSignal(list)
            
            def __init__(self, search_tab):
                super().__init__()
                self.search_tab = search_tab
                self.should_stop = False
            
            def run_search(self):
                """Run the search in background thread."""
                try:
                    self.progress.emit("🔍 Starting background search...")
                    
                    # Import scraper safely
                    from grant_ai.scrapers.wv_grants import WVGrantScraper
                    scraper = WVGrantScraper()
                    
                    self.progress.emit("🏔️ Searching WV grant sources...")
                    grants = scraper.scrape_all_sources()
                    
                    if not self.should_stop:
                        self.grants_found.emit(grants)
                        self.progress.emit(f"✅ Found {len(grants)} grants!")
                    
                    self.finished.emit()
                    
                except Exception as e:
                    self.error.emit(f"Search error: {str(e)}")
                    self.finished.emit()
            
            def stop(self):
                """Stop the search."""
                self.should_stop = True
        
        # Patch the GrantSearchTab class
        original_search = GrantSearchTab.intelligent_grant_search
        
        def threaded_search(self):
            """Threaded version of intelligent_grant_search."""
            print("🧵 Using threaded search to prevent VS Code crashes")
            
            # Check if we already have a thread running
            if hasattr(self, '_search_thread') and self._search_thread.isRunning():
                print("⚠️ Search already running, skipping")
                return
            
            # Get profile
            profile = self.org_profile_tab.get_profile()
            if not profile:
                self.results_list.clear()
                self.results_list.addItem("Please load an organization profile first.")
                return
            
            # Create thread and worker
            self._search_thread = QThread()
            self._search_worker = EmergencySearchWorker(self)
            
            # Move worker to thread
            self._search_worker.moveToThread(self._search_thread)
            
            # Connect signals
            self._search_worker.progress.connect(self._on_search_progress)
            self._search_worker.grants_found.connect(self._on_grants_found)
            self._search_worker.error.connect(self._on_search_error)
            self._search_worker.finished.connect(self._cleanup_search_thread)
            
            # Connect thread signals
            self._search_thread.started.connect(self._search_worker.run_search)
            self._search_thread.finished.connect(self._search_thread.deleteLater)
            
            # Start thread
            self._search_thread.start()
            
            # Update UI
            self.results_list.addItem("🔍 Starting threaded search (prevents crashes)...")
        
        def _on_search_progress(self, message):
            """Handle progress updates."""
            self.results_list.addItem(message)
        
        def _on_grants_found(self, grants):
            """Handle grants found."""
            self.results_list.clear()
            
            if not hasattr(self, 'grant_map'):
                self.grant_map = {}
            
            for grant in grants:
                display_text = f"📊 {grant.title} ({grant.funder_name})"
                self.grant_map[display_text] = grant
                self.results_list.addItem(display_text)
        
        def _on_search_error(self, error_msg):
            """Handle search errors."""
            self.results_list.addItem(f"❌ {error_msg}")
        
        def _cleanup_search_thread(self):
            """Clean up thread resources."""
            if hasattr(self, '_search_thread'):
                self._search_thread.quit()
                self._search_thread.wait()
                self._search_thread = None
                self._search_worker = None
        
        # Apply the patches
        GrantSearchTab.intelligent_grant_search = threaded_search
        GrantSearchTab._on_search_progress = _on_search_progress
        GrantSearchTab._on_grants_found = _on_grants_found
        GrantSearchTab._on_search_error = _on_search_error
        GrantSearchTab._cleanup_search_thread = _cleanup_search_thread
        
        print("✅ Emergency threading fix applied successfully!")
        print("🎯 VS Code force quit issue should now be prevented")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Cannot apply threading fix due to missing modules")
        return False
    except Exception as e:
        print(f"❌ Failed to apply fix: {e}")
        return False


def main():
    """Apply the emergency fix and launch GUI."""
    print("🚨 VS Code Force Quit Emergency Fix")
    print("=" * 40)
    
    # Apply the fix
    if apply_emergency_threading_fix():
        print("\n🚀 Launching GUI with threading fix...")
        
        try:
            from grant_ai.gui.qt_app import main as gui_main
            gui_main()
        except KeyboardInterrupt:
            print("\n👋 Application closed by user")
        except Exception as e:
            print(f"\n❌ GUI launch error: {e}")
    else:
        print("\n❌ Could not apply emergency fix")
        print("Please check dependencies and try again")


if __name__ == "__main__":
    main()
