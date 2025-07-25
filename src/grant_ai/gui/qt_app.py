"""
PyQt5 GUI for Grant Research AI Project
"""
import json
import os
import sys
import traceback
from pathlib import Path

# Set environment variables to suppress Qt warnings
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Force X11 backend instead of Wayland

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from grant_ai.analysis.grant_researcher import GrantResearcher
from grant_ai.core.db import SessionLocal
from grant_ai.gui.enhanced_past_grants_tab import EnhancedPastGrantsTab
from grant_ai.gui.icon_manager import icon_manager
from grant_ai.gui.predictive_grants_tab import PredictiveGrantsTab
from grant_ai.gui.questionnaire_widget import QuestionnaireWidget
from grant_ai.models import OrganizationProfile
from grant_ai.models.grant import Grant as GrantModel
from grant_ai.models.grant import GrantORM
from grant_ai.scrapers.wv_grants import WVGrantScraper
from grant_ai.utils.ai_grant_agent import AIGrantAgent
from grant_ai.utils.preset_organizations import preset_manager

PROFILE_PATH = Path.home() / ".grant_ai_profile.json"
GRANTS_PATH = Path.home() / ".grant_ai_grants.json"


class GrantSearchThread(QThread):
    """Background thread for grant searching to prevent UI freezing."""
    
    # Signals for communicating with the main thread
    status_update = pyqtSignal(str)  # Status message
    grants_found = pyqtSignal(list)  # List of grants found
    search_complete = pyqtSignal(list)  # Final list of all grants
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self, profile, existing_grants, selected_country, selected_state, 
                 ai_agent, grant_researcher, db_session=None):
        super().__init__()
        self.profile = profile
        self.existing_grants = existing_grants
        self.selected_country = selected_country
        self.selected_state = selected_state
        self.ai_agent = ai_agent
        self.grant_researcher = grant_researcher
        self.db_session = db_session
        self.all_grants = existing_grants.copy()
        
    def run(self):
        """Run the grant search in the background thread."""
        try:
            # Step 1: Search database for new grants
            self.status_update.emit("💾 Searching database for matching grants...")
            try:
                db_grants = self._search_database_for_profile()
                new_db_grants = [g for g in db_grants if g not in self.existing_grants]
                self.all_grants.extend(new_db_grants)
                self.status_update.emit(f"   Found {len(new_db_grants)} new grants in database")
                if new_db_grants:
                    self.grants_found.emit(new_db_grants)
            except Exception as e:
                self.status_update.emit(f"   ⚠️ Database search failed: {str(e)[:100]}...")
                
            # Step 2: AI Agent discovery
            self.status_update.emit("🤖 Using AI Agent for web search...")
            try:
                ai_grants = self.ai_agent.search_grants_for_profile(self.profile)
                new_ai_grants = [g for g in ai_grants if g not in self.all_grants]
                self.all_grants.extend(new_ai_grants)
                self.status_update.emit(f"   Found {len(new_ai_grants)} new grants via AI Agent")
                if new_ai_grants:
                    self.grants_found.emit(new_ai_grants)
            except Exception as e:
                self.status_update.emit(f"   ⚠️ AI search failed: {str(e)[:100]}...")
                
            # Step 3: WV Scraper if applicable
            if self.selected_state == "West Virginia":
                self.status_update.emit("🏔️ Searching West Virginia specific grants...")
                try:
                    wv_scraper = WVGrantScraper()
                    wv_grants = wv_scraper.scrape_all_sources()
                    new_wv_grants = [g for g in wv_grants if g not in self.all_grants]
                    self.all_grants.extend(new_wv_grants)
                    self.status_update.emit(f"   Found {len(new_wv_grants)} WV grants")
                    if new_wv_grants:
                        self.grants_found.emit(new_wv_grants)
                except Exception as e:
                    self.status_update.emit(f"   ⚠️ WV search failed: {str(e)[:100]}...")
                    
            # Step 4: Additional scrapers based on location
            if self.selected_country and self.selected_state:
                self.status_update.emit(f"🌐 Searching {self.selected_country}/{self.selected_state} grants...")
                try:
                    location_grants = self.grant_researcher.find_grants_by_location(
                        self.selected_country, self.selected_state
                    )
                    new_location_grants = [g for g in location_grants if g not in self.all_grants]
                    self.all_grants.extend(new_location_grants)
                    self.status_update.emit(f"   Found {len(new_location_grants)} location-based grants")
                    if new_location_grants:
                        self.grants_found.emit(new_location_grants)
                except Exception as e:
                    self.status_update.emit(f"   ⚠️ Location search failed: {str(e)[:100]}...")
                    
            # Emit completion signal
            self.search_complete.emit(self.all_grants)
            
        except Exception as e:
            self.error_occurred.emit(f"Search failed: {str(e)}")
            
    def _search_database_for_profile(self):
        """Search database for grants matching the profile."""
        try:
            # Use the provided session or create a new one
            session = self.db_session if self.db_session else SessionLocal()
            
            try:
                # Search for grants that match the organization's focus areas
                focus_areas = getattr(self.profile, 'focus_areas', [])
                if not focus_areas:
                    return []
                    
                matching_grants = []
                for focus_area in focus_areas:
                    grants = session.query(GrantORM).filter(
                        GrantORM.focus_areas.contains(focus_area)
                    ).limit(20).all()
                    
                    for grant_orm in grants:
                        grant_model = GrantModel(
                            id=grant_orm.id,
                            title=grant_orm.title,
                            description=grant_orm.description or "",
                            funder_name=grant_orm.funder_name or "",
                            funder_type=grant_orm.funder_type or "",
                            amount_min=grant_orm.amount_min,
                            amount_max=grant_orm.amount_max,
                            amount_typical=grant_orm.amount_typical,
                            focus_areas=grant_orm.focus_areas or [],
                            source=grant_orm.source or "",
                            source_url=grant_orm.source_url or "",
                        )
                        if grant_model not in matching_grants:
                            matching_grants.append(grant_model)
                            
                return matching_grants[:50]  # Limit results
                
            finally:
                if not self.db_session:  # Only close if we created the session
                    session.close()
                    
        except Exception as e:
            print(f"Database search error: {e}")
            return []


