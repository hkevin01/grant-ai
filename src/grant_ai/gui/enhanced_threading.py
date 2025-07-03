"""
Enhanced Qt GUI with robust threading and AI integration.
Prevents force quits during long-running operations.
"""
import logging
import sys
import traceback
from typing import List, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QTextEdit

from grant_ai.models import OrganizationProfile
from grant_ai.models.grant import Grant
from grant_ai.scrapers.wv_grants import WVGrantScraper
from grant_ai.services.ai_assistant import AIAssistant
from grant_ai.services.robust_scraper import RobustWebScraper


class GrantSearchWorker(QObject):
    """Worker thread for grant searching to prevent GUI freezing."""
    
    # Signals for communication with main thread
    progress_update = pyqtSignal(str)
    grants_found = pyqtSignal(list)
    search_completed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.should_stop = False
        
        # Initialize services
        self.ai_assistant = AIAssistant()
        self.robust_scraper = RobustWebScraper()
        self.wv_scraper = WVGrantScraper()
    
    def search_grants(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ):
        """
        Perform comprehensive grant search in background thread.
        
        Args:
            organization: Organization profile
            search_params: Search parameters dictionary
        """
        try:
            self.should_stop = False
            all_grants = []
            
            # Step 1: Database search
            if not self.should_stop:
                self.progress_update.emit("🔍 Searching database...")
                try:
                    db_grants = self._search_database(organization, search_params)
                    all_grants.extend(db_grants)
                    self.progress_update.emit(
                        f"📊 Found {len(db_grants)} grants in database"
                    )
                except Exception as e:
                    self.error_occurred.emit(f"Database search error: {e}")
            
            # Step 2: AI-enhanced web search
            if not self.should_stop and self.ai_assistant.is_available():
                self.progress_update.emit("🤖 AI-enhanced web search...")
                try:
                    ai_grants = self._ai_web_search(organization, search_params)
                    new_grants = [g for g in ai_grants if g not in all_grants]
                    all_grants.extend(new_grants)
                    self.progress_update.emit(
                        f"🧠 Found {len(new_grants)} new grants via AI"
                    )
                except Exception as e:
                    self.error_occurred.emit(f"AI search error: {e}")
            
            # Step 3: State/Regional scrapers
            if not self.should_stop:
                state = search_params.get('state', 'West Virginia')
                if state in ['West Virginia', 'All States']:
                    self.progress_update.emit("🏔️ Searching West Virginia sources...")
                    try:
                        wv_grants = self.wv_scraper.scrape_all_sources()
                        new_wv_grants = [g for g in wv_grants if g not in all_grants]
                        all_grants.extend(new_wv_grants)
                        self.progress_update.emit(
                            f"🏛️ Found {len(new_wv_grants)} new WV grants"
                        )
                    except Exception as e:
                        self.error_occurred.emit(f"WV scraper error: {e}")
            
            # Step 4: Enhanced web scraping with fallbacks
            if not self.should_stop:
                self.progress_update.emit("🌐 Enhanced web scraping...")
                try:
                    web_grants = self._enhanced_web_search(organization, search_params)
                    new_web_grants = [g for g in web_grants if g not in all_grants]
                    all_grants.extend(new_web_grants)
                    self.progress_update.emit(
                        f"🔗 Found {len(new_web_grants)} new grants via web scraping"
                    )
                except Exception as e:
                    self.error_occurred.emit(f"Web scraping error: {e}")
            
            # Step 5: AI ranking and filtering
            if not self.should_stop and all_grants and self.ai_assistant.is_available():
                self.progress_update.emit("📊 AI ranking and filtering...")
                try:
                    ranked_grants = self.ai_assistant.rank_grants_by_relevance(
                        all_grants, organization, limit=50
                    )
                    # Extract just the grants (without scores) for now
                    final_grants = [grant for grant, score in ranked_grants]
                    all_grants = final_grants
                    self.progress_update.emit(
                        f"🎯 Ranked and filtered to {len(all_grants)} relevant grants"
                    )
                except Exception as e:
                    self.error_occurred.emit(f"AI ranking error: {e}")
            
            # Emit results
            if not self.should_stop:
                self.grants_found.emit(all_grants)
                self.search_completed.emit(True)
                self.progress_update.emit(
                    f"✅ Search completed! Found {len(all_grants)} total grants"
                )
            else:
                self.search_completed.emit(False)
                self.progress_update.emit("❌ Search cancelled")
                
        except Exception as e:
            self.logger.error(f"Search worker error: {e}")
            self.error_occurred.emit(f"Unexpected error: {e}")
            self.search_completed.emit(False)
    
    def stop_search(self):
        """Stop the current search operation."""
        self.should_stop = True
        self.progress_update.emit("🛑 Stopping search...")
    
    def _search_database(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """Search local database for grants."""
        # Placeholder for database search
        # In real implementation, would query the database
        return []
    
    def _ai_web_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """Perform AI-enhanced web search."""
        try:
            # Get AI-suggested search terms
            search_terms = self.ai_assistant.suggest_search_terms(organization)
            
            # Use search terms to find grants
            # This would integrate with web APIs or scraping
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"AI web search error: {e}")
            return []
    
    def _enhanced_web_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """Perform enhanced web scraping with robust error handling."""
        grants = []
        
        try:
            # Define grant websites with selectors
            grant_sources = [
                {
                    'url': 'https://www.grants.gov/search-grants',
                    'fallbacks': [
                        'https://www.grants.gov/web/grants/search-grants.html'
                    ],
                    'selectors': {
                        'containers': [
                            '.search-result',
                            '.grant-listing',
                            '.opportunity-item'
                        ],
                        'title': ['.title', 'h3', '.grant-title'],
                        'description': ['.description', '.summary', 'p'],
                        'funder': ['.agency', '.funder', '.organization'],
                        'amount': ['.amount', '.funding', '.award'],
                        'deadline': ['.deadline', '.due-date', '.closing-date']
                    }
                }
            ]
            
            for source in grant_sources:
                if self.should_stop:
                    break
                
                soup = self.robust_scraper.fetch_with_fallbacks(
                    source['url'],
                    source.get('fallbacks', [])
                )
                
                if soup:
                    source_grants = self.robust_scraper.extract_grants_with_selectors(
                        soup,
                        source['selectors']
                    )
                    grants.extend(source_grants)
            
        except Exception as e:
            self.logger.error(f"Enhanced web search error: {e}")
        
        return grants


