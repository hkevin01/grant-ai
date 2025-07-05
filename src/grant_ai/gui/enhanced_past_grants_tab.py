"""
Enhanced Past Grants Tab with detailed views and document management.
Supports viewing detailed grant information and opening submission documents.
"""

import os
import platform
import subprocess
from datetime import date, datetime
from typing import List, Optional

from PyQt5.QtCore import QDate, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QDesktopServices, QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from grant_ai.gui.icon_manager import icon_manager
from grant_ai.models.enhanced_past_grant import (
    BudgetItem,
    DocumentType,
    EnhancedPastGrant,
    GrantDocument,
    GrantMilestone,
    create_enhanced_sample_past_grants,
)


class DocumentViewerDialog(QDialog):
    """Dialog for viewing document details and opening files."""
    
    def __init__(self, document: GrantDocument, parent=None):
        super().__init__(parent)
        self.document = document
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the document viewer UI."""
        self.setWindowTitle(f"Document: {self.document.name}")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Document information
        info_group = QGroupBox("Document Information")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Name:", QLabel(self.document.name))
        info_layout.addRow("Type:", QLabel(self.document.document_type.value))
        info_layout.addRow("Upload Date:", 
                          QLabel(self.document.upload_date.strftime("%B %d, %Y")))
        
        if self.document.file_size:
            info_layout.addRow("File Size:", 
                              QLabel(self.document.get_size_formatted()))
        
        if self.document.description:
            desc_label = QLabel(self.document.description)
            desc_label.setWordWrap(True)
            info_layout.addRow("Description:", desc_label)
        
        # File path/URL information
        if self.document.file_path:
            path_label = QLabel(self.document.file_path)
            path_label.setWordWrap(True)
            path_label.setStyleSheet("font-family: monospace; color: #666;")
            info_layout.addRow("File Path:", path_label)
            
            # Check if file exists
            exists_label = QLabel("✅ File exists" if self.document.exists() 
                                 else "❌ File not found")
            exists_label.setStyleSheet(
                "color: green;" if self.document.exists() else "color: red;"
            )
            info_layout.addRow("Status:", exists_label)
        
        if self.document.url:
            url_label = QLabel(f'<a href="{self.document.url}">{self.document.url}</a>')
            url_label.setOpenExternalLinks(True)
            info_layout.addRow("URL:", url_label)
        
        layout.addWidget(info_group)
        
        # Preview area (for text documents)
        if self.document.file_path and self.document.exists():
            if self.document.file_path.lower().endswith(('.txt', '.md', '.log')):
                preview_group = QGroupBox("Preview")
                preview_layout = QVBoxLayout(preview_group)
                
                preview_text = QTextBrowser()
                try:
                    with open(self.document.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:2000]  # First 2000 characters
                        if len(content) == 2000:
                            content += "\n\n[Preview truncated...]"
                        preview_text.setPlainText(content)
                except Exception as e:
                    preview_text.setPlainText(f"Error reading file: {e}")
                
                preview_layout.addWidget(preview_text)
                layout.addWidget(preview_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        if self.document.file_path and self.document.exists():
            open_btn = QPushButton("📂 Open File")
            open_btn.clicked.connect(self.open_file)
            button_layout.addWidget(open_btn)
            
            open_folder_btn = QPushButton("📁 Open Folder")
            open_folder_btn.clicked.connect(self.open_folder)
            button_layout.addWidget(open_folder_btn)
        
        if self.document.url:
            open_url_btn = QPushButton("🌐 Open URL")
            open_url_btn.clicked.connect(self.open_url)
            button_layout.addWidget(open_url_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def open_file(self):
        """Open the document file with the default application."""
        if not self.document.file_path or not self.document.exists():
            QMessageBox.warning(self, "Error", "File not found!")
            return
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.document.file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.document.file_path)
            else:  # Linux
                subprocess.call(['xdg-open', self.document.file_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")
    
    def open_folder(self):
        """Open the folder containing the document."""
        if not self.document.file_path:
            return
        
        folder_path = os.path.dirname(self.document.file_path)
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', folder_path])
            elif platform.system() == 'Windows':  # Windows
                subprocess.call(['explorer', folder_path])
            else:  # Linux
                subprocess.call(['xdg-open', folder_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {e}")
    
    def open_url(self):
        """Open the document URL in the default browser."""
        if self.document.url:
            QDesktopServices.openUrl(QUrl(self.document.url))


class GrantDetailDialog(QDialog):
    """Dialog for viewing comprehensive grant details."""
    
    def __init__(self, grant: EnhancedPastGrant, parent=None):
        super().__init__(parent)
        self.grant = grant
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the grant detail dialog UI."""
        self.setWindowTitle(f"Grant Details: {self.grant.title}")
        self.setModal(True)
        
        # Set window flags to ensure the dialog is moveable
        window_flags = (Qt.Dialog | Qt.WindowTitleHint |
                        Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(window_flags)
        
        # Set minimum and initial size
        self.setMinimumSize(600, 400)
        self.resize(800, 600)
        
        # Center the dialog on the parent or screen
        self.center_on_parent()
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for different aspects
        tab_widget = QTabWidget()
        
        # Overview tab
        overview_tab = self.create_overview_tab()
        tab_widget.addTab(overview_tab, "📋 Overview")
        
        # Financial tab
        financial_tab = self.create_financial_tab()
        tab_widget.addTab(financial_tab, "💰 Financial")
        
        # Milestones tab
        milestones_tab = self.create_milestones_tab()
        tab_widget.addTab(milestones_tab, "🎯 Milestones")
        
        # Documents tab
        documents_tab = self.create_documents_tab()
        tab_widget.addTab(documents_tab, "📄 Documents")
        
        # Impact tab
        impact_tab = self.create_impact_tab()
        tab_widget.addTab(impact_tab, "📈 Impact")
        
        layout.addWidget(tab_widget)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
        
    def center_on_parent(self):
        """Center the dialog on its parent or screen."""
        if self.parent():
            # Center on parent widget
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            # Calculate position to center this dialog
            dialog_size = self.size()
            new_x = parent_center.x() - dialog_size.width() // 2
            new_y = parent_center.y() - dialog_size.height() // 2
            
            # Ensure the dialog stays within screen bounds
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            
            new_x = max(screen_geometry.left(), 
                       min(new_x, screen_geometry.right() - dialog_size.width()))
            new_y = max(screen_geometry.top(), 
                       min(new_y, screen_geometry.bottom() - dialog_size.height()))
            
            self.move(new_x, new_y)
        else:
            # Center on screen
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            screen_center = screen_geometry.center()
            
            dialog_size = self.size()
            new_x = screen_center.x() - dialog_size.width() // 2
            new_y = screen_center.y() - dialog_size.height() // 2
            
            self.move(new_x, new_y)
        
    def create_overview_tab(self) -> QWidget:
        """Create the overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Basic information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        basic_layout.addRow("Title:", QLabel(self.grant.title))
        basic_layout.addRow("Funder:", QLabel(self.grant.funder))
        basic_layout.addRow("Amount:", QLabel(f"${self.grant.amount:,.2f}"))
        basic_layout.addRow("Year:", QLabel(str(self.grant.year)))
        basic_layout.addRow("Type:", QLabel(self.grant.type))
        basic_layout.addRow("Status:", QLabel(self.grant.status))
        
        if self.grant.grant_number:
            basic_layout.addRow("Grant Number:", QLabel(self.grant.grant_number))
        
        if self.grant.program_name:
            basic_layout.addRow("Program:", QLabel(self.grant.program_name))
        
        layout.addWidget(basic_group)
        
        # Project details
        project_group = QGroupBox("Project Details")
        project_layout = QVBoxLayout(project_group)
        
        purpose_label = QLabel("Purpose:")
        purpose_label.setFont(QFont("", weight=QFont.Bold))
        project_layout.addWidget(purpose_label)
        
        purpose_text = QTextEdit()
        purpose_text.setPlainText(self.grant.purpose)
        purpose_text.setMaximumHeight(80)
        purpose_text.setReadOnly(True)
        project_layout.addWidget(purpose_text)
        
        if self.grant.project_period_start and self.grant.project_period_end:
            period_label = QLabel(
                f"Project Period: {self.grant.project_period_start.strftime('%m/%d/%Y')} - "
                f"{self.grant.project_period_end.strftime('%m/%d/%Y')}"
            )
            project_layout.addWidget(period_label)
        
        if self.grant.project_director:
            project_layout.addWidget(QLabel(f"Project Director: {self.grant.project_director}"))
        
        if self.grant.collaborating_organizations:
            collab_text = ", ".join(self.grant.collaborating_organizations)
            collab_label = QLabel(f"Collaborators: {collab_text}")
            collab_label.setWordWrap(True)
            project_layout.addWidget(collab_label)
        
        layout.addWidget(project_group)
        
        # Tags
        if self.grant.tags:
            tags_group = QGroupBox("Tags")
            tags_layout = QVBoxLayout(tags_group)
            tags_text = ", ".join(self.grant.tags)
            tags_label = QLabel(tags_text)
            tags_label.setWordWrap(True)
            tags_layout.addWidget(tags_label)
            layout.addWidget(tags_group)
        
        layout.addStretch()
        return widget
        
    def create_financial_tab(self) -> QWidget:
        """Create the financial details tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Financial summary
        summary_group = QGroupBox("Financial Summary")
        summary_layout = QFormLayout(summary_group)
        
        summary_layout.addRow("Grant Amount:", QLabel(f"${self.grant.amount:,.2f}"))
        
        if self.grant.total_project_cost:
            summary_layout.addRow("Total Project Cost:", 
                                 QLabel(f"${self.grant.total_project_cost:,.2f}"))
        
        if self.grant.match_required:
            summary_layout.addRow("Match Required:", 
                                 QLabel(f"${self.grant.match_required:,.2f}"))
        
        if self.grant.match_provided:
            summary_layout.addRow("Match Provided:", 
                                 QLabel(f"${self.grant.match_provided:,.2f}"))
        
        layout.addWidget(summary_group)
        
        # Budget breakdown
        if self.grant.budget_items:
            budget_group = QGroupBox("Budget Breakdown")
            budget_layout = QVBoxLayout(budget_group)
            
            budget_table = QTableWidget()
            budget_table.setColumnCount(5)
            budget_table.setHorizontalHeaderLabels([
                "Category", "Description", "Budgeted", "Actual", "Variance"
            ])
            budget_table.setRowCount(len(self.grant.budget_items))
            
            for row, item in enumerate(self.grant.budget_items):
                budget_table.setItem(row, 0, QTableWidgetItem(item.category))
                budget_table.setItem(row, 1, QTableWidgetItem(item.description))
                budget_table.setItem(row, 2, QTableWidgetItem(f"${item.budgeted_amount:,.2f}"))
                
                actual_text = f"${item.actual_amount:,.2f}" if item.actual_amount else "N/A"
                budget_table.setItem(row, 3, QTableWidgetItem(actual_text))
                
                if item.actual_amount is not None:
                    variance = item.actual_amount - item.budgeted_amount
                    variance_text = f"${variance:+,.2f}"
                    variance_item = QTableWidgetItem(variance_text)
                    if variance > 0:
                        variance_item.setBackground(QColor(255, 182, 193))  # Light red for over
                    elif variance < 0:
                        variance_item.setBackground(QColor(144, 238, 144))  # Light green for under
                    budget_table.setItem(row, 4, variance_item)
                else:
                    budget_table.setItem(row, 4, QTableWidgetItem("N/A"))
            
            budget_table.resizeColumnsToContents()
            budget_layout.addWidget(budget_table)
            layout.addWidget(budget_group)
        
        layout.addStretch()
        return widget
        
    def create_milestones_tab(self) -> QWidget:
        """Create the milestones tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        if not self.grant.milestones:
            no_milestones = QLabel("No milestones defined for this grant.")
            no_milestones.setAlignment(Qt.AlignCenter)
            no_milestones.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(no_milestones)
            return widget
        
        # Progress overview
        progress_group = QGroupBox("Progress Overview")
        progress_layout = QVBoxLayout(progress_group)
        
        completion_pct = self.grant.get_completion_percentage()
        progress_bar = QProgressBar()
        progress_bar.setValue(int(completion_pct))
        progress_layout.addWidget(QLabel(f"Overall Progress: {completion_pct:.1f}%"))
        progress_layout.addWidget(progress_bar)
        
        layout.addWidget(progress_group)
        
        # Milestones table
        milestones_group = QGroupBox("Milestones")
        milestones_layout = QVBoxLayout(milestones_group)
        
        milestones_table = QTableWidget()
        milestones_table.setColumnCount(5)
        milestones_table.setHorizontalHeaderLabels([
            "Title", "Due Date", "Completion Date", "Status", "Notes"
        ])
        milestones_table.setRowCount(len(self.grant.milestones))
        
        for row, milestone in enumerate(self.grant.milestones):
            milestones_table.setItem(row, 0, QTableWidgetItem(milestone.title))
            milestones_table.setItem(row, 1, 
                                   QTableWidgetItem(milestone.due_date.strftime("%m/%d/%Y")))
            
            completion_text = (milestone.completion_date.strftime("%m/%d/%Y") 
                             if milestone.completion_date else "Not completed")
            milestones_table.setItem(row, 2, QTableWidgetItem(completion_text))
            
            status_item = QTableWidgetItem(milestone.status)
            if milestone.status == "Completed":
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            elif milestone.status == "Overdue":
                status_item.setBackground(QColor(255, 182, 193))  # Light red
            elif milestone.status == "In Progress":
                status_item.setBackground(QColor(255, 255, 224))  # Light yellow
            milestones_table.setItem(row, 3, status_item)
            
            milestones_table.setItem(row, 4, QTableWidgetItem(milestone.notes))
        
        milestones_table.resizeColumnsToContents()
        milestones_layout.addWidget(milestones_table)
        layout.addWidget(milestones_group)
        
        return widget
        
    def create_documents_tab(self) -> QWidget:
        """Create the documents tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        if not self.grant.documents:
            no_docs = QLabel("No documents available for this grant.")
            no_docs.setAlignment(Qt.AlignCenter)
            no_docs.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(no_docs)
            return widget
        
        # Documents by type
        doc_types = {}
        for doc in self.grant.documents:
            doc_type = doc.document_type.value
            if doc_type not in doc_types:
                doc_types[doc_type] = []
            doc_types[doc_type].append(doc)
        
        for doc_type, docs in doc_types.items():
            type_group = QGroupBox(f"{doc_type} ({len(docs)})")
            type_layout = QVBoxLayout(type_group)
            
            for doc in docs:
                doc_widget = self.create_document_widget(doc)
                type_layout.addWidget(doc_widget)
            
            layout.addWidget(type_group)
        
        layout.addStretch()
        return widget
        
    def create_document_widget(self, document: GrantDocument) -> QWidget:
        """Create a widget for a single document."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet("QFrame { border: 1px solid #ccc; margin: 2px; }")
        
        layout = QHBoxLayout(widget)
        
        # Document info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(document.name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)
        
        if document.description:
            desc_label = QLabel(document.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666;")
            info_layout.addWidget(desc_label)
        
        details_text = f"Uploaded: {document.upload_date.strftime('%m/%d/%Y')}"
        if document.file_size:
            details_text += f" • Size: {document.get_size_formatted()}"
        details_label = QLabel(details_text)
        details_label.setStyleSheet("color: #888; font-size: 10px;")
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout, 1)
        
        # Action buttons
        actions_layout = QVBoxLayout()
        
        view_btn = icon_manager.create_button('view', 'View')
        view_btn.clicked.connect(lambda: self.view_document(document))
        actions_layout.addWidget(view_btn)
        
        if document.file_path and document.exists():
            open_btn = icon_manager.create_button('folder', 'Open')
            open_btn.clicked.connect(lambda: self.open_document(document))
            actions_layout.addWidget(open_btn)
        elif document.url:
            open_btn = QPushButton("🌐 Open")
            open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(document.url)))
            actions_layout.addWidget(open_btn)
        
        layout.addLayout(actions_layout)
        
        return widget
        
    def create_impact_tab(self) -> QWidget:
        """Create the impact and outcomes tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Impact metrics
        if self.grant.impact_metrics:
            metrics_group = QGroupBox("Impact Metrics")
            metrics_layout = QFormLayout(metrics_group)
            
            for key, value in self.grant.impact_metrics.items():
                display_key = key.replace('_', ' ').title()
                metrics_layout.addRow(f"{display_key}:", QLabel(str(value)))
            
            layout.addWidget(metrics_group)
        
        if self.grant.beneficiaries_served:
            beneficiaries_group = QGroupBox("Beneficiaries")
            beneficiaries_layout = QVBoxLayout(beneficiaries_group)
            beneficiaries_layout.addWidget(
                QLabel(f"Total Beneficiaries Served: {self.grant.beneficiaries_served}")
            )
            layout.addWidget(beneficiaries_group)
        
        # Success stories
        if self.grant.success_stories:
            success_group = QGroupBox("Success Stories")
            success_layout = QVBoxLayout(success_group)
            
            for story in self.grant.success_stories:
                story_label = QLabel(f"• {story}")
                story_label.setWordWrap(True)
                success_layout.addWidget(story_label)
            
            layout.addWidget(success_group)
        
        # Lessons learned
        if self.grant.lessons_learned:
            lessons_group = QGroupBox("Lessons Learned")
            lessons_layout = QVBoxLayout(lessons_group)
            
            for lesson in self.grant.lessons_learned:
                lesson_label = QLabel(f"• {lesson}")
                lesson_label.setWordWrap(True)
                lessons_layout.addWidget(lesson_label)
            
            layout.addWidget(lessons_group)
        
        # Notes
        if self.grant.notes:
            notes_group = QGroupBox("Additional Notes")
            notes_layout = QVBoxLayout(notes_group)
            
            notes_text = QTextEdit()
            notes_text.setPlainText(self.grant.notes)
            notes_text.setReadOnly(True)
            notes_layout.addWidget(notes_text)
            
            layout.addWidget(notes_group)
        
        layout.addStretch()
        return widget
        
    def view_document(self, document: GrantDocument):
        """View document details in a separate dialog."""
        dialog = DocumentViewerDialog(document, self)
        dialog.exec_()
        
    def open_document(self, document: GrantDocument):
        """Open document with default application."""
        if not document.file_path or not document.exists():
            QMessageBox.warning(self, "Error", "File not found!")
            return
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', document.file_path])
            elif platform.system() == 'Windows':  # Windows
                os.startfile(document.file_path)
            else:  # Linux
                subprocess.call(['xdg-open', document.file_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {e}")


class EnhancedPastGrantsTab(QWidget):
    """Enhanced Past Grants tab with detailed views and document management."""
    
    grant_selected = pyqtSignal(object)  # Emits selected EnhancedPastGrant
    
    def __init__(self):
        """Initialize the Enhanced Past Grants tab."""
        super().__init__()
        
        # Data
        self.past_grants_data = []
        self.filtered_grants_data = []
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
        
        # Main content area
        main_widget = self.create_main_content()
        layout.addWidget(main_widget)
        
    def create_header(self) -> QHBoxLayout:
        """Create the header section."""
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("📊 Enhanced Past Grants")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Comprehensive grant history with documents and analytics")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        # Add grant button
        add_btn = QPushButton("➕ Add Grant")
        add_btn.clicked.connect(self.add_new_grant)
        layout.addWidget(add_btn)
        
        return layout
        
    def create_main_content(self) -> QWidget:
        """Create the main content area."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filters and statistics
        filters_stats_layout = QHBoxLayout()
        
        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Year filter
        filters_layout.addWidget(QLabel("Year:"))
        self.year_filter = QComboBox()
        self.year_filter.addItem("All")
        self.year_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.year_filter)
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Federal", "State", "Foundation", "Corporate"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.type_filter)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "In Progress", "Received"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.status_filter)
        
        filters_layout.addStretch()
        
        filters_stats_layout.addWidget(filters_group)
        
        # Statistics
        self.stats_widget = self.create_stats_widget()
        filters_stats_layout.addWidget(self.stats_widget)
        
        layout.addLayout(filters_stats_layout)
        
        # Grants table
        self.grants_table = self.create_grants_table()
        layout.addWidget(self.grants_table)
        
        return widget
        
    def create_stats_widget(self) -> QWidget:
        """Create the statistics widget."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet("QFrame { background-color: #f0f0f0; border: 1px solid #ccc; }")
        
        layout = QVBoxLayout(widget)
        
        self.total_funding_label = QLabel("Total Funding: $0")
        self.grant_count_label = QLabel("Grants: 0")
        self.avg_grant_label = QLabel("Average: $0")
        self.completion_rate_label = QLabel("Completion Rate: 0%")
        
        layout.addWidget(self.total_funding_label)
        layout.addWidget(self.grant_count_label)
        layout.addWidget(self.avg_grant_label)
        layout.addWidget(self.completion_rate_label)
        
        return widget
        
    def create_grants_table(self) -> QTableWidget:
        """Create the enhanced grants table."""
        table = QTableWidget()
        
        # Set up columns
        headers = [
            "Title", "Funder", "Amount", "Year", "Type", 
            "Status", "Progress", "Documents", "Actions"
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
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Funder
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Year
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Progress
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Documents
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions
        
        # Connect double-click to show details
        table.itemDoubleClicked.connect(self.on_grant_double_clicked)
        
        return table
        
    def load_sample_data(self):
        """Load sample enhanced past grants data."""
        self.past_grants_data = create_enhanced_sample_past_grants()
        self.filtered_grants_data = self.past_grants_data.copy()
        
        # Populate year filter
        years = sorted(set(grant.year for grant in self.past_grants_data), reverse=True)
        for year in years:
            self.year_filter.addItem(str(year))
            
    def populate_grants_table(self):
        """Populate the grants table with enhanced data."""
        self.grants_table.setRowCount(len(self.filtered_grants_data))
        
        for row, grant in enumerate(self.filtered_grants_data):
            # Title
            title_item = QTableWidgetItem(grant.title)
            title_item.setData(Qt.UserRole, grant)
            self.grants_table.setItem(row, 0, title_item)
            
            # Funder
            self.grants_table.setItem(row, 1, QTableWidgetItem(grant.funder))
            
            # Amount
            amount_item = QTableWidgetItem(f"${grant.amount:,.0f}")
            self.grants_table.setItem(row, 2, amount_item)
            
            # Year
            self.grants_table.setItem(row, 3, QTableWidgetItem(str(grant.year)))
            
            # Type
            self.grants_table.setItem(row, 4, QTableWidgetItem(grant.type))
            
            # Status with color coding
            status_item = QTableWidgetItem(grant.status)
            if grant.status == "Completed":
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            elif grant.status == "In Progress":
                status_item.setBackground(QColor(255, 255, 224))  # Light yellow
            self.grants_table.setItem(row, 5, status_item)
            
            # Progress (for grants with milestones)
            if grant.milestones:
                progress_pct = grant.get_completion_percentage()
                progress_item = QTableWidgetItem(f"{progress_pct:.0f}%")
                self.grants_table.setItem(row, 6, progress_item)
            else:
                self.grants_table.setItem(row, 6, QTableWidgetItem("N/A"))
            
            # Document count
            doc_count = len(grant.documents)
            doc_item = QTableWidgetItem(f"{doc_count} files")
            self.grants_table.setItem(row, 7, doc_item)
            
            # Actions button
            actions_btn = QPushButton("📋 Details")
            actions_btn.clicked.connect(lambda checked, g=grant: self.show_grant_details(g))
            self.grants_table.setCellWidget(row, 8, actions_btn)
        
        # Update statistics
        self.update_statistics()
        
    def update_statistics(self):
        """Update the statistics display."""
        if not self.filtered_grants_data:
            self.total_funding_label.setText("Total Funding: $0")
            self.grant_count_label.setText("Grants: 0")
            self.avg_grant_label.setText("Average: $0")
            self.completion_rate_label.setText("Completion Rate: 0%")
            return
        
        total_funding = sum(grant.amount for grant in self.filtered_grants_data)
        grant_count = len(self.filtered_grants_data)
        avg_grant = total_funding / grant_count if grant_count > 0 else 0
        
        completed_grants = len([g for g in self.filtered_grants_data if g.status == "Completed"])
        completion_rate = (completed_grants / grant_count * 100) if grant_count > 0 else 0
        
        self.total_funding_label.setText(f"Total Funding: ${total_funding:,.0f}")
        self.grant_count_label.setText(f"Grants: {grant_count}")
        self.avg_grant_label.setText(f"Average: ${avg_grant:,.0f}")
        self.completion_rate_label.setText(f"Completion Rate: {completion_rate:.0f}%")
        
    def apply_filters(self):
        """Apply the current filters to the grants list."""
        filtered_data = self.past_grants_data.copy()
        
        # Year filter
        year_filter = self.year_filter.currentText()
        if year_filter != "All":
            filtered_data = [g for g in filtered_data if str(g.year) == year_filter]
        
        # Type filter
        type_filter = self.type_filter.currentText()
        if type_filter != "All":
            filtered_data = [g for g in filtered_data if g.type == type_filter]
        
        # Status filter
        status_filter = self.status_filter.currentText()
        if status_filter != "All":
            filtered_data = [g for g in filtered_data if g.status == status_filter]
        
        self.filtered_grants_data = filtered_data
        self.populate_grants_table()
        
    def on_grant_double_clicked(self, item):
        """Handle double-click on grant row to show details."""
        row = item.row()
        title_item = self.grants_table.item(row, 0)
        grant = title_item.data(Qt.UserRole)
        
        if grant:
            self.show_grant_details(grant)
            
    def show_grant_details(self, grant: EnhancedPastGrant):
        """Show detailed grant information in a dialog."""
        dialog = GrantDetailDialog(grant, self)
        # The dialog will be properly centered by its setup_ui method
        dialog.exec_()
        
    def add_new_grant(self):
        """Add a new grant (placeholder for future implementation)."""
        QMessageBox.information(
            self, 
            "Add New Grant", 
            "Grant addition feature will be implemented in the next update."
        )
    
    def update_organization_context(self, organization_profile):
        """Update the tab with organization context for filtering."""
        if organization_profile:
            self.current_organization = organization_profile
            # Apply organization-specific filtering
            self.apply_organization_filter()
            print(f"🏢 Updated past grants context for: {organization_profile.name}")
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
        for grant in self.past_grants_data:
            # Check if grant matches organization focus areas
            grant_relevance = any(
                focus_area.lower() in grant.purpose.lower()
                for focus_area in org_focus_areas
            ) if org_focus_areas and hasattr(grant, 'purpose') and grant.purpose else True
            
            # Check organization name match using the organization field
            org_relevance = True
            if org_name and hasattr(grant, 'organization'):
                grant_org = getattr(grant, 'organization', '')
                org_relevance = (
                    org_name.lower() in grant_org.lower() if grant_org
                    else False
                )
            
            if grant_relevance or org_relevance:
                relevant_grants.append(grant)
        
        # Update display with filtered grants
        self.filtered_grants_data = relevant_grants
        self.populate_grants_table()
        
        print(f"📊 Filtered to {len(relevant_grants)} past grants "
              f"for {org_name}")
    
    def center_on_parent(self):
        """Center the dialog on its parent or screen."""
        if self.parent():
            # Center on parent widget
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            # Calculate position to center this dialog
            dialog_size = self.size()
            new_x = parent_center.x() - dialog_size.width() // 2
            new_y = parent_center.y() - dialog_size.height() // 2
            
            # Ensure the dialog stays within screen bounds
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            
            new_x = max(screen_geometry.left(), 
                       min(new_x, screen_geometry.right() - dialog_size.width()))
            new_y = max(screen_geometry.top(), 
                       min(new_y, screen_geometry.bottom() - dialog_size.height()))
            
            self.move(new_x, new_y)
        else:
            # Center on screen
            desktop = QApplication.desktop()
            screen_geometry = desktop.availableGeometry()
            screen_center = screen_geometry.center()
            
            dialog_size = self.size()
            new_x = screen_center.x() - dialog_size.width() // 2
            new_y = screen_center.y() - dialog_size.height() // 2
            
            self.move(new_x, new_y)
