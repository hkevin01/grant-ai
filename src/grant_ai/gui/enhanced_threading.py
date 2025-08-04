"""
Enhanced Qt GUI with robust threading and AI integration.
Prevents force quits during long-running operations.
"""
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

try:
    from PyQt5.QtCore import QObject, QThread, pyqtSignal
    from PyQt5.QtWidgets import QProgressBar, QTextEdit
except ImportError as e:
    logging.error("PyQt5 import failed: %s", e)
    raise

from grant_ai.core.exceptions import AIError, DatabaseError, NetworkError, ScraperError
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
        """Initialize the worker with required services."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.should_stop = False

        # Initialize services
        self.ai_assistant = AIAssistant()
        self.robust_scraper = RobustWebScraper()
        self.wv_scraper = WVGrantScraper()

        # Thread pool for parallel operations
        self.thread_pool = ThreadPoolExecutor(max_workers=3)

    def search_grants(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ):
        """
        Perform comprehensive grant search in background thread.

        Args:
            organization: Organization profile to match grants against
            search_params: Search parameters for filtering grants
        """
        try:
            self.should_stop = False
            all_grants = []

            # Step 1: Database search
            if not self.should_stop:
                self.progress_update.emit("🔍 Searching database...")
                try:
                    params = search_params.copy()
                    db_grants = self._search_database(
                        organization=organization,
                        search_params=params
                    )
                    all_grants.extend(db_grants)
                    self.progress_update.emit(
                        "📊 Found %d grants in database", len(db_grants)
                    )
                except DatabaseError as e:
                    self.logger.error("Database search failed: %s", e)
                    self.error_occurred.emit(str(e))

            # Step 2: AI-enhanced web search
            if not self.should_stop and self.ai_assistant.is_available():
                self.progress_update.emit("🤖 AI-enhanced web search...")
                try:
                    params = search_params.copy()
                    ai_grants = self._ai_web_search(
                        organization=organization,
                        search_params=params
                    )
                    new_grants = [g for g in ai_grants if g not in all_grants]
                    all_grants.extend(new_grants)
                    self.progress_update.emit(
                        "🧠 Found %d new grants via AI", len(new_grants)
                    )
                except AIError as e:
                    self.logger.error("AI search failed: %s", e)
                    self.error_occurred.emit(str(e))

            # Step 3: State/Regional scrapers
            if not self.should_stop:
                state = search_params.get('state', 'West Virginia')
                if state in ['West Virginia', 'All States']:
                    msg = "🏔️ Searching WV sources..."
                    self.progress_update.emit(msg)
                    try:
                        wv_grants = self.wv_scraper.scrape_all_sources()
                        new_grants = [
                            g for g in wv_grants if g not in all_grants
                        ]
                        all_grants.extend(new_grants)
                        self.progress_update.emit(
                            "🏛️ Found %d new WV grants", len(new_grants)
                        )
                    except ScraperError as e:
                        self.logger.error("WV scraper failed: %s", e)
                        self.error_occurred.emit(str(e))

            # Step 4: Enhanced web scraping with fallbacks
            if not self.should_stop:
                self.progress_update.emit("🌐 Enhanced web scraping...")
                try:
                    params = search_params.copy()
                    web_grants = self._enhanced_web_search(
                        organization=organization,
                        search_params=params
                    )
                    new_grants = [
                        g for g in web_grants if g not in all_grants
                    ]
                    all_grants.extend(new_grants)
                    self.progress_update.emit(
                        "🔗 Found %d new grants via web", len(new_grants)
                    )
                except NetworkError as e:
                    self.logger.error("Web scraping failed: %s", e)
                    self.error_occurred.emit(str(e))

            # Step 5: AI ranking and filtering
            if (not self.should_stop and all_grants and
                    self.ai_assistant.is_available()):
                self.progress_update.emit("📊 AI ranking and filtering...")
                try:
                    ranked_grants = self.ai_assistant.rank_grants_by_relevance(
                        all_grants, organization, limit=50
                    )
                    # Extract just the grants (without scores)
                    final_grants = [grant for grant, _ in ranked_grants]
                    all_grants = final_grants
                    self.progress_update.emit(
                        "🎯 Ranked and filtered to %d grants", len(all_grants)
                    )
                except AIError as e:
                    self.logger.error("AI ranking failed: %s", e)
                    self.error_occurred.emit(str(e))

            # Emit results
            if not self.should_stop:
                self.grants_found.emit(all_grants)
                self.search_completed.emit(True)
                self.progress_update.emit(
                    "✅ Found %d total grants", len(all_grants)
                )
            else:
                self.search_completed.emit(False)
                self.progress_update.emit("❌ Search cancelled")

        except Exception as e:
            self.logger.error("Unexpected error in search worker: %s", e)
            self.error_occurred.emit(str(e))
            self.search_completed.emit(False)
        finally:
            # Always cleanup thread pool
            self.thread_pool.shutdown(wait=False)

    def stop_search(self):
        """Stop the current search operation."""
        self.should_stop = True
        self.progress_update.emit("🛑 Stopping search...")
        self.thread_pool.shutdown(wait=False)

    def _search_database(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """
        Search local database for matching grants.

        Args:
            organization: Organization to match grants against
            search_params: Additional search parameters

        Returns:
            List of matching Grant objects

        Raises:
            DatabaseError: If database access fails
        """
        # This would be implemented to search the database
        # For now return empty list
        return []

    def __del__(self):
        """Cleanup resources on deletion."""
        self.thread_pool.shutdown(wait=True)

    def _ai_web_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """
        Perform AI-enhanced web search for grants.

        Args:
            organization: Organization to match grants against
            search_params: Additional search parameters

        Returns:
            List of matching Grant objects

        Raises:
            AIError: If AI operations fail
        """
        try:
            # Get AI-suggested search terms based on organization profile
            search_terms = self.ai_assistant.suggest_search_terms(organization)
            return self.ai_assistant.search_grants(search_terms)

        except Exception as e:
            self.logger.error("AI web search failed: %s", e)
            raise AIError(f"AI web search failed: {e}")

    def _enhanced_web_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ) -> List[Grant]:
        """
        Perform enhanced web scraping for grants.

        Args:
            organization: Organization to match grants against
            search_params: Additional search parameters

        Returns:
            List of matching Grant objects

        Raises:
            NetworkError: If web scraping fails
        """
        try:
            # Use thread pool for parallel scraping
            futures = []

            # Define grant sources with fallback URLs
            sources = [
                {
                    'url': 'https://www.grants.gov/search-grants',
                    'fallbacks': [
                        'https://www.grants.gov/web/grants/search-grants.html'
                    ]
                },
                {
                    'url': 'https://www.nsf.gov/funding/',
                    'fallbacks': [
                        'https://www.nsf.gov/funding/pgm_list.jsp'
                    ]
                }
            ]

            # Submit scraping tasks to thread pool
            for source in sources:
                future = self.thread_pool.submit(
                    self.robust_scraper.fetch_with_fallbacks,
                    source['url'],
                    source['fallbacks']
                )
                futures.append(future)

            # Collect results
            grants = []
            for future in futures:
                if not self.should_stop:
                    try:
                        soup = future.result()
                        if soup:
                            source_grants = (
                                self.robust_scraper
                                .extract_grants_with_selectors(soup)
                            )
                            grants.extend(source_grants)
                    except Exception as e:
                        self.logger.error(
                            "Error fetching from source: %s", str(e)
                        )

            return grants

        except Exception as e:
            self.logger.error("Enhanced web search failed: %s", e)
            raise NetworkError(f"Enhanced web search failed: {e}")


class EnhancedGrantSearchTab:
    """Enhanced grant search tab with threading support."""

    CACHE_SIZE = 50  # Maximum number of cached results

    def __init__(self, parent_widget):
        """Initialize the tab with memory management."""
        self.parent = parent_widget
        self.logger = logging.getLogger(__name__)

        # Threading components
        self.search_thread: Optional[QThread] = None
        self.search_worker: Optional[GrantSearchWorker] = None

        # UI components (would be passed from main GUI)
        self.progress_bar: Optional[QProgressBar] = None
        self.status_text: Optional[QTextEdit] = None
        self.results_list = None

        # Search state with memory management
        self.current_grants: List[Grant] = []
        self.is_searching = False
        self._cache = {}  # Results cache
        self._result_count = 0  # For progress tracking

    def start_intelligent_search(
        self,
        organization: OrganizationProfile,
        search_params: dict
    ):
        """Start intelligent grant search in background thread."""
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
            self._connect_worker_signals()

            # Start search
            self.is_searching = True
            self.search_thread.start()

            # Update UI
            self._show_search_starting()

        except Exception as e:
            self.logger.error("Failed to start search: %s", e)
            self._on_error_occurred(str(e))

    def stop_search(self):
        """Stop the current search operation."""
        try:
            if self.search_worker:
                self.search_worker.stop_search()
            self._cleanup_thread()
        except Exception as e:
            self.logger.error("Error stopping search: %s", e)

    def _cleanup_thread(self):
        """Clean up thread and worker to prevent memory leaks."""
        try:
            if self.search_worker:
                # Disconnect all signals
                self._disconnect_worker_signals()

                # Stop and delete worker
                self.search_worker.stop_search()
                self.search_worker.deleteLater()
                self.search_worker = None

            if self.search_thread:
                # Stop and wait for thread
                if self.search_thread.isRunning():
                    self.search_thread.quit()
                    self.search_thread.wait()

                # Delete thread
                self.search_thread.deleteLater()
                self.search_thread = None

            # Clear search state
            self.is_searching = False

            # Update UI
            if self.progress_bar:
                self.progress_bar.setVisible(False)

        except Exception as e:
            self.logger.error("Error during thread cleanup: %s", e)

    def _connect_worker_signals(self):
        """Connect all worker signals."""
        if self.search_worker:
            self.search_worker.progress_update.connect(self._on_progress_update)
            self.search_worker.grants_found.connect(self._on_grants_found)
            self.search_worker.search_completed.connect(
                self._on_search_completed
            )
            self.search_worker.error_occurred.connect(self._on_error_occurred)

            # Connect thread start signal
            self.search_thread.started.connect(
                lambda: self.search_worker.search_grants(
                    organization,
                    search_params
                )
            )
            self.search_thread.finished.connect(self._cleanup_thread)

    def _disconnect_worker_signals(self):
        """Disconnect all worker signals to prevent memory leaks."""
        if self.search_worker:
            self.search_worker.progress_update.disconnect()
            self.search_worker.grants_found.disconnect()
            self.search_worker.search_completed.disconnect()
            self.search_worker.error_occurred.disconnect()

    def _manage_cache(self):
        """Manage the results cache to prevent memory bloat."""
        if len(self._cache) > self.CACHE_SIZE:
            # Get oldest keys to remove
            keys = sorted(self._cache.keys())
            remove_count = len(self._cache) - self.CACHE_SIZE
            oldest_keys = keys[:remove_count]

            # Remove oldest entries
            for key in oldest_keys:
                del self._cache[key]

    def _show_search_starting(self):
        """Update UI to show search is starting."""
        if self.progress_bar:
            self.progress_bar.setVisible(True)
        self._on_progress_update("🚀 Starting intelligent grant search...")

    def _on_progress_update(self, message: str):
        """Handle progress updates."""
        if self.status_text:
            self.status_text.append(message)

    def _on_grants_found(self, grants: List[Grant]):
        """Handle found grants with memory management."""
        try:
            # Update result count for progress tracking
            self._result_count = len(grants)

            # Store in cache with timestamp
            import time
            cache_key = str(time.time())
            self._cache[cache_key] = grants

            # Update current grants
            self.current_grants = grants

            # Manage cache size
            self._manage_cache()

            # Update UI
            if self.results_list:
                self.results_list.clear()
                for grant in grants:
                    self.results_list.addItem(grant.title)

            # Update progress
            self._on_progress_update(f"📋 Found {self._result_count} grants")

        except Exception as e:
            self.logger.error("Error handling grants: %s", e)
            self._on_error_occurred(str(e))

    def _on_search_completed(self, success: bool):
        """Handle search completion with cleanup."""
        try:
            if success:
                msg = "✅ Search completed successfully!"
                if self._result_count > 0:
                    msg += f" Found {self._result_count} grants."
            else:
                msg = "⚠️ Search cancelled or failed"

            if self.status_text:
                self.status_text.append(msg)

        except Exception as e:
            self.logger.error("Error handling completion: %s", e)

        finally:
            # Always ensure cleanup
            self._cleanup_thread()

    def _on_error_occurred(self, error_msg: str):
        """Handle errors with cleanup."""
        self.logger.error("Search error: %s", error_msg)

        if self.status_text:
            self.status_text.append(f"❌ Error: {error_msg}")

        # Ensure cleanup
        self._cleanup_thread()

    def __del__(self):
        """Ensure cleanup on deletion."""
        self._cleanup_thread()


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