class EnhancedGrantSearchTab:
    """Enhanced grant search tab with threading support."""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.logger = logging.getLogger(__name__)
        
        # Threading components
        self.search_thread: Optional[QThread] = None
        self.search_worker: Optional[GrantSearchWorker] = None
        
        # UI components (would be passed from main GUI)
        self.progress_bar: Optional[QProgressBar] = None
        self.status_text: Optional[QTextEdit] = None
        self.results_list = None
        
        # Search state
        self.current_grants: List[Grant] = []
        self.is_searching = False
    
    def start_intelligent_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ):
        """
        Start intelligent grant search in background thread.
        
        Args:
            organization: Organization profile
            search_params: Search parameters
        """
        if self.is_searching:
            self.logger.warning("Search already in progress")
            return
        
        try:
            # Clean up previous thread if exists
            self._cleanup_thread()
            
            # Create new thread and worker
            self.search_thread = QThread()
            self.search_worker = GrantSearchWorker()
            
            # Move worker to thread
            self.search_worker.moveToThread(self.search_thread)
            
            # Connect signals
            self.search_worker.progress_update.connect(self._on_progress_update)
            self.search_worker.grants_found.connect(self._on_grants_found)
            self.search_worker.search_completed.connect(self._on_search_completed)
            self.search_worker.error_occurred.connect(self._on_error_occurred)
            
            # Connect thread signals
            self.search_thread.started.connect(
                lambda: self.search_worker.search_grants(organization, search_params)
            )
            self.search_thread.finished.connect(self._cleanup_thread)
            
            # Start search
            self.is_searching = True
            self.search_thread.start()
            
            # Update UI
            if self.progress_bar:
                self.progress_bar.setVisible(True)
            self._on_progress_update("🚀 Starting intelligent grant search...")
            
        except Exception as e:
            self.logger.error(f"Failed to start search: {e}")
            self._on_error_occurred(f"Failed to start search: {e}")
    
    def stop_search(self):
        """Stop the current search operation."""
        if self.search_worker and self.is_searching:
            self.search_worker.stop_search()
    
    def _on_progress_update(self, message: str):
        """Handle progress updates from worker thread."""
        try:
            if self.status_text:
                self.status_text.append(message)
                # Auto-scroll to bottom
                cursor = self.status_text.textCursor()
                cursor.movePosition(cursor.End)
                self.status_text.setTextCursor(cursor)
        except Exception as e:
            self.logger.error(f"Progress update error: {e}")
    
    def _on_grants_found(self, grants: List[Grant]):
        """Handle grants found by worker thread."""
        try:
            self.current_grants = grants
            
            # Update results list if available
            if self.results_list and hasattr(self.results_list, 'clear'):
                self.results_list.clear()
                
                for grant in grants:
                    display_text = f"{grant.title} ({grant.funder_name})"
                    self.results_list.addItem(display_text)
            
            self._on_progress_update(f"📋 Updated results: {len(grants)} grants")
            
        except Exception as e:
            self.logger.error(f"Error handling found grants: {e}")
    
    def _on_search_completed(self, success: bool):
        """Handle search completion."""
        try:
            self.is_searching = False
            
            if self.progress_bar:
                self.progress_bar.setVisible(False)
            
            if success:
                self._on_progress_update(
                    f"🎉 Search completed successfully! "
                    f"Found {len(self.current_grants)} grants"
                )
            else:
                self._on_progress_update("⚠️ Search was stopped or failed")
                
        except Exception as e:
            self.logger.error(f"Error handling search completion: {e}")
    
    def _on_error_occurred(self, error_message: str):
        """Handle errors from worker thread."""
        try:
            self.logger.error(f"Search error: {error_message}")
            self._on_progress_update(f"❌ Error: {error_message}")
        except Exception as e:
            self.logger.error(f"Error handling error: {e}")
    
    def _cleanup_thread(self):
        """Clean up thread resources."""
        try:
            if self.search_thread:
                if self.search_thread.isRunning():
                    self.search_thread.quit()
                    self.search_thread.wait(5000)  # Wait up to 5 seconds
                
                self.search_thread.deleteLater()
                self.search_thread = None
            
            if self.search_worker:
                self.search_worker.deleteLater()
                self.search_worker = None
                
        except Exception as e:
            self.logger.error(f"Thread cleanup error: {e}")
    
    def get_current_grants(self) -> List[Grant]:
        """Get the current list of grants."""
        return self.current_grants.copy()
    
    def is_search_active(self) -> bool:
        """Check if a search is currently active."""
        return self.is_searching


