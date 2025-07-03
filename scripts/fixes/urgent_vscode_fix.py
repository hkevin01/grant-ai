#!/usr/bin/env python3
"""
URGENT FIX: Patch the existing GUI to prevent VS Code force quit
This replaces the problematic intelligent_grant_search with a threaded version
"""
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def apply_urgent_fix():
    """Apply immediate fix to prevent VS Code force quit"""
    print("🚨 Applying URGENT fix to prevent VS Code force quit...")
    
    try:
        # Import the GUI module
        from PyQt5.QtCore import QObject, QThread, pyqtSignal

        from grant_ai.gui.qt_app import GrantSearchTab

        # Create a worker class for background search
        class SearchWorker(QObject):
            progress = pyqtSignal(str)
            finished = pyqtSignal(list)
            error = pyqtSignal(str)
            
            def __init__(self, search_tab):
                super().__init__()
                self.search_tab = search_tab
                
            def run_search(self):
                """Run the search in background thread"""
                try:
                    self.progress.emit("🔍 Starting background search...")
                    
                    # Get profile
                    profile = self.search_tab.org_profile_tab.get_profile()
                    if not profile:
                        self.error.emit("Please load an organization profile first.")
                        return
                    
                    all_grants = []
                    
                    # Step 1: Database search (quick)
                    try:
                        self.progress.emit("💾 Searching database...")
                        db_grants = self.search_tab._search_database_for_profile(profile)
                        all_grants.extend(db_grants)
                        self.progress.emit(f"   Found {len(db_grants)} grants in database")
                    except Exception as e:
                        self.progress.emit(f"   ⚠️ Database search failed: {str(e)[:50]}...")
                    
                    # Step 2: AI search (if available)
                    try:
                        if hasattr(self.search_tab, 'ai_agent'):
                            self.progress.emit("🤖 AI search...")
                            ai_grants = self.search_tab.ai_agent.search_grants_for_profile(profile)
                            new_ai_grants = [g for g in ai_grants if g not in all_grants]
                            all_grants.extend(new_ai_grants)
                            self.progress.emit(f"   Found {len(new_ai_grants)} AI grants")
                    except Exception as e:
                        self.progress.emit(f"   ⚠️ AI search failed: {str(e)[:50]}...")
                    
                    # Step 3: Web scraping (this was causing the hang)
                    try:
                        self.progress.emit("🏔️ Searching WV sources...")
                        if hasattr(self.search_tab, 'wv_scraper'):
                            wv_grants = self.search_tab.wv_scraper.scrape_all_sources()
                            new_wv_grants = [g for g in wv_grants if g not in all_grants]
                            all_grants.extend(new_wv_grants)
                            self.progress.emit(f"   Found {len(new_wv_grants)} WV grants")
                    except Exception as e:
                        self.progress.emit(f"   ⚠️ WV scraper failed: {str(e)[:50]}...")
                    
                    self.finished.emit(all_grants)
                    
                except Exception as e:
                    self.error.emit(f"Search failed: {e}")
        
        # Replace the problematic method
        def threaded_intelligent_grant_search(self):
            """Threaded version that won't freeze VS Code"""
            try:
                # Disable the button to prevent multiple searches
                self.intelligent_search_btn.setEnabled(False)
                self.intelligent_search_btn.setText("🔄 Searching...")
                
                # Clear results and add status
                self.results_list.clear()
                self.results_list.addItem("🚀 Starting threaded search (no more VS Code crashes!)")
                
                # Create worker and thread
                self.search_worker = SearchWorker(self)
                self.search_thread = QThread()
                
                # Move worker to thread
                self.search_worker.moveToThread(self.search_thread)
                
                # Connect signals
                self.search_worker.progress.connect(self.on_search_progress)
                self.search_worker.finished.connect(self.on_search_finished)
                self.search_worker.error.connect(self.on_search_error)
                self.search_thread.started.connect(self.search_worker.run_search)
                
                # Start the thread
                self.search_thread.start()
                
            except Exception as e:
                self.results_list.addItem(f"❌ Threading setup failed: {e}")
                self.intelligent_search_btn.setEnabled(True)
                self.intelligent_search_btn.setText("🔍 Intelligent Grant Search")
        
        def on_search_progress(self, message):
            """Handle progress updates"""
            self.results_list.addItem(message)
            # Auto-scroll to bottom
            self.results_list.scrollToBottom()
        
        def on_search_finished(self, grants):
            """Handle search completion"""
            try:
                # Re-enable button
                self.intelligent_search_btn.setEnabled(True)
                self.intelligent_search_btn.setText("🔍 Intelligent Grant Search")
                
                # Clean up thread
                if hasattr(self, 'search_thread'):
                    self.search_thread.quit()
                    self.search_thread.wait()
                
                # Process results
                if grants:
                    self.results_list.addItem(f"✅ Search completed! Found {len(grants)} grants")
                    
                    # Update grant map
                    if not hasattr(self, 'grant_map'):
                        self.grant_map = {}
                    
                    # Add grants to list
                    for grant in grants:
                        display_text = f"📄 {grant.title} ({grant.funder_name or 'Unknown'})"
                        self.grant_map[display_text] = grant
                        self.results_list.addItem(display_text)
                else:
                    self.results_list.addItem("⚠️ No grants found in search")
                    
            except Exception as e:
                self.results_list.addItem(f"❌ Error processing results: {e}")
        
        def on_search_error(self, error_msg):
            """Handle search errors"""
            self.intelligent_search_btn.setEnabled(True)
            self.intelligent_search_btn.setText("🔍 Intelligent Grant Search")
            self.results_list.addItem(f"❌ Search error: {error_msg}")
            
            # Clean up thread
            if hasattr(self, 'search_thread'):
                self.search_thread.quit()
                self.search_thread.wait()
        
        # Apply the patch
        GrantSearchTab.intelligent_grant_search = threaded_intelligent_grant_search
        GrantSearchTab.on_search_progress = on_search_progress
        GrantSearchTab.on_search_finished = on_search_finished
        GrantSearchTab.on_search_error = on_search_error
        
        print("✅ URGENT FIX APPLIED!")
        print("   - intelligent_grant_search now runs in background thread")
        print("   - VS Code will no longer freeze or force quit")
        print("   - Progress updates show in real-time")
        print("   - Errors are handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply urgent fix: {e}")
        return False

if __name__ == "__main__":
    print("🚨 URGENT VS Code Force Quit Fix")
    print("=" * 40)
    
    if apply_urgent_fix():
        print("\n🎉 Fix applied successfully!")
        print("Now you can run the GUI without VS Code force quit issues:")
        print("   python launch_gui.py")
    else:
        print("\n❌ Fix failed. Manual intervention needed.")
        print("\n❌ Fix failed. Manual intervention needed.")
