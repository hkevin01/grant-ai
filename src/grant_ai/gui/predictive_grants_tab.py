"""
Predictive Grants Tab for the Grant Research AI GUI.
Shows annually recurring grants that haven't been posted yet but are expected.
"""

from datetime import date
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from grant_ai.models.predictive_grant import (
    PredictiveGrant,
    PredictiveGrantDatabase,
    PredictiveStatus,
    create_sample_predictive_grants,
)


class PredictiveGrantsTab(QWidget):
    """Tab for managing and viewing predictive grant opportunities."""
    
    grant_selected = pyqtSignal(object)  # Emits selected PredictiveGrant
    
    def __init__(self):
        """Initialize the Predictive Grants tab."""
        super().__init__()
        
        # Data
        self.predictive_db = PredictiveGrantDatabase()
        self.current_grants = []
        self.selected_grant = None
        self.current_organization = None  # Track current organization context
        
        # Setup UI
        self.setup_ui()
        self.load_sample_data()
        self.populate_grants_table()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Grants table and filters
        left_widget = self.create_grants_section()
        splitter.addWidget(left_widget)
        
        # Right side - Grant details
        right_widget = self.create_details_section()
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
    def create_header(self) -> QHBoxLayout:
        """Create the header section with title and controls."""
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("🔮 Predictive Grants")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Annually recurring grants expected to open soon")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Predictions")
        refresh_btn.clicked.connect(self.refresh_predictions)
        layout.addWidget(refresh_btn)
        
        return layout
        
    def create_grants_section(self) -> QWidget:
        """Create the grants table section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All", "Expected", "Overdue", "Early", "Posted"
        ])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.status_filter)
        
        # Focus area filter
        filters_layout.addWidget(QLabel("Focus Area:"))
        self.focus_filter = QComboBox()
        self.focus_filter.addItems([
            "All", "Education", "Arts", "Housing", "Seniors", 
            "Technology", "Community"
        ])
        self.focus_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.focus_filter)
        
        # Confidence threshold
        filters_layout.addWidget(QLabel("Min Confidence:"))
        self.confidence_filter = QComboBox()
        self.confidence_filter.addItems([
            "0%", "25%", "50%", "75%", "90%"
        ])
        self.confidence_filter.setCurrentText("50%")
        self.confidence_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.confidence_filter)
        
        filters_layout.addStretch()
        layout.addWidget(filters_group)
        
        # Summary stats
        self.stats_widget = self.create_stats_widget()
        layout.addWidget(self.stats_widget)
        
        # Grants table
        self.grants_table = self.create_grants_table()
        layout.addWidget(self.grants_table)
        
        return widget
        
    def create_stats_widget(self) -> QWidget:
        """Create the statistics widget."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }"
        )
        
        layout = QHBoxLayout(widget)
        
        # Stats labels
        self.total_grants_label = QLabel("Total: 0")
        self.expected_grants_label = QLabel("Expected: 0")
        self.overdue_grants_label = QLabel("Overdue: 0")
        self.avg_confidence_label = QLabel("Avg Confidence: 0%")
        
        layout.addWidget(self.total_grants_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.expected_grants_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.overdue_grants_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.avg_confidence_label)
        layout.addStretch()
        
        return widget
        
    def create_grants_table(self) -> QTableWidget:
        """Create the predictive grants table."""
        table = QTableWidget()
        
        # Set up columns
        headers = [
            "Grant Title",
            "Agency", 
            "Status",
            "Predicted Post Date",
            "Days Until Post",
            "Predicted Amount",
            "Confidence",
            "Match Score",
            "Focus Areas"
        ]
        
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Configure table
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Grant Title
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Agency
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Post Date
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Days Until
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Confidence
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Match Score
        header.setSectionResizeMode(8, QHeaderView.Stretch)  # Focus Areas
        
        # Connect selection
        table.itemSelectionChanged.connect(self.on_grant_selected)
        
        return table
        
    def create_details_section(self) -> QWidget:
        """Create the grant details section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Details header
        details_label = QLabel("📋 Grant Details")
        details_font = QFont()
        details_font.setPointSize(14)
        details_font.setBold(True)
        details_label.setFont(details_font)
        layout.addWidget(details_label)
        
        # Scrollable details area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        scroll_area.setWidget(self.details_widget)
        
        layout.addWidget(scroll_area)
        
        # Initially show placeholder
        self.show_no_selection()
        
        return widget
        
    def load_sample_data(self):
        """Load sample predictive grants data."""
        sample_grants = create_sample_predictive_grants()
        
        for grant in sample_grants:
            self.predictive_db.add_grant(grant)
        
        # Update all statuses
        self.predictive_db.update_all_statuses()
        
        # Set current grants to all grants initially
        self.current_grants = self.predictive_db.grants.copy()
        
    def populate_grants_table(self):
        """Populate the grants table with current grants."""
        self.grants_table.setRowCount(len(self.current_grants))
        
        for row, grant in enumerate(self.current_grants):
            # Grant Title
            title_item = QTableWidgetItem(grant.title)
            title_item.setData(Qt.UserRole, grant)
            self.grants_table.setItem(row, 0, title_item)
            
            # Agency
            agency_item = QTableWidgetItem(grant.agency)
            self.grants_table.setItem(row, 1, agency_item)
            
            # Status with color coding
            status_item = QTableWidgetItem(grant.status.value)
            if grant.status == PredictiveStatus.EXPECTED:
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            elif grant.status == PredictiveStatus.OVERDUE:
                status_item.setBackground(QColor(255, 182, 193))  # Light red
            elif grant.status == PredictiveStatus.EARLY:
                status_item.setBackground(QColor(173, 216, 230))  # Light blue
            self.grants_table.setItem(row, 2, status_item)
            
            # Predicted Post Date
            post_date_item = QTableWidgetItem(
                grant.predicted_post_date.strftime("%m/%d/%Y")
            )
            self.grants_table.setItem(row, 3, post_date_item)
            
            # Days Until Post
            days_until = grant.days_until_predicted_posting()
            days_item = QTableWidgetItem(str(days_until))
            if days_until < 0:
                days_item.setBackground(QColor(255, 182, 193))  # Light red for overdue
            elif days_until <= 30:
                days_item.setBackground(QColor(255, 255, 224))  # Light yellow for soon
            self.grants_table.setItem(row, 4, days_item)
            
            # Predicted Amount
            if grant.predicted_amount_min and grant.predicted_amount_max:
                amount_text = f"${grant.predicted_amount_min:,} - ${grant.predicted_amount_max:,}"
            elif grant.predicted_amount_max:
                amount_text = f"Up to ${grant.predicted_amount_max:,}"
            else:
                amount_text = "Not specified"
            amount_item = QTableWidgetItem(amount_text)
            self.grants_table.setItem(row, 5, amount_item)
            
            # Confidence Score
            confidence_item = QTableWidgetItem(f"{grant.confidence_score:.0%}")
            if grant.confidence_score >= 0.8:
                confidence_item.setBackground(QColor(144, 238, 144))  # High confidence
            elif grant.confidence_score >= 0.5:
                confidence_item.setBackground(QColor(255, 255, 224))  # Medium confidence
            else:
                confidence_item.setBackground(QColor(255, 182, 193))  # Low confidence
            self.grants_table.setItem(row, 6, confidence_item)
            
            # Match Score
            match_item = QTableWidgetItem(f"{grant.organization_match_score:.0%}")
            self.grants_table.setItem(row, 7, match_item)
            
            # Focus Areas
            focus_areas_text = ", ".join(grant.focus_areas[:3])
            if len(grant.focus_areas) > 3:
                focus_areas_text += f" (+{len(grant.focus_areas) - 3})"
            focus_item = QTableWidgetItem(focus_areas_text)
            self.grants_table.setItem(row, 8, focus_item)
        
        # Update statistics
        self.update_statistics()
        
    def update_statistics(self):
        """Update the statistics display."""
        total = len(self.current_grants)
        expected = len([g for g in self.current_grants 
                       if g.status == PredictiveStatus.EXPECTED])
        overdue = len([g for g in self.current_grants 
                      if g.status == PredictiveStatus.OVERDUE])
        
        avg_confidence = 0
        if self.current_grants:
            avg_confidence = sum(g.confidence_score for g in self.current_grants) / len(self.current_grants)
        
        self.total_grants_label.setText(f"Total: {total}")
        self.expected_grants_label.setText(f"Expected: {expected}")
        self.overdue_grants_label.setText(f"Overdue: {overdue}")
        self.avg_confidence_label.setText(f"Avg Confidence: {avg_confidence:.0%}")
        
    def apply_filters(self):
        """Apply the current filters to the grants list."""
        filtered_grants = self.predictive_db.grants.copy()
        
        # Status filter
        status_filter = self.status_filter.currentText()
        if status_filter != "All":
            status_map = {
                "Expected": PredictiveStatus.EXPECTED,
                "Overdue": PredictiveStatus.OVERDUE,
                "Early": PredictiveStatus.EARLY,
                "Posted": PredictiveStatus.POSTED
            }
            if status_filter in status_map:
                filtered_grants = [g for g in filtered_grants 
                                 if g.status == status_map[status_filter]]
        
        # Focus area filter
        focus_filter = self.focus_filter.currentText().lower()
        if focus_filter != "all":
            filtered_grants = [g for g in filtered_grants 
                             if any(focus_filter in area.lower() 
                                   for area in g.focus_areas)]
        
        # Confidence filter
        confidence_text = self.confidence_filter.currentText()
        min_confidence = int(confidence_text.replace('%', '')) / 100
        filtered_grants = [g for g in filtered_grants 
                          if g.confidence_score >= min_confidence]
        
        self.current_grants = filtered_grants
        self.populate_grants_table()
        
    def on_grant_selected(self):
        """Handle grant selection in the table."""
        selected_items = self.grants_table.selectedItems()
        if not selected_items:
            self.show_no_selection()
            return
        
        # Get the grant from the first column's UserRole data
        row = selected_items[0].row()
        title_item = self.grants_table.item(row, 0)
        grant = title_item.data(Qt.UserRole)
        
        if grant:
            self.selected_grant = grant
            self.show_grant_details(grant)
            self.grant_selected.emit(grant)
        
    def show_grant_details(self, grant: PredictiveGrant):
        """Show detailed information for the selected grant."""
        # Clear existing details
        for i in reversed(range(self.details_layout.count())):
            child = self.details_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Title and agency
        title_label = QLabel(grant.title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        self.details_layout.addWidget(title_label)
        
        agency_label = QLabel(f"Agency: {grant.agency}")
        agency_font = QFont()
        agency_font.setItalic(True)
        agency_label.setFont(agency_font)
        self.details_layout.addWidget(agency_label)
        
        # Prediction information
        pred_group = QGroupBox("📊 Prediction Information")
        pred_layout = QVBoxLayout(pred_group)
        
        pred_layout.addWidget(QLabel(f"Status: {grant.status.value}"))
        pred_layout.addWidget(QLabel(
            f"Predicted Post Date: {grant.predicted_post_date.strftime('%B %d, %Y')}"
        ))
        pred_layout.addWidget(QLabel(
            f"Days Until Posting: {grant.days_until_predicted_posting()}"
        ))
        pred_layout.addWidget(QLabel(
            f"Predicted Deadline: {grant.predicted_deadline.strftime('%B %d, %Y')}"
        ))
        pred_layout.addWidget(QLabel(f"Confidence Score: {grant.confidence_score:.0%}"))
        pred_layout.addWidget(QLabel(f"Years Tracked: {grant.years_tracked}"))
        
        self.details_layout.addWidget(pred_group)
        
        # Grant details
        details_group = QGroupBox("📋 Grant Details")
        details_layout = QVBoxLayout(details_group)
        
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("", weight=QFont.Bold))
        details_layout.addWidget(desc_label)
        
        desc_text = QTextEdit()
        desc_text.setPlainText(grant.description)
        desc_text.setMaximumHeight(100)
        desc_text.setReadOnly(True)
        details_layout.addWidget(desc_text)
        
        details_layout.addWidget(QLabel(f"Focus Areas: {', '.join(grant.focus_areas)}"))
        
        if grant.predicted_amount_min or grant.predicted_amount_max:
            if grant.predicted_amount_min and grant.predicted_amount_max:
                amount_text = f"${grant.predicted_amount_min:,} - ${grant.predicted_amount_max:,}"
            elif grant.predicted_amount_max:
                amount_text = f"Up to ${grant.predicted_amount_max:,}"
            else:
                amount_text = f"From ${grant.predicted_amount_min:,}"
            details_layout.addWidget(QLabel(f"Predicted Amount Range: {amount_text}"))
        
        if grant.typical_award_count:
            details_layout.addWidget(QLabel(f"Typical Awards Made: {grant.typical_award_count}"))
        
        self.details_layout.addWidget(details_group)
        
        # Historical data
        if grant.historical_data:
            history_group = QGroupBox("📈 Historical Data")
            history_layout = QVBoxLayout(history_group)
            
            for data in grant.historical_data[-3:]:  # Show last 3 years
                history_text = f"{data.year}: Posted {data.posted_date.strftime('%m/%d')}, "
                history_text += f"Deadline {data.deadline_date.strftime('%m/%d')}"
                if data.amount_min and data.amount_max:
                    history_text += f", ${data.amount_min:,}-${data.amount_max:,}"
                if data.notes:
                    history_text += f" - {data.notes}"
                
                history_layout.addWidget(QLabel(history_text))
            
            self.details_layout.addWidget(history_group)
        
        # Eligibility
        if grant.eligibility_criteria:
            eligibility_group = QGroupBox("✅ Eligibility Criteria")
            eligibility_layout = QVBoxLayout(eligibility_group)
            
            for criterion in grant.eligibility_criteria:
                eligibility_layout.addWidget(QLabel(f"• {criterion}"))
            
            self.details_layout.addWidget(eligibility_group)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        track_btn = QPushButton("📌 Track This Grant")
        track_btn.clicked.connect(lambda: self.track_grant(grant))
        actions_layout.addWidget(track_btn)
        
        similar_btn = QPushButton("🔍 Find Similar Grants")
        similar_btn.clicked.connect(lambda: self.find_similar_grants(grant))
        actions_layout.addWidget(similar_btn)
        
        self.details_layout.addLayout(actions_layout)
        
        self.details_layout.addStretch()
        
    def show_no_selection(self):
        """Show placeholder when no grant is selected."""
        # Clear existing details
        for i in reversed(range(self.details_layout.count())):
            child = self.details_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Placeholder message
        placeholder = QLabel("Select a predictive grant from the table to view details")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        self.details_layout.addWidget(placeholder)
        
        self.details_layout.addStretch()
        
    def refresh_predictions(self):
        """Refresh prediction data and update display."""
        # Update all grant statuses
        self.predictive_db.update_all_statuses()
        
        # Reapply filters and refresh display
        self.apply_filters()
        
        print("🔄 Predictions refreshed")
        
    def track_grant(self, grant: PredictiveGrant):
        """Add grant to tracking/watchlist."""
        print(f"📌 Tracking grant: {grant.title}")
        # TODO: Implement tracking functionality
        
    def find_similar_grants(self, grant: PredictiveGrant):
        """Find similar grants based on focus areas."""
        print(f"🔍 Finding grants similar to: {grant.title}")
        # TODO: Implement similar grant finding
        
    def update_organization_context(self, organization_profile):
        """Update the tab with organization context for filtering."""
        if organization_profile:
            self.current_organization = organization_profile
            # Apply organization-specific filtering
            self.apply_organization_filter()
            print(f"🏢 Updated predictive grants context for: {organization_profile.name}")
        else:
            self.current_organization = None
            # Show all grants
            self.populate_grants_table()
            
    def apply_organization_filter(self):
        """Filter grants based on current organization profile."""
        if not hasattr(self, 'current_organization') or not self.current_organization:
            return
            
        # Get organization focus areas for filtering
        org_focus_areas = getattr(self.current_organization, 'focus_areas', [])
        org_name = getattr(self.current_organization, 'name', '')
        
        # Filter grants based on organization relevance
        relevant_grants = []
        for grant in self.predictive_db.get_all_grants():
            # Check if grant matches organization focus areas
            grant_relevance = any(
                focus_area.lower() in ' '.join(grant.focus_areas).lower()
                for focus_area in org_focus_areas
            ) if org_focus_areas else True
            
            # Check if organization matches target demographics
            org_relevance = (
                'nonprofit' in grant.eligibility_criteria.lower() or
                'education' in grant.eligibility_criteria.lower() or
                any(area.lower() in grant.eligibility_criteria.lower() 
                    for area in org_focus_areas)
            ) if org_focus_areas else True
            
            if grant_relevance or org_relevance:
                relevant_grants.append(grant)
        
        # Update display with filtered grants
        self.current_grants = relevant_grants
        self.populate_grants_table()
        
        print(f"📊 Filtered to {len(relevant_grants)} grants relevant to {org_name}")