def apply_threading_to_existing_gui(qt_app_instance):
    """
    Apply threading enhancements to existing QT application.
    
    Args:
        qt_app_instance: Instance of the existing QT application
    """
    try:
        # Replace the search method with threaded version
        enhanced_search = EnhancedGrantSearchTab(qt_app_instance)
        
        # Store reference to enhanced search
        qt_app_instance.enhanced_search = enhanced_search
        
        # Override the intelligent_grant_search method
        original_search = qt_app_instance.intelligent_grant_search
        
        def threaded_intelligent_search():
            try:
                # Get organization profile
                profile = qt_app_instance.org_profile_tab.get_profile()
                if not profile:
                    qt_app_instance.results_list.clear()
                    qt_app_instance.results_list.addItem(
                        "Please load an organization profile first."
                    )
                    return
                
                # Get search parameters
                search_params = {
                    'country': qt_app_instance.country_combo.currentText(),
                    'state': qt_app_instance.state_combo.currentText(),
                    'keywords': qt_app_instance.search_input.text(),
                    'focus_area': qt_app_instance.focus_area_input.text(),
                    'min_amount': qt_app_instance.amount_min_input.text(),
                    'max_amount': qt_app_instance.amount_max_input.text(),
                    'eligibility': qt_app_instance.eligibility_input.text()
                }
                
                # Set up UI references for the enhanced search
                enhanced_search.results_list = qt_app_instance.results_list
                enhanced_search.status_text = getattr(
                    qt_app_instance, 'status_text', None
                )
                enhanced_search.progress_bar = getattr(
                    qt_app_instance, 'progress_bar', None
                )
                
                # Start threaded search
                enhanced_search.start_intelligent_search(profile, search_params)
                
            except Exception as e:
                logging.error(f"Threaded search error: {e}")
                qt_app_instance.results_list.clear()
                qt_app_instance.results_list.addItem(f"Search error: {e}")
        
        # Replace the method
        qt_app_instance.intelligent_grant_search = threaded_intelligent_search
        
        # Add stop search capability if button exists
        if hasattr(qt_app_instance, 'stop_search_btn'):
            qt_app_instance.stop_search_btn.clicked.connect(
                enhanced_search.stop_search
            )
        
        logging.info("Successfully applied threading enhancements to GUI")
        
    except Exception as e:
        logging.error(f"Failed to apply threading enhancements: {e}")


# Error handling for Qt applications
def setup_qt_error_handling():
    """Set up global error handling for Qt applications."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logging.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Try to show error in GUI if possible
        try:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText("An unexpected error occurred.")
            msg.setDetailedText(
                ''.join(traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                ))
            )
            msg.exec_()
        except Exception:
            pass  # GUI not available or already closed
    
    sys.excepthook = handle_exception