class GrantSearchTab(QWidget):
    def __init__(self, org_profile_tab):
        super().__init__()
        self.org_profile_tab = org_profile_tab
        layout = QVBoxLayout()
        
        # Search description field (read-only)
        self.search_description = QTextEdit()
        self.search_description.setMaximumHeight(80)
        self.search_description.setPlaceholderText("Search description will appear here when a profile is loaded...")
        self.search_description.setReadOnly(True)
        
        # Location selection
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Country:"))
        self.country_combo = QComboBox()
        self.country_combo.addItems(["USA", "Canada", "United Kingdom", "Australia"])
        self.country_combo.setCurrentText("USA")
        location_layout.addWidget(self.country_combo)
        
        location_layout.addWidget(QLabel("State:"))
        self.state_combo = QComboBox()
        self.state_combo.addItems([
            "West Virginia", "All States", "California", "New York", "Texas", 
            "Florida", "Pennsylvania", "Ohio", "Michigan", "Illinois"
        ])
        self.state_combo.setCurrentText("West Virginia")
        location_layout.addWidget(self.state_combo)
        
        # Search fields
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords or filters...")
        self.focus_area_input = QLineEdit()
        self.focus_area_input.setPlaceholderText(
            "Focus area (e.g. housing, education)"
        )
        self.amount_min_input = QLineEdit()
        self.amount_min_input.setPlaceholderText("Min amount")
        self.amount_max_input = QLineEdit()
        self.amount_max_input.setPlaceholderText("Max amount")
        self.eligibility_input = QLineEdit()
        self.eligibility_input.setPlaceholderText(
            "Eligibility (e.g. nonprofit)"
        )
        
        # Search buttons - Single intelligent search button
        self.intelligent_search_btn = icon_manager.create_button(
            'search', 'Intelligent Grant Search'
        )
        
        # Results
        self.results_list = QListWidget()
        
        # Add widgets to layout
        layout.addWidget(QLabel("Grant Search"))
        layout.addWidget(QLabel("Search Description:"))
        layout.addWidget(self.search_description)
        layout.addWidget(QLabel("Location:"))
        layout.addLayout(location_layout)
        layout.addWidget(QLabel("Search Fields:"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.focus_area_input)
        layout.addWidget(self.amount_min_input)
        layout.addWidget(self.amount_max_input)
        layout.addWidget(self.eligibility_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.intelligent_search_btn)
        layout.addLayout(button_layout)
        
        layout.addWidget(self.results_list)
        self.setLayout(layout)
        
        # Connect signals
        self.intelligent_search_btn.clicked.connect(self.intelligent_grant_search)
        self.results_list.itemClicked.connect(self.show_grant_details)
        
        # Initialize components
        self.researcher = GrantResearcher()
        self.ai_agent = AIGrantAgent()
        self.wv_scraper = WVGrantScraper()
        self.load_grants()
        
        # Connect profile tab to auto-fill and suggest
        self.org_profile_tab.profile_loaded.connect(self.auto_fill_and_suggest)
        
        # Threading support
        self.scraping_workers = []
        self.is_searching = False
        self.search_thread = None
        
        # Initialize grant map for storing grant objects
        self.grant_map = {}

    def load_grants(self):
        """Load grants from file into the researcher for in-memory matching."""
        # Optionally load grants into the researcher for in-memory matching
        if GRANTS_PATH.exists():
            try:
                with open(GRANTS_PATH, "r", encoding="utf-8") as f:
                    grants_data = json.load(f)
                grants = [GrantModel(**g) for g in grants_data]
                self.researcher.add_grants(grants)
                print(f"✅ Loaded {len(grants)} grants from file")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON error in grants file: {e}")
                print(f"📁 Backing up corrupted file and creating fresh grants database")
                self.handle_corrupted_grants_file()
            except Exception as e:
                print(f"⚠️ Error loading grants file: {e}")
                self.handle_corrupted_grants_file()
    
    def handle_corrupted_grants_file(self):
        """Handle corrupted grants file by backing it up and creating a new one."""
        try:
            # Backup the corrupted file
            backup_path = GRANTS_PATH.with_suffix('.json.backup')
            if GRANTS_PATH.exists():
                import shutil
                shutil.move(str(GRANTS_PATH), str(backup_path))
                print(f"🔄 Backed up corrupted file to {backup_path}")
            
            # Create a fresh grants file with empty array
            self.create_fresh_grants_file()
            
        except Exception as e:
            print(f"❌ Error handling corrupted grants file: {e}")
    
    def create_fresh_grants_file(self):
        """Create a fresh grants file with sample data."""
        try:
            sample_grants = [
                {
                    "id": "sample_001",
                    "title": "Education Innovation Grant",
                    "description": "Support for innovative education programs",
                    "funder_name": "Sample Foundation",
                    "funder_type": "foundation",
                    "funding_type": "grant",
                    "amount_min": 10000,
                    "amount_max": 100000,
                    "amount_typical": 50000,
                    "status": "open",
                    "focus_areas": ["education", "innovation"],
                    "source": "Sample Data",
                    "source_url": "https://example.com/grant"
                }
            ]
            
            with open(GRANTS_PATH, "w", encoding="utf-8") as f:
                json.dump(sample_grants, f, indent=2)
            
            print(f"✅ Created fresh grants file at {GRANTS_PATH}")
            
            # Load the new grants
            grants = [GrantModel(**g) for g in sample_grants]
            self.researcher.add_grants(grants)
            
        except Exception as e:
            print(f"❌ Error creating fresh grants file: {e}")

    def auto_fill_and_suggest(self, profile=None, auto_search=False):
        """Auto-fill search fields and suggest grants based on profile.
        
        Args:
            profile: Organization profile to use for auto-filling
            auto_search: Whether to automatically trigger a search
        """
        if profile is None:
            profile = self.org_profile_tab.get_profile()
        if not profile:
            return
        
        # Auto-fill search fields
        if profile.focus_areas:
            focus_text = ", ".join([
                str(fa).replace('_', ' ') for fa in profile.focus_areas
            ])
            self.focus_area_input.setText(focus_text)
        
        # Auto-fill amount fields
        if (hasattr(profile, 'preferred_grant_size') and
                profile.preferred_grant_size):
            min_amt, max_amt = profile.preferred_grant_size
            self.amount_min_input.setText(str(min_amt))
            self.amount_max_input.setText(str(max_amt))
        else:
            # Set default amounts if not specified
            self.amount_min_input.setText("1000")
            self.amount_max_input.setText("100000")
        
        # Auto-fill eligibility based on target demographics
        if (hasattr(profile, 'target_demographics') and
                profile.target_demographics):
            demo_text = ", ".join(profile.target_demographics)
            self.eligibility_input.setText(demo_text)
        else:
            # Set default eligibility
            self.eligibility_input.setText("nonprofit, education")
        
        # Auto-fill search keywords based on focus areas and name
        search_keywords = []
        if profile.name:
            # First word of name
            search_keywords.append(profile.name.split()[0])
        if profile.focus_areas:
            search_keywords.extend([
                str(fa).replace('_', ' ') for fa in profile.focus_areas[:2]
            ])
        if profile.location:
            search_keywords.append(profile.location.split(',')[0])  # City name
        
        if search_keywords:
            self.search_input.setText(" ".join(search_keywords))
        
        # Set location based on profile
        if profile.location:
            if "west virginia" in profile.location.lower():
                self.state_combo.setCurrentText("West Virginia")
            else:
                # Try to match state from location
                for i in range(self.state_combo.count()):
                    state = self.state_combo.itemText(i)
                    if state.lower() in profile.location.lower():
                        self.state_combo.setCurrentText(state)
                        break
        
        # Generate search description
        self.update_search_description(profile)
        
        # Clear existing results and show ready message
        self.results_list.clear()
        self.results_list.addItem(
            "✅ Profile loaded and search fields populated. "
            "Click 'Intelligent Grant Search' to begin searching."
        )
        
        # Only trigger automatic search if explicitly requested
        if auto_search:
            self.intelligent_grant_search()

    def update_search_description(self, profile):
        """Update the search description field with a natural language description."""
        if not profile:
            return
        
        # Build description based on profile
        desc_parts = []
        
        # Organization info
        desc_parts.append(f"Searching for grants for {profile.name}")
        
        # Mission statement if available
        if hasattr(profile, 'mission_statement') and profile.mission_statement:
            desc_parts.append(f"({profile.mission_statement})")
        
        # Focus areas
        if profile.focus_areas:
            focus_text = ", ".join([str(fa).replace('_', ' ') for fa in profile.focus_areas])
            desc_parts.append(f"focusing on {focus_text}")
        
        # Location with more detail
        selected_state = self.state_combo.currentText()
        selected_country = self.country_combo.currentText()
        if hasattr(profile, 'region') and profile.region:
            desc_parts.append(f"in the {profile.region}")
        if selected_state != "All States":
            desc_parts.append(f"specifically in {selected_state}")
        if hasattr(profile, 'county') and profile.county:
            desc_parts.append(f"({profile.county})")
        desc_parts.append(f"({selected_country})")
        
        # Amount range
        if profile.preferred_grant_size:
            min_amt, max_amt = profile.preferred_grant_size
            desc_parts.append(f"with preferred amounts between ${min_amt:,} and ${max_amt:,}")
        
        # Target demographics
        if hasattr(profile, 'target_demographics') and profile.target_demographics:
            demo_text = ", ".join(profile.target_demographics)
            desc_parts.append(f"serving {demo_text}")
        
        # Program types
        if profile.program_types:
            prog_text = ", ".join([str(pt).replace('_', ' ') for pt in profile.program_types])
            desc_parts.append(f"for {prog_text} programs")
        
        # Key programs if available
        if hasattr(profile, 'key_programs') and profile.key_programs:
            key_prog_text = ", ".join(profile.key_programs)
            desc_parts.append(f"including {key_prog_text}")
        
        # Offerings if available
        if hasattr(profile, 'offerings') and profile.offerings:
            offerings_text = ", ".join(profile.offerings)
            desc_parts.append(f"providing {offerings_text}")
        
        # Impact metrics if available
        if hasattr(profile, 'impact_metrics') and profile.impact_metrics:
            if 'youth_served_2018' in profile.impact_metrics:
                desc_parts.append(f"serving {profile.impact_metrics['youth_served_2018']}+ youth annually")
        
        description = " ".join(desc_parts) + "."
        self.search_description.setPlainText(description)

    def intelligent_grant_search(self):
        """Intelligent grant search using background thread to prevent UI freezing."""
        profile = self.org_profile_tab.get_profile()
        if not profile:
            self.results_list.clear()
            self.results_list.addItem("Please load an organization profile first.")
            return
        
        # Disable search button to prevent multiple simultaneous searches
        self.intelligent_search_btn.setEnabled(False)
        self.intelligent_search_btn.setText("Searching...")
        
        # Keep existing grants in the list
        existing_items = []
        existing_grants = []
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if item and hasattr(self, 'grant_map') and item.text() in self.grant_map:
                existing_items.append(item.text())
                existing_grants.append(self.grant_map[item.text()])
        
        # Add status message
        if existing_items:
            self.results_list.addItem("🔄 Keeping existing grants and searching for new ones...")
        else:
            self.results_list.addItem("🔍 Starting intelligent grant search...")
        
        # Get location information
        selected_country = self.country_combo.currentText()
        selected_state = self.state_combo.currentText()
        
        # Create and configure the search thread
        self.search_thread = GrantSearchThread(
            profile=profile,
            existing_grants=existing_grants,
            selected_country=selected_country,
            selected_state=selected_state,
            ai_agent=self.ai_agent,
            grant_researcher=self.researcher
        )
        
        # Connect thread signals to UI update methods
        self.search_thread.status_update.connect(self._on_search_status_update)
        self.search_thread.grants_found.connect(self._on_grants_found)
        self.search_thread.search_complete.connect(self._on_search_complete)
        self.search_thread.error_occurred.connect(self._on_search_error)
        
        # Start the background search
        self.search_thread.start()
        
    def _on_search_status_update(self, message):
        """Handle status updates from the search thread."""
        self.results_list.addItem(message)
        # Auto-scroll to bottom to show latest updates
        self.results_list.scrollToBottom()
        
    def _on_grants_found(self, new_grants):
        """Handle new grants found during search."""
        for grant in new_grants:
            self._add_grant_to_ui(grant)
            
    def _on_search_complete(self, all_grants):
        """Handle search completion."""
        # Re-enable the search button
        self.intelligent_search_btn.setEnabled(True)
        icon_manager.set_button_icon(
            self.intelligent_search_btn, 'search', 'Intelligent Search'
        )
        
        # Show completion message
        total_grants = len(all_grants)
        success_icon = icon_manager.get_icon_text('success')
        status_text = (
            f"{success_icon} Search completed! "
            f"Found {total_grants} total grants."
        )
        self.results_list.addItem(status_text)
        self.results_list.scrollToBottom()
        
        # Save grants to local storage
        try:
            self._save_grants_to_file(all_grants)
        except Exception as e:
            print(f"Failed to save grants: {e}")
            
    def _on_search_error(self, error_message):
        """Handle search errors."""
        # Re-enable the search button
        self.intelligent_search_btn.setEnabled(True)
        icon_manager.set_button_icon(
            self.intelligent_search_btn, 'search', 'Intelligent Search'
        )
        
        # Show error message
        error_icon = icon_manager.get_icon_text('error')
        self.results_list.addItem(f"{error_icon} {error_message}")
        self.results_list.scrollToBottom()
        
    def _add_grant_to_ui(self, grant):
        """Add a grant to the UI list."""
        # Create grant map if it doesn't exist
        if not hasattr(self, 'grant_map'):
            self.grant_map = {}
            
        # Format grant display text
        amount_text = ""
        if hasattr(grant, 'amount_typical') and grant.amount_typical:
            amount_text = f" (${grant.amount_typical:,})"
        elif hasattr(grant, 'amount_max') and grant.amount_max:
            amount_text = f" (up to ${grant.amount_max:,})"
            
        display_text = f"{grant.title}{amount_text}"
        
        # Add to UI if not already present
        # Add to UI if not already present
        if display_text not in self.grant_map:
            self.grant_map[display_text] = grant
            self.results_list.addItem(display_text)
            
    def _save_grants_to_file(self, grants):
        """Save grants to local file storage."""
        try:
            grants_data = []
            for grant in grants:
                grant_dict = {
                    'id': grant.id,
                    'title': grant.title,
                    'description': grant.description,
                    'funder_name': grant.funder_name,
                    'funder_type': grant.funder_type,
                    'amount_typical': grant.amount_typical,
                    'amount_min': grant.amount_min,
                    'amount_max': grant.amount_max,
                    'focus_areas': grant.focus_areas,
                    'source': grant.source,
                    'source_url': (str(grant.source_url)
                                   if grant.source_url else None)
                }
                grants_data.append(grant_dict)
            
            with open(GRANTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(grants_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving grants to file: {e}")
            import traceback
            traceback.print_exc()

    def _search_database_for_profile(self, profile):
        """Search database for grants matching the profile."""
        try:
            session = SessionLocal()
            query = session.query(GrantORM)
            
            # Use focus areas for filtering
            focus_areas = [str(fa).lower() for fa in getattr(profile, 'focus_areas', [])]
            if focus_areas:
                # Search for any focus area
                for focus in focus_areas:
                    query = query.filter(GrantORM.focus_areas.contains(focus))
            
            # Use amount range
            min_amt, max_amt = getattr(profile, 'preferred_grant_size', (1000, 100000))
            if min_amt is not None:
                query = query.filter(
                    GrantORM.amount_min.is_(None) | 
                    (GrantORM.amount_min >= min_amt)
                )
            if max_amt is not None:
                query = query.filter(
                    GrantORM.amount_max.is_(None) | 
                    (GrantORM.amount_max <= max_amt)
                )
            
            # Use search input if provided
            if self.search_input.text().strip():
                search_text = self.search_input.text().strip()
                query = query.filter(GrantORM.title.ilike(f"%{search_text}%"))
            
            # Use focus area input if provided
            if self.focus_area_input.text().strip():
                focus = self.focus_area_input.text().strip().split(",")[0].lower()
                query = query.filter(GrantORM.focus_areas.contains(focus))
            
            # Use amount inputs if provided
            if self.amount_min_input.text().strip().isdigit():
                min_amt = int(self.amount_min_input.text().strip())
                query = query.filter(
                    GrantORM.amount_min.is_(None) | 
                    (GrantORM.amount_min >= min_amt)
                )
            if self.amount_max_input.text().strip().isdigit():
                max_amt = int(self.amount_max_input.text().strip())
                query = query.filter(
                    GrantORM.amount_max.is_(None) | 
                    (GrantORM.amount_max <= max_amt)
                )
            
            # Use eligibility input if provided
            if self.eligibility_input.text().strip():
                elig = self.eligibility_input.text().strip().split(",")[0].lower()
                query = query.filter(GrantORM.eligibility_types.contains(elig))
            
            grants = query.limit(20).all()  # Limit to 20 results
            session.close()
            
            # Convert GrantORM to Grant models
            grant_models = []
            for grant_orm in grants:
                try:
                    grant_model = GrantModel(
                        id=grant_orm.id,
                        title=grant_orm.title,
                        description=grant_orm.description,
                        funder_name=grant_orm.funder_name,
                        funder_type=grant_orm.funder_type,
                        funding_type=grant_orm.funding_type,
                        amount_min=grant_orm.amount_min,
                        amount_max=grant_orm.amount_max,
                        amount_typical=grant_orm.amount_typical,
                        status=(grant_orm.status.value 
                                if hasattr(grant_orm.status, 'value')
                                else str(grant_orm.status) 
                                if grant_orm.status else None),
                        eligibility_types=grant_orm.eligibility_types,
                        focus_areas=grant_orm.focus_areas,
                        source=grant_orm.source,
                        source_url=grant_orm.source_url,
                        contact_email=grant_orm.contact_email,
                        contact_phone=grant_orm.contact_phone,
                        application_url=grant_orm.application_url,
                        last_updated=grant_orm.last_updated,
                        created_at=grant_orm.created_at
                    )
                    grant_models.append(grant_model)
                except Exception as e:
                    print(f"Error converting GrantORM to Grant model: {e}")
                    continue
            
            return grant_models
            
        except Exception as e:
            print(f"Error searching database: {e}")
            return []

    def save_grants_to_db(self, grants):
        """Save discovered grants to the database."""
        try:
            session = SessionLocal()
            
            for grant in grants:
                # Check if grant already exists
                existing = session.query(GrantORM).filter(
                    GrantORM.title == grant.title,
                    GrantORM.funder_name == grant.funder_name
                ).first()
                
                if not existing:
                    # Convert URLs to strings to avoid HttpUrl issues
                    source_url_str = str(grant.source_url) if grant.source_url else None
                    application_url_str = str(grant.application_url) if grant.application_url else None
                    information_url_str = str(grant.information_url) if grant.information_url else None
                    
                    # Convert Grant model to GrantORM with proper enum handling
                    grant_orm = GrantORM(
                        id=grant.id,
                        title=grant.title,
                        description=grant.description,
                        funder_name=grant.funder_name,
                        funder_type=grant.funder_type,
                        funding_type=grant.funding_type.value if hasattr(grant.funding_type, 'value') else str(grant.funding_type) if grant.funding_type else None,
                        amount_min=grant.amount_min,
                        amount_max=grant.amount_max,
                        amount_typical=grant.amount_typical,
                        status=grant.status.value if hasattr(grant.status, 'value') else str(grant.status) if grant.status else None,
                        eligibility_types=[e.value if hasattr(e, 'value') else str(e) for e in grant.eligibility_types] if grant.eligibility_types else [],
                        focus_areas=grant.focus_areas,
                        source=grant.source,
                        source_url=source_url_str,
                        contact_email=grant.contact_email,
                        contact_phone=grant.contact_phone,
                        application_url=application_url_str,
                        information_url=information_url_str,
                        last_updated=grant.last_updated,
                        created_at=grant.created_at
                    )
                    session.add(grant_orm)
            
            session.commit()
            session.close()
            
        except Exception as e:
            print(f"Error saving grants to database: {e}")
            traceback.print_exc()
            # Don't fail the search if database save fails

    def show_grant_details(self, item):
        grant = self.grant_map.get(item.text())
        if not grant:
            return

        def safe_join(val):
            if isinstance(val, list):
                return ', '.join(str(x) for x in val)
            return str(val) if val else ''

        # Create a more comprehensive details display
        details = f"""
GRANT DETAILS
{'='*50}

Title: {grant.title}
Funder: {grant.funder_name}
Amount Range: ${grant.amount_min:,} - ${grant.amount_max:,}

Focus Areas: {safe_join(getattr(grant, 'focus_areas', []))}
Eligibility Types: {safe_join(getattr(grant, 'eligibility_types', []))}

Description:
{grant.description}

Application URL: {grant.application_url}

Additional Information:
- Grant ID: {getattr(grant, 'id', 'N/A')}
- Deadline: {getattr(grant, 'application_deadline', 'N/A')}
- Application Type: {getattr(grant, 'funding_type', 'N/A')}
- Geographic Focus: {getattr(grant, 'geographic_restrictions', 'N/A')}
- Target Demographics: {safe_join(getattr(grant, 'target_demographics', []))}
- Program Types: {safe_join(getattr(grant, 'program_types', []))}

Contact Information:
- Contact Name: {getattr(grant, 'contact_name', 'N/A')}
- Contact Email: {getattr(grant, 'contact_email', 'N/A')}
- Contact Phone: {getattr(grant, 'contact_phone', 'N/A')}

Source: {getattr(grant, 'source', 'Unknown')}
        """

        # Create a proper dialog window
        dialog = QDialog()
        dialog.setWindowTitle(f"Grant Details: {grant.title}")
        dialog.setModal(True)
        dialog.resize(700, 600)
        
        layout = QVBoxLayout()
        
        # Create text display
        text_edit = QTextEdit()
        text_edit.setPlainText(details)
        text_edit.setReadOnly(True)
        text_edit.setFontFamily("Courier")
        text_edit.setFontPointSize(10)
        layout.addWidget(text_edit)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(details))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec_()

    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")


class OrgProfileTab(QWidget):
    # Add signals for profile loading and changes
    profile_loaded = pyqtSignal(object)
    profile_changed = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Title and description
        title_label = QLabel("Organization Profile")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        desc_label = QLabel("Set up your organization's profile to help find relevant grants. This information will be used to auto-fill grant searches and match you with suitable funding opportunities.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # Form layout for the main fields
        form_layout = QFormLayout()
        
        # Preset organizations section
        preset_label = QLabel("Quick Start - Choose a Preset:")
        preset_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 10px;")
        layout.addWidget(preset_label)
        
        preset_desc = QLabel("Select a preset organization to quickly load a complete profile, or choose 'Custom Organization' to start from scratch.")
        preset_desc.setWordWrap(True)
        preset_desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(preset_desc)
        
        # Enhanced preset combo with loading indicator
        preset_layout = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Loading Presets... --")
        self.preset_combo.currentTextChanged.connect(self.load_preset_profile)
        self.preset_combo.setToolTip("Choose a preset organization profile or start with a custom one")
        
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setMaximum(0)  # Indeterminate progress
        
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.loading_indicator)
        form_layout.addRow("Preset Organizations:", preset_layout)
        
        # Organization details section
        details_label = QLabel("Organization Details:")
        details_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 15px;")
        layout.addWidget(details_label)
        
        details_desc = QLabel("Fill in your organization's basic information. This helps the system find grants that match your mission and focus areas.")
        details_desc.setWordWrap(True)
        details_desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(details_desc)
        
        # Organization name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your organization's full name (e.g., 'Coda Mountain Academy')")
        self.name_input.setToolTip("The official name of your organization as it appears on legal documents")
        form_layout.addRow("Organization Name:", self.name_input)
        
        # Mission field
        self.mission_input = QTextEdit()
        self.mission_input.setMaximumHeight(100)
        self.mission_input.setPlaceholderText("Describe your organization's mission, goals, and the communities you serve. This helps match you with relevant grants.")
        self.mission_input.setToolTip("A clear description of what your organization does and who it serves")
        form_layout.addRow("Mission & Description:", self.mission_input)
        
        # Organization type field
        self.type_input = QComboBox()
        self.type_input.addItems(["Education", "Arts", "Robotics", "Housing", "Community", "Other"])
        self.type_input.setToolTip("Select the primary focus area of your organization to help find relevant grants")
        form_layout.addRow("Primary Focus Area:", self.type_input)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Buttons section
        buttons_label = QLabel("Save & Load:")
        buttons_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 15px;")
        layout.addWidget(buttons_label)
        
        buttons_desc = QLabel("Save your profile to reuse it later, or load a previously saved profile.")
        buttons_desc.setWordWrap(True)
        buttons_desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(buttons_desc)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.save_btn = icon_manager.create_button('save', 'Save Profile')
        self.save_btn.setToolTip("Save your current profile to reuse it later")
        self.save_btn.clicked.connect(self.save_profile)
        
        self.load_btn = icon_manager.create_button('load', 'Load Profile')
        self.load_btn.setToolTip("Load a previously saved profile from your computer")
        self.load_btn.clicked.connect(self.load_profile)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.load_btn)
        layout.addLayout(button_layout)
        
        # Status section
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        # Add some spacing at the bottom
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Load presets asynchronously
        QTimer.singleShot(100, self.load_available_presets)

    def load_available_presets(self):
        """Load all available preset organizations asynchronously."""
        try:
            self.loading_indicator.setVisible(True)
            self.preset_combo.clear()
            self.preset_combo.addItem("-- Select Preset Organization --")
            
            # Get all available presets
            presets = preset_manager.get_available_presets()
            
            # Add presets to combo box with descriptive text
            for preset in presets:
                if preset.name == "custom":
                    display_text = "Custom Organization"
                else:
                    display_text = f"{preset.display_name} ({preset.focus_area})"
                    if preset.location != "Not specified":
                        display_text += f" - {preset.location}"
                
                self.preset_combo.addItem(display_text, preset.name)
            
            self.loading_indicator.setVisible(False)
            self.status_label.setText("✅ Preset organizations loaded successfully!")
            
        except Exception as e:
            self.loading_indicator.setVisible(False)
            self.preset_combo.clear()
            self.preset_combo.addItem("-- Error Loading Presets --")
            self.status_label.setText(f"❌ Error loading presets: {str(e)}")

    def load_preset_profile(self, display_text: str):
        """Load a preset organization profile."""
        if not display_text or display_text.startswith("--"):
            return
        
        try:
            # Show loading state
            self.loading_indicator.setVisible(True)
            self.status_label.setText("🔄 Loading organization profile...")
            
            # Get the preset name from the combo box data
            current_index = self.preset_combo.currentIndex()
            if current_index < 0:
                return
            
            preset_name = self.preset_combo.itemData(current_index)
            if not preset_name:
                return
            
            # Load the profile data
            profile_data = preset_manager.load_preset_profile(preset_name)
            if not profile_data:
                self.status_label.setText("❌ Error: Could not load profile data")
                return
            
            # Fill the form fields
            self._fill_form_with_profile(profile_data)
            
            # Create and emit profile object
            profile = self.get_profile()
            if profile:
                self.profile_loaded.emit(profile)
                self.profile_changed.emit(profile)
            
            self.loading_indicator.setVisible(False)
            self.status_label.setText(f"✅ {profile_data.get('name', 'Organization')} profile loaded successfully!")
            
        except Exception as e:
            self.loading_indicator.setVisible(False)
            self.status_label.setText(f"❌ Error loading profile: {str(e)}")

    def _fill_form_with_profile(self, profile_data: dict):
        """Fill form fields with profile data."""
        # Basic fields
        self.name_input.setText(profile_data.get("name", ""))
        self.mission_input.setPlainText(profile_data.get("description", ""))
        
        # Handle focus areas mapping
        focus_areas = profile_data.get("focus_areas", [])
        if focus_areas:
            # Map focus areas to combo box options
            focus_mapping = {
                "education": "Education",
                "art_education": "Arts", 
                "music_education": "Arts",
                "robotics": "Robotics",
                "housing": "Housing",
                "affordable_housing": "Housing",
                "community": "Community",
                "community_development": "Community",
                "youth_development": "Education",
                "senior_services": "Community",
                "social_services": "Community"
            }
            
            # Try to find the first focus area that maps to a combo box option
            for focus in focus_areas:
                mapped_focus = focus_mapping.get(focus, focus.replace("_", " ").title())
                idx = self.type_input.findText(mapped_focus)
                if idx >= 0:
                    self.type_input.setCurrentIndex(idx)
                    break
            else:
                # If no mapping found, default to "Education"
                idx = self.type_input.findText("Education")
                if idx >= 0:
                    self.type_input.setCurrentIndex(idx)

    def clear_form(self):
        """Clear the form for custom organization."""
        self.name_input.clear()
        self.mission_input.clear()
        self.type_input.setCurrentIndex(0)
        self.status_label.setText("📝 Form cleared - ready for custom organization details")

    def get_profile(self):
        name = self.name_input.text().strip()
        if not name:
            return None
        return OrganizationProfile(
            name=name,
            description=self.mission_input.toPlainText(),
            focus_areas=[],  # Will be set based on type_input
            program_types=[],
            target_demographics=[],
            location="",
            contact_name="",
            contact_email="",
            contact_phone="",
            annual_budget=None,
            website=None,
            ein=None,
            founded_year=None,
            preferred_grant_size=(10000, 100000)
        )

    def save_profile(self):
        profile = self.get_profile()
        if not profile:
            self.status_label.setText("❌ Please fill in the organization name before saving")
            return
        try:
            with open(PROFILE_PATH, "w") as f:
                json.dump(profile.model_dump(), f, default=str)
            # Emit signal after saving
            self.profile_loaded.emit(profile)
            self.profile_changed.emit(profile)
            self.status_label.setText("✅ Profile saved successfully!")
        except Exception as e:
            self.status_label.setText(f"❌ Error saving profile: {str(e)}")

    def load_profile(self):
        """Load a previously saved profile."""
        try:
            if PROFILE_PATH.exists():
                with open(PROFILE_PATH, "r") as f:
                    data = json.load(f)
                
                # Fill form with loaded data
                self._fill_form_with_profile(data)
                
                # Create and emit profile object
                profile = self.get_profile()
                if profile:
                    self.profile_loaded.emit(profile)
                    self.profile_changed.emit(profile)
                
                self.status_label.setText("✅ Profile loaded successfully!")
            else:
                self.status_label.setText("❌ No saved profile found")
        except Exception as e:
            self.status_label.setText(f"❌ Error loading profile: {str(e)}")

    def load_questionnaire_profile(self, profile):
        """Load a profile created from the questionnaire."""
        try:
            # Fill in the form fields
            self.name_input.setText(profile.name or "")
            self.mission_input.setPlainText(profile.description or "")
            
            # Set focus area
            if profile.focus_areas:
                focus_text = str(profile.focus_areas[0]).replace('_', ' ').title()
                # Try to match with combo box items
                for i in range(self.type_input.count()):
                    if focus_text.lower() in self.type_input.itemText(i).lower():
                        self.type_input.setCurrentIndex(i)
                        break
            
            # Update status
            self.status_label.setText(
                f"✅ Profile '{profile.name}' loaded from questionnaire!"
            )
            
            # Store the profile
            self.current_profile = profile
            
            # Emit signal to update search tab
            self.profile_loaded.emit(profile)
            self.profile_changed.emit(profile)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error loading questionnaire profile: {str(e)}")


class ReportingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the reporting UI."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("📊 Grant Application Reports & Analytics")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Organization filter
        org_layout = QHBoxLayout()
        org_layout.addWidget(QLabel("Organization:"))
        self.org_combo = QComboBox()
        self.org_combo.addItems(["All Organizations", "CODA", "NRG_Development"])
        org_layout.addWidget(self.org_combo)
        org_layout.addStretch()
        layout.addLayout(org_layout)
        
        # Report generation buttons
        buttons_layout = QVBoxLayout()
        
        self.excel_btn = QPushButton("📊 Generate Excel Report")
        self.excel_btn.clicked.connect(self.generate_excel_report)
        buttons_layout.addWidget(self.excel_btn)
        
        self.html_btn = QPushButton("🌐 Generate HTML Report")
        self.html_btn.clicked.connect(self.generate_html_report)
        buttons_layout.addWidget(self.html_btn)
        
        self.pdf_btn = QPushButton("📄 Generate PDF Report")
        self.pdf_btn.clicked.connect(self.generate_pdf_report)
        buttons_layout.addWidget(self.pdf_btn)
        
        layout.addLayout(buttons_layout)
        
        # Status and metrics display
        self.status_label = QLabel("Ready to generate reports...")
        layout.addWidget(self.status_label)
        
        # Metrics display area
        self.metrics_text = QTextEdit()
        self.metrics_text.setMaximumHeight(200)
        self.metrics_text.setReadOnly(True)
        layout.addWidget(QLabel("Current Metrics:"))
        layout.addWidget(self.metrics_text)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Load initial metrics
        self.update_metrics()
    
    def get_selected_organization(self):
        """Get the selected organization or None for all."""
        selected = self.org_combo.currentText()
        return None if selected == "All Organizations" else selected
    
    def update_metrics(self):
        """Update the metrics display."""
        try:
            from grant_ai.services.report_generator import ReportGenerator
            
            generator = ReportGenerator()
            org_id = self.get_selected_organization()
            metrics = generator.calculate_metrics(org_id)
            
            metrics_text = f"""
📊 CURRENT METRICS {f"({org_id})" if org_id else "(All Organizations)"}

Total Applications: {metrics.total_applications}
Success Rate: {metrics.success_rate:.1f}%
Average Processing Time: {metrics.average_processing_time:.1f} days
Overdue Applications: {metrics.overdue_count}
Due Soon (7 days): {metrics.due_soon_count}
Total Funding Requested: ${metrics.funding_requested:,.2f}
Total Funding Awarded: ${metrics.funding_awarded:,.2f}

STATUS BREAKDOWN:
"""
            
            for status, count in metrics.by_status.items():
                status_display = status.replace('_', ' ').title()
                metrics_text += f"  • {status_display}: {count}\n"
            
            if len(metrics.by_organization) > 1 and not org_id:
                metrics_text += "\nORGANIZATION BREAKDOWN:\n"
                for org, count in metrics.by_organization.items():
                    metrics_text += f"  • {org}: {count}\n"
            
            self.metrics_text.setPlainText(metrics_text)
            
        except Exception as e:
            self.metrics_text.setPlainText(f"❌ Error loading metrics: {str(e)}")
    
    def generate_excel_report(self):
        """Generate Excel report."""
        try:
            from grant_ai.services.report_generator import ReportGenerator
            
            self.status_label.setText("📊 Generating Excel report...")
            self.excel_btn.setEnabled(False)
            
            generator = ReportGenerator()
            org_id = self.get_selected_organization()
            filepath = generator.generate_excel_report(org_id)
            
            self.status_label.setText(f"✅ Excel report saved: {filepath}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error generating Excel report: {str(e)}")
        finally:
            self.excel_btn.setEnabled(True)
    
    def generate_html_report(self):
        """Generate HTML report."""
        try:
            from grant_ai.services.report_generator import ReportGenerator
            
            self.status_label.setText("🌐 Generating HTML report...")
            self.html_btn.setEnabled(False)
            
            generator = ReportGenerator()
            org_id = self.get_selected_organization()
            filepath = generator.generate_html_report(org_id)
            
            self.status_label.setText(f"✅ HTML report saved: {filepath}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error generating HTML report: {str(e)}")
        finally:
            self.html_btn.setEnabled(True)
    
    def generate_pdf_report(self):
        """Generate PDF report."""
        try:
            from grant_ai.services.report_generator import ReportGenerator
            
            self.status_label.setText("📄 Generating PDF report...")
            self.pdf_btn.setEnabled(False)
            
            generator = ReportGenerator()
            org_id = self.get_selected_organization()
            filepath = generator.generate_pdf_report(org_id)
            
            self.status_label.setText(f"✅ PDF report saved: {filepath}")
            
        except ImportError:
            self.status_label.setText("❌ ReportLab not available for PDF generation")
        except Exception as e:
            self.status_label.setText(f"❌ Error generating PDF report: {str(e)}")
        finally:
            self.pdf_btn.setEnabled(True)
        

class PastGrantsTab(QWidget):
    """Tab for viewing and managing past grants and funding history."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_past_grants()
    
    def init_ui(self):
        """Initialize the user interface for past grants tracking."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("CODA Past Grants & Funding History")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Summary stats
        self.create_summary_section(layout)
        
        # Filter controls
        self.create_filter_section(layout)
        
        # Past grants table
        self.create_grants_table(layout)
        
        # Add new grant section
        self.create_add_grant_section(layout)
        
        self.setLayout(layout)
    
    def create_summary_section(self, layout):
        """Create summary statistics section."""
        summary_widget = QWidget()
        summary_layout = QHBoxLayout()
        
        # Total funding received
        self.total_funding_label = QLabel("Total Funding: $0")
        self.total_funding_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #27ae60;
                padding: 10px;
                background-color: #d5f4e6;
                border-radius: 5px;
                border: 2px solid #27ae60;
            }
        """)
        
        # Number of grants
        self.grants_count_label = QLabel("Total Grants: 0")
        self.grants_count_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498db;
                padding: 10px;
                background-color: #ebf3fd;
                border-radius: 5px;
                border: 2px solid #3498db;
            }
        """)
        
        # Average grant size
        self.avg_grant_label = QLabel("Average Grant: $0")
        self.avg_grant_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #f39c12;
                padding: 10px;
                background-color: #fef9e7;
                border-radius: 5px;
                border: 2px solid #f39c12;
            }
        """)
        
        summary_layout.addWidget(self.total_funding_label)
        summary_layout.addWidget(self.grants_count_label)
        summary_layout.addWidget(self.avg_grant_label)
        summary_layout.addStretch()
        
        summary_widget.setLayout(summary_layout)
        layout.addWidget(summary_widget)
    
    def create_filter_section(self, layout):
        """Create filter controls for grants."""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        # Year filter
        filter_layout.addWidget(QLabel("Filter by Year:"))
        self.year_filter = QComboBox()
        self.year_filter.addItem("All Years")
        # Add years from 2010 to current year
        from datetime import datetime
        current_year = datetime.now().year
        for year in range(current_year, 2009, -1):
            self.year_filter.addItem(str(year))
        self.year_filter.currentTextChanged.connect(self.filter_grants)
        filter_layout.addWidget(self.year_filter)
        
        # Funding type filter
        filter_layout.addWidget(QLabel("Funding Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "All Types", "Federal Grant", "State Grant", "Foundation Grant",
            "Corporate Sponsorship", "Private Donation", "Other"
        ])
        self.type_filter.currentTextChanged.connect(self.filter_grants)
        filter_layout.addWidget(self.type_filter)
        
        # Status filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Status", "Received", "In Progress", "Completed", "Pending"
        ])
        self.status_filter.currentTextChanged.connect(self.filter_grants)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_past_grants)
        filter_layout.addWidget(refresh_btn)
        
        filter_widget.setLayout(filter_layout)
        layout.addWidget(filter_widget)
    
    def create_grants_table(self, layout):
        """Create the past grants table."""
        
        self.grants_table = QTableWidget()
        self.grants_table.setColumnCount(7)
        self.grants_table.setHorizontalHeaderLabels([
            "Funder", "Amount", "Year", "Type", "Purpose", "Status", "Notes"
        ])
        
        # Set column widths
        header = self.grants_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Funder
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Amount
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Year
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Type
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Purpose
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Status
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Notes
        
        self.grants_table.setColumnWidth(1, 100)  # Amount
        self.grants_table.setColumnWidth(2, 70)   # Year
        self.grants_table.setColumnWidth(3, 120)  # Type
        self.grants_table.setColumnWidth(5, 90)   # Status
        
        # Enable sorting
        self.grants_table.setSortingEnabled(True)
        
        # Style the table
        self.grants_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.grants_table)
    
    def create_add_grant_section(self, layout):
        """Create section for adding new past grants."""
        add_widget = QWidget()
        add_layout = QVBoxLayout()
        
        # Add grant button
        add_btn = QPushButton("+ Add New Past Grant")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        add_btn.clicked.connect(self.add_new_grant)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addStretch()
        
        add_layout.addLayout(button_layout)
        add_widget.setLayout(add_layout)
        layout.addWidget(add_widget)
    
    def load_past_grants(self):
        """Load past grants data from database or storage."""
        # Sample data for demonstration - in production, this would come from a database
        self.past_grants_data = [
            {
                "funder": "West Virginia Department of Education",
                "amount": 25000,
                "year": 2024,
                "type": "State Grant",
                "purpose": "After-school STEM programs",
                "status": "Completed",
                "notes": "Successfully funded robotics equipment and training"
            },
            {
                "funder": "Appalachian Regional Commission",
                "amount": 50000,
                "year": 2023,
                "type": "Federal Grant",
                "purpose": "Rural arts education initiative",
                "status": "Completed",
                "notes": "Expanded music and art programs to 3 schools"
            },
            {
                "funder": "Claude Worthington Benedum Foundation",
                "amount": 15000,
                "year": 2023,
                "type": "Foundation Grant",
                "purpose": "Music education equipment",
                "status": "Completed",
                "notes": "Purchased new instruments for school band"
            },
            {
                "funder": "United Way of Central West Virginia",
                "amount": 8000,
                "year": 2022,
                "type": "Foundation Grant",
                "purpose": "Summer camp scholarships",
                "status": "Completed",
                "notes": "Provided scholarships for 40 low-income students"
            },
            {
                "funder": "WV Community Foundation",
                "amount": 12000,
                "year": 2022,
                "type": "Foundation Grant",
                "purpose": "Technology upgrade",
                "status": "Completed",
                "notes": "Upgraded computer lab with new equipment"
            },
            {
                "funder": "Local Business Coalition",
                "amount": 5000,
                "year": 2024,
                "type": "Corporate Sponsorship",
                "purpose": "Robotics competition team",
                "status": "In Progress",
                "notes": "Ongoing support for FIRST Robotics team"
            }
        ]
        
        self.populate_grants_table()
        self.update_summary_stats()
    
    def populate_grants_table(self):
        """Populate the grants table with filtered data."""
        # Filter data based on current filters
        filtered_data = self.filter_data()
        
        self.grants_table.setRowCount(len(filtered_data))
        
        for row, grant in enumerate(filtered_data):
            self.grants_table.setItem(row, 0, QTableWidgetItem(grant["funder"]))
            self.grants_table.setItem(row, 1, QTableWidgetItem(f"${grant['amount']:,}"))
            self.grants_table.setItem(row, 2, QTableWidgetItem(str(grant["year"])))
            self.grants_table.setItem(row, 3, QTableWidgetItem(grant["type"]))
            self.grants_table.setItem(row, 4, QTableWidgetItem(grant["purpose"]))
            self.grants_table.setItem(row, 5, QTableWidgetItem(grant["status"]))
            self.grants_table.setItem(row, 6, QTableWidgetItem(grant["notes"]))
            
            # Color code by status
            status_item = self.grants_table.item(row, 5)
            if grant["status"] == "Completed":
                status_item.setBackground(QColor("#d5f4e6"))
                status_item.setForeground(QColor("#27ae60"))
            elif grant["status"] == "In Progress":
                status_item.setBackground(QColor("#fff3cd"))
                status_item.setForeground(QColor("#856404"))
            elif grant["status"] == "Pending":
                status_item.setBackground(QColor("#f8d7da"))
                status_item.setForeground(QColor("#721c24"))
    
    def filter_data(self):
        """Filter grants data based on current filter settings."""
        filtered_data = self.past_grants_data.copy()
        
        # Year filter
        if self.year_filter.currentText() != "All Years":
            year = int(self.year_filter.currentText())
            filtered_data = [g for g in filtered_data if g["year"] == year]
        
        # Type filter
        if self.type_filter.currentText() != "All Types":
            grant_type = self.type_filter.currentText()
            filtered_data = [g for g in filtered_data if g["type"] == grant_type]
        
        # Status filter
        if self.status_filter.currentText() != "All Status":
            status = self.status_filter.currentText()
            filtered_data = [g for g in filtered_data if g["status"] == status]
        
        return filtered_data
    
    def filter_grants(self):
        """Apply filters and refresh the table."""
        self.populate_grants_table()
        self.update_summary_stats()
    
    def update_summary_stats(self):
        """Update the summary statistics."""
        filtered_data = self.filter_data()
        
        if filtered_data:
            total_funding = sum(grant["amount"] for grant in filtered_data)
            grants_count = len(filtered_data)
            avg_grant = total_funding / grants_count if grants_count > 0 else 0
            
            self.total_funding_label.setText(f"Total Funding: ${total_funding:,}")
            self.grants_count_label.setText(f"Total Grants: {grants_count}")
            self.avg_grant_label.setText(f"Average Grant: ${avg_grant:,.0f}")
        else:
            self.total_funding_label.setText("Total Funding: $0")
            self.grants_count_label.setText("Total Grants: 0")
            self.avg_grant_label.setText("Average Grant: $0")
    
    def add_new_grant(self):
        """Open dialog to add a new past grant."""
        self.show_add_grant_dialog()
    
    def show_add_grant_dialog(self):
        """Show dialog for adding a new past grant."""
        from PyQt5.QtWidgets import (
            QComboBox,
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QLineEdit,
            QSpinBox,
            QTextEdit,
        )
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Past Grant")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QFormLayout()
        
        # Form fields
        funder_edit = QLineEdit()
        amount_edit = QSpinBox()
        amount_edit.setRange(0, 10000000)
        amount_edit.setSuffix(" USD")
        
        year_edit = QSpinBox()
        year_edit.setRange(2000, 2030)
        year_edit.setValue(2024)
        
        type_combo = QComboBox()
        type_combo.addItems([
            "Federal Grant", "State Grant", "Foundation Grant",
            "Corporate Sponsorship", "Private Donation", "Other"
        ])
        
        purpose_edit = QLineEdit()
        
        status_combo = QComboBox()
        status_combo.addItems(["Received", "In Progress", "Completed", "Pending"])
        
        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(80)
        
        # Add fields to form
        layout.addRow("Funder:", funder_edit)
        layout.addRow("Amount ($):", amount_edit)
        layout.addRow("Year:", year_edit)
        layout.addRow("Type:", type_combo)
        layout.addRow("Purpose:", purpose_edit)
        layout.addRow("Status:", status_combo)
        layout.addRow("Notes:", notes_edit)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_new_grant(
            dialog, funder_edit.text(), amount_edit.value(),
            year_edit.value(), type_combo.currentText(),
            purpose_edit.text(), status_combo.currentText(),
            notes_edit.toPlainText()
        ))
        buttons.rejected.connect(dialog.reject)
        
        layout.addRow(buttons)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_new_grant(self, dialog, funder, amount, year, grant_type, purpose, status, notes):
        """Save the new grant to the data."""
        if not funder or not purpose:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Funder and Purpose are required fields.")
            return
        
        new_grant = {
            "funder": funder,
            "amount": amount,
            "year": year,
            "type": grant_type,
            "purpose": purpose,
            "status": status,
            "notes": notes
        }
        
        self.past_grants_data.append(new_grant)
        self.populate_grants_table()
        self.update_summary_stats()
        
        dialog.accept()
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", "New grant added successfully!")


class ApplicationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_applications()
        
    def setup_ui(self):
        """Set up the application tracking UI."""
        layout = QVBoxLayout()
        
        # Header with summary stats
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📊 Application Tracking Dashboard"))
        
        # Status filter dropdown
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Applications", "Draft", "In Progress", "Submitted",
            "Under Review", "Approved", "Rejected", "Awarded"
        ])
        self.status_filter.currentTextChanged.connect(self.filter_applications)
        header_layout.addWidget(QLabel("Filter by Status:"))
        header_layout.addWidget(self.status_filter)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_applications)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Summary stats
        self.stats_label = QLabel("Loading statistics...")
        layout.addWidget(self.stats_label)
        
        # Applications list
        self.applications_list = QListWidget()
        self.applications_list.itemDoubleClicked.connect(
            self.view_application_details
        )
        layout.addWidget(self.applications_list)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add New Application")
        self.add_btn.clicked.connect(self.add_new_application)
        self.view_btn = QPushButton("👁️ View Details")
        self.view_btn.clicked.connect(self.view_selected_application)
        self.update_status_btn = QPushButton("📝 Update Status")
        self.update_status_btn.clicked.connect(self.update_application_status)
        self.add_note_btn = QPushButton("📄 Add Note")
        self.add_note_btn.clicked.connect(self.add_application_note)
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.view_btn)
        buttons_layout.addWidget(self.update_status_btn)
        buttons_layout.addWidget(self.add_note_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def load_applications(self):
        """Load and display applications."""
        try:
            from grant_ai.utils.tracking_manager import TrackingManager
            
            self.tracking_manager = TrackingManager()
            self.all_applications = self.tracking_manager.list_tracking()
            
            # Update stats
            self.update_statistics()
            
            # Update list
            self.filter_applications()
            
        except Exception as e:
            self.stats_label.setText(f"❌ Error loading applications: {str(e)}")
            
    def update_statistics(self):
        """Update the statistics display."""
        if not hasattr(self, 'all_applications'):
            return
            
        total = len(self.all_applications)
        if total == 0:
            self.stats_label.setText(
                "📊 No applications found. Click 'Add New Application' "
                "to get started."
            )
            return
            
        # Count by status
        status_counts = {}
        overdue_count = 0
        due_soon_count = 0
        
        for app in self.all_applications:
            status = app.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if hasattr(app, 'is_overdue') and app.is_overdue():
                overdue_count += 1
                
            if hasattr(app, 'days_until_deadline'):
                days_until = app.days_until_deadline()
                if days_until is not None and 0 <= days_until <= 7:
                    due_soon_count += 1
        
        stats_text = f"📊 Total: {total} | "
        stats_text += f"⚠️ Overdue: {overdue_count} | "
        stats_text += f"⏰ Due Soon: {due_soon_count} | "
        
        # Show top statuses
        if status_counts:
            top_statuses = sorted(
                status_counts.items(), key=lambda x: x[1], reverse=True
            )[:3]
            status_summary = ", ".join([
                f"{status.title()}: {count}"
                for status, count in top_statuses
            ])
            stats_text += f"Status: {status_summary}"
            
        self.stats_label.setText(stats_text)
        
    def filter_applications(self):
        """Filter applications based on selected status."""
        if not hasattr(self, 'all_applications'):
            return
            
        self.applications_list.clear()
        
        selected_status = self.status_filter.currentText().lower()
        
        for app in self.all_applications:
            # Filter by status
            if selected_status != "all applications":
                app_status = app.current_status.value.replace("_", " ")
                if app_status != selected_status:
                    continue
            
            # Create display text
            status_emoji = self.get_status_emoji(app.current_status.value)
            
            # Get days until deadline
            deadline_text = ""
            if hasattr(app, 'days_until_deadline'):
                days_until = app.days_until_deadline()
                if days_until is not None:
                    if days_until < 0:
                        deadline_text = f" (⚠️ {abs(days_until)} days overdue)"
                    elif days_until <= 7:
                        deadline_text = f" (⏰ {days_until} days left)"
                    else:
                        deadline_text = f" ({days_until} days left)"
            
            display_text = (
                f"{status_emoji} {app.application_id} | "
                f"Org: {app.organization_id} | "
                f"Status: {app.current_status.value.replace('_', ' ').title()}"
                f"{deadline_text}"
            )
            
            self.applications_list.addItem(display_text)
            
    def get_status_emoji(self, status):
        """Get emoji for application status."""
        status_emojis = {
            "draft": "📝",
            "in_progress": "⚙️",
            "submitted": "📤",
            "under_review": "👀",
            "approved": "✅",
            "rejected": "❌",
            "awarded": "🏆",
            "declined": "❌",
            "withdrawn": "↩️"
        }
        return status_emojis.get(status, "📄")
        
    def view_application_details(self):
        """View details of double-clicked application."""
        self.view_selected_application()
        
    def view_selected_application(self):
        """View details of selected application."""
        current_item = self.applications_list.currentItem()
        if not current_item:
            return
            
        # Extract application ID from display text
        app_id = current_item.text().split(" | ")[0].split(" ", 1)[1]
        
        # Find the application
        app = None
        for application in self.all_applications:
            if application.application_id == app_id:
                app = application
                break
                
        if not app:
            return
            
        # Show details dialog
        self.show_application_details_dialog(app)
        
    def show_application_details_dialog(self, app):
        """Show detailed view of application."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Application Details - {app.application_id}")
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Basic info
        info_text = f"""
        <h3>Application Information</h3>
        <b>ID:</b> {app.application_id}<br>
        <b>Organization:</b> {app.organization_id}<br>
        <b>Grant ID:</b> {app.grant_id}<br>
        <b>Status:</b> {app.current_status.value.replace('_', ' ').title()}<br>
        <b>Created:</b> {app.created_at.strftime('%Y-%m-%d %H:%M')}<br>
        <b>Updated:</b> {app.updated_at.strftime('%Y-%m-%d %H:%M')}<br>
        """
        
        if app.assigned_to:
            info_text += f"<b>Assigned to:</b> {app.assigned_to}<br>"
            
        if hasattr(app, 'grant_deadline') and app.grant_deadline:
            info_text += f"<b>Deadline:</b> {app.grant_deadline.strftime('%Y-%m-%d')}<br>"
            
        if hasattr(app, 'funding_amount') and app.funding_amount:
            info_text += f"<b>Funding Amount:</b> ${app.funding_amount:,.2f}<br>"
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Events timeline
        if app.events:
            layout.addWidget(QLabel("<h4>Timeline</h4>"))
            events_list = QListWidget()
            for event in sorted(app.events, key=lambda x: x.created_at, reverse=True):
                event_text = f"{event.created_at.strftime('%Y-%m-%d %H:%M')} - {event.event_type}: {event.description}"
                events_list.addItem(event_text)
            events_list.setMaximumHeight(150)
            layout.addWidget(events_list)
        
        # Notes
        if app.notes:
            layout.addWidget(QLabel("<h4>Notes</h4>"))
            notes_list = QListWidget()
            for note in sorted(app.notes, key=lambda x: x.created_at, reverse=True):
                note_text = f"{note.created_at.strftime('%Y-%m-%d')} - {note.title}: {note.content[:100]}..."
                notes_list.addItem(note_text)
            notes_list.setMaximumHeight(100)
            layout.addWidget(notes_list)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def add_new_application(self):
        """Add a new application."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Application")
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        # Form fields
        app_id_input = QLineEdit()
        app_id_input.setPlaceholderText("e.g., APP_001")
        
        org_id_input = QLineEdit()
        org_id_input.setPlaceholderText("e.g., CODA")
        
        grant_id_input = QLineEdit()
        grant_id_input.setPlaceholderText("Optional")
        
        assigned_to_input = QLineEdit()
        assigned_to_input.setPlaceholderText("Optional")
        
        layout.addRow("Application ID:", app_id_input)
        layout.addRow("Organization ID:", org_id_input)
        layout.addRow("Grant ID:", grant_id_input)
        layout.addRow("Assigned To:", assigned_to_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        
        def create_application():
            app_id = app_id_input.text().strip()
            org_id = org_id_input.text().strip()
            
            if not app_id or not org_id:
                return
                
            try:
                tracking = self.tracking_manager.create_tracking(
                    application_id=app_id,
                    organization_id=org_id,
                    grant_id=grant_id_input.text().strip(),
                    assigned_to=assigned_to_input.text().strip()
                )
                
                self.tracking_manager.save_tracking(tracking)
                self.load_applications()
                dialog.close()
                
            except Exception as e:
                print(f"Error creating application: {e}")
        
        create_btn.clicked.connect(create_application)
        cancel_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def update_application_status(self):
        """Update status of selected application."""
        current_item = self.applications_list.currentItem()
        if not current_item:
            return
            
        # Extract application ID
        app_id = current_item.text().split(" | ")[0].split(" ", 1)[1]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Update Status - {app_id}")
        dialog.resize(400, 200)
        
        layout = QFormLayout()
        
        # Status dropdown
        status_combo = QComboBox()
        status_combo.addItems([
            "draft", "in_progress", "submitted", "under_review", 
            "approved", "rejected", "awarded", "declined", "withdrawn"
        ])
        
        description_input = QLineEdit()
        description_input.setPlaceholderText("Optional description")
        
        layout.addRow("New Status:", status_combo)
        layout.addRow("Description:", description_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        update_btn = QPushButton("Update")
        cancel_btn = QPushButton("Cancel")
        
        def update_status():
            from grant_ai.models.application_tracking import ApplicationStatus
            
            new_status = ApplicationStatus(status_combo.currentText())
            description = description_input.text().strip()
            
            try:
                success = self.tracking_manager.update_status(
                    application_id=app_id,
                    new_status=new_status,
                    description=description,
                    created_by="User"
                )
                
                if success:
                    self.load_applications()
                    dialog.close()
                else:
                    print("Failed to update status")
                    
            except Exception as e:
                print(f"Error updating status: {e}")
        
        update_btn.clicked.connect(update_status)
        cancel_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(update_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def add_application_note(self):
        """Add a note to selected application."""
        current_item = self.applications_list.currentItem()
        if not current_item:
            return
            
        # Extract application ID
        app_id = current_item.text().split(" | ")[0].split(" ", 1)[1]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Note - {app_id}")
        dialog.resize(400, 300)
        
        layout = QFormLayout()
        
        title_input = QLineEdit()
        title_input.setPlaceholderText("Note title")
        
        content_input = QTextEdit()
        content_input.setPlaceholderText("Note content...")
        
        internal_checkbox = QWidget()  # Placeholder for checkbox
        
        layout.addRow("Title:", title_input)
        layout.addRow("Content:", content_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Add Note")
        cancel_btn = QPushButton("Cancel")
        
        def add_note():
            title = title_input.text().strip()
            content = content_input.toPlainText().strip()
            
            if not title or not content:
                return
                
            try:
                success = self.tracking_manager.add_note(
                    application_id=app_id,
                    title=title,
                    content=content,
                    created_by="User",
                    is_internal=True
                )
                
                if success:
                    self.load_applications()
                    dialog.close()
                else:
                    print("Failed to add note")
                    
            except Exception as e:
                print(f"Error adding note: {e}")
        
        add_btn.clicked.connect(add_note)
        cancel_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grant Research AI - PyQt GUI")
        self.resize(800, 600)
        tabs = QTabWidget()
        
        # Create tabs
        self.org_profile_tab = OrgProfileTab()
        self.grant_search_tab = GrantSearchTab(self.org_profile_tab)
        self.questionnaire_tab = QuestionnaireWidget()
        self.reporting_tab = ReportingTab()
        self.past_grants_tab = PastGrantsTab()
        self.predictive_grants_tab = PredictiveGrantsTab()
        self.enhanced_past_grants_tab = EnhancedPastGrantsTab()
        
        # Connect questionnaire to profile tab
        self.questionnaire_tab.profileCreated.connect(
            self.org_profile_tab.load_questionnaire_profile
        )
        
        # Connect organization profile changes to new tabs
        self.org_profile_tab.profile_changed.connect(
            self.predictive_grants_tab.update_organization_context
        )
        self.org_profile_tab.profile_changed.connect(
            self.enhanced_past_grants_tab.update_organization_context
        )
        
        # Add tabs
        tabs.addTab(self.grant_search_tab, "Grant Search")
        tabs.addTab(self.org_profile_tab, "Organization Profile")
        tabs.addTab(self.questionnaire_tab, "Profile Questionnaire")
        tabs.addTab(ApplicationTab(), "Applications")
        tabs.addTab(self.past_grants_tab, "Past Grants")
        tabs.addTab(self.enhanced_past_grants_tab, "Enhanced Past Grants")
        tabs.addTab(self.predictive_grants_tab, "Predictive Grants")
        tabs.addTab(self.reporting_tab, "Reports")
        
        self.setCentralWidget(tabs)


def main():
    """Main function to launch the GUI application."""
    try:
        # Suppress Qt warnings by redirecting stderr temporarily
        import contextlib
        import io

        # Create application with suppressed warnings
        with contextlib.redirect_stderr(io.StringIO()):
            app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Grant Research AI")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Grant AI Project")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        print("GUI launched successfully! You can now:")
        print("1. Go to 'Organization Profile' tab")
        print("2. Select 'Coda Mountain Academy' from the dropdown")
        print("3. The profile should load without any crashes")
        
        # Start grant database update in background (non-blocking)
        def update_database_background():
            try:
                from grant_ai.utils.grant_database_manager import update_grant_database
                print("🔄 Checking for grant database updates...")
                update_grant_database(force_update=False)  # Only update if needed
            except Exception as e:
                print(f"⚠️  Grant database update failed: {e}")
        
        # Run database update in background thread
        import threading
        update_thread = threading.Thread(target=update_database_background, daemon=True)
        update_thread.start()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error launching GUI: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
