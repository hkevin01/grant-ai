"""
AI Writing Assistant GUI Widget for Grant-AI
Integrates AI-powered grant writing assistance into the Material Design interface
"""
import asyncio
from datetime import datetime
from typing import Any, Dict

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import DATA_DIR
from ..gui.material_theme import MaterialTheme
from ..gui.modern_ui import MaterialButton, MaterialCard
from ..services.ai_grant_writing import ProposalSection, ai_writing_assistant


class AIGenerationWorker(QThread):
    """Worker thread for AI content generation"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, section_type: str, context: Dict[str, Any]):
        super().__init__()
        self.section_type = section_type
        self.context = context

    def run(self):
        """Run the AI generation in a separate thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                ai_writing_assistant.generate_section_content(
                    self.section_type, self.context
                )
            )

            loop.close()

            if "error" in result:
                self.error.emit(result["error"])
            else:
                self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class AIReviewWorker(QThread):
    """Worker thread for AI content review"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, content: str, review_type: str, context: Dict[str, Any]):
        super().__init__()
        self.content = content
        self.review_type = review_type
        self.context = context

    def run(self):
        """Run the AI review in a separate thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                ai_writing_assistant.review_section(
                    self.content, self.review_type, self.context
                )
            )

            loop.close()

            if "error" in result:
                self.error.emit(result["error"])
            else:
                self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class ProposalSectionWidget(MaterialCard):
    """Widget for editing a single proposal section"""

    content_changed = pyqtSignal(str, str)  # section_title, content
    review_requested = pyqtSignal(str, str)  # section_title, review_type

    def __init__(self, section: ProposalSection, theme: MaterialTheme):
        super().__init__(theme)
        self.section = section
        self.theme = theme
        self.setup_ui()

    def setup_ui(self):
        """Setup the section editing interface"""
        layout = QVBoxLayout()

        # Section header
        header_layout = QHBoxLayout()

        title_label = QLabel(self.section.title)
        title_label.setFont(QFont("Roboto", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme.primary_color};")
        header_layout.addWidget(title_label)

        # Word count and status
        self.word_count_label = QLabel(f"{self.section.get_word_count()} words")
        self.word_count_label.setStyleSheet(f"color: {self.theme.secondary_color};")
        header_layout.addWidget(self.word_count_label)

        if self.section.word_limit:
            limit_label = QLabel(f"/ {self.section.word_limit} limit")
            limit_label.setStyleSheet(f"color: {self.theme.secondary_color};")
            header_layout.addWidget(limit_label)

        header_layout.addStretch()

        # Status indicator
        status = self.section.get_status()
        status_colors = {
            "empty": self.theme.error_color,
            "needs_expansion": self.theme.warning_color,
            "over_limit": self.theme.error_color,
            "complete": self.theme.success_color
        }

        status_label = QLabel(status.replace("_", " ").title())
        status_label.setStyleSheet(
            f"color: {status_colors.get(status, self.theme.secondary_color)}; "
            f"font-weight: bold;"
        )
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Content editor
        self.content_editor = QTextEdit()
        self.content_editor.setPlainText(self.section.content)
        self.content_editor.setMinimumHeight(200)
        self.content_editor.setFont(QFont("Roboto", 11))
        self.content_editor.setStyleSheet(
            f"QTextEdit {{"
            f"  border: 1px solid {self.theme.outline_color};"
            f"  border-radius: 8px;"
            f"  padding: 12px;"
            f"  background-color: {self.theme.surface_color};"
            f"  color: {self.theme.on_surface_color};"
            f"}}"
        )
        self.content_editor.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.content_editor)

        # Action buttons
        button_layout = QHBoxLayout()

        review_button = MaterialButton("Review with AI", self.theme)
        review_button.clicked.connect(self.show_review_options)
        button_layout.addWidget(review_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # AI suggestions (if any)
        if self.section.ai_suggestions:
            suggestions_label = QLabel("AI Suggestions:")
            suggestions_label.setFont(QFont("Roboto", 12, QFont.Bold))
            layout.addWidget(suggestions_label)

            for suggestion in self.section.ai_suggestions[-3:]:  # Show last 3
                suggestion_text = QLabel(f"• {suggestion}")
                suggestion_text.setWordWrap(True)
                suggestion_text.setStyleSheet(
                    f"color: {self.theme.secondary_color}; margin-left: 16px;"
                )
                layout.addWidget(suggestion_text)

        self.setLayout(layout)

    def on_content_changed(self):
        """Handle content changes"""
        self.section.content = self.content_editor.toPlainText()
        self.section.last_updated = datetime.now()
        self.update_word_count()
        self.content_changed.emit(self.section.title, self.section.content)

    def update_word_count(self):
        """Update the word count display"""
        count = self.section.get_word_count()
        self.word_count_label.setText(f"{count} words")

        # Update color based on limit
        if self.section.word_limit:
            if count > self.section.word_limit:
                color = self.theme.error_color
            elif count < self.section.word_limit * 0.8:
                color = self.theme.warning_color
            else:
                color = self.theme.success_color

            self.word_count_label.setStyleSheet(f"color: {color};")

    def show_review_options(self):
        """Show review type selection dialog"""
        dialog = QMessageBox()
        dialog.setWindowTitle("AI Review Options")
        dialog.setText("Select review type:")

        clarity_btn = dialog.addButton("Clarity Check", QMessageBox.ActionRole)
        alignment_btn = dialog.addButton("Alignment Analysis", QMessageBox.ActionRole)
        competitive_btn = dialog.addButton("Competitiveness Analysis", QMessageBox.ActionRole)
        dialog.addButton("Cancel", QMessageBox.RejectRole)

        dialog.exec_()

        clicked = dialog.clickedButton()
        if clicked == clarity_btn:
            self.review_requested.emit(self.section.title, "clarity_check")
        elif clicked == alignment_btn:
            self.review_requested.emit(self.section.title, "alignment_analysis")
        elif clicked == competitive_btn:
            self.review_requested.emit(self.section.title, "competitiveness_analysis")


class ProposalMetadataWidget(MaterialCard):
    """Widget for editing proposal metadata"""

    metadata_changed = pyqtSignal(dict)

    def __init__(self, proposal, theme: MaterialTheme):
        super().__init__(theme)
        self.proposal = proposal
        self.theme = theme
        self.setup_ui()

    def setup_ui(self):
        """Setup the metadata editing interface"""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Proposal Information")
        title_label.setFont(QFont("Roboto", 16, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme.primary_color}; margin-bottom: 16px;")
        layout.addWidget(title_label)

        # Proposal title
        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit(self.proposal.title)
        self.title_edit.setStyleSheet(
            f"QLineEdit {{"
            f"  border: 1px solid {self.theme.outline_color};"
            f"  border-radius: 4px;"
            f"  padding: 8px;"
            f"  background-color: {self.theme.surface_color};"
            f"}}"
        )
        layout.addWidget(self.title_edit)

        # Grant ID
        layout.addWidget(QLabel("Grant ID:"))
        self.grant_id_edit = QLineEdit(self.proposal.grant_id)
        self.grant_id_edit.setStyleSheet(self.title_edit.styleSheet())
        layout.addWidget(self.grant_id_edit)

        # Organization
        layout.addWidget(QLabel("Organization:"))
        self.org_edit = QLineEdit(self.proposal.organization_id)
        self.org_edit.setStyleSheet(self.title_edit.styleSheet())
        layout.addWidget(self.org_edit)

        # Metadata fields
        metadata_fields = [
            ("Agency:", "agency"),
            ("Program:", "program"),
            ("Funding Amount:", "funding_amount"),
            ("Deadline:", "deadline"),
            ("Submission Method:", "submission_method")
        ]

        self.metadata_edits = {}
        for label, key in metadata_fields:
            layout.addWidget(QLabel(label))
            edit = QLineEdit(str(self.proposal.metadata.get(key, "")))
            edit.setStyleSheet(self.title_edit.styleSheet())
            self.metadata_edits[key] = edit
            layout.addWidget(edit)

        # Connect change signals
        self.title_edit.textChanged.connect(self.on_metadata_changed)
        self.grant_id_edit.textChanged.connect(self.on_metadata_changed)
        self.org_edit.textChanged.connect(self.on_metadata_changed)

        for edit in self.metadata_edits.values():
            edit.textChanged.connect(self.on_metadata_changed)

        layout.addStretch()
        self.setLayout(layout)

    def on_metadata_changed(self):
        """Handle metadata changes"""
        self.proposal.title = self.title_edit.text()
        self.proposal.grant_id = self.grant_id_edit.text()
        self.proposal.organization_id = self.org_edit.text()

        for key, edit in self.metadata_edits.items():
            self.proposal.metadata[key] = edit.text()

        self.metadata_changed.emit(self.proposal.metadata)


class AIWritingAssistantWidget(QWidget):
    """Main AI Writing Assistant Widget"""

    def __init__(self, theme: MaterialTheme):
        super().__init__()
        self.theme = theme
        self.current_proposal = None
        self.section_widgets = {}
        self.generation_worker = None
        self.review_worker = None
        self.setup_ui()
        self.load_proposals()

    def setup_ui(self):
        """Setup the main AI writing interface"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🤖 AI Grant Writing Assistant")
        title_label.setFont(QFont("Roboto", 20, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.theme.primary_color}; margin: 16px 0;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Proposal selector
        self.proposal_selector = QComboBox()
        self.proposal_selector.setMinimumWidth(300)
        self.proposal_selector.setStyleSheet(
            f"QComboBox {{"
            f"  border: 1px solid {self.theme.outline_color};"
            f"  border-radius: 4px;"
            f"  padding: 8px;"
            f"  background-color: {self.theme.surface_color};"
            f"}}"
        )
        self.proposal_selector.currentTextChanged.connect(self.on_proposal_selected)
        header_layout.addWidget(QLabel("Proposal:"))
        header_layout.addWidget(self.proposal_selector)

        # Action buttons
        new_proposal_btn = MaterialButton("New Proposal", self.theme)
        new_proposal_btn.clicked.connect(self.create_new_proposal)
        header_layout.addWidget(new_proposal_btn)

        save_btn = MaterialButton("Save", self.theme)
        save_btn.clicked.connect(self.save_proposals)
        header_layout.addWidget(save_btn)

        layout.addLayout(header_layout)

        # Main content area
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Proposal info and generation
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Proposal metadata
        self.metadata_widget = None
        left_layout.addWidget(QLabel("No proposal selected"))

        # Section generation
        generation_card = MaterialCard(self.theme)
        gen_layout = QVBoxLayout()

        gen_title = QLabel("Generate New Section")
        gen_title.setFont(QFont("Roboto", 14, QFont.Bold))
        gen_layout.addWidget(gen_title)

        gen_layout.addWidget(QLabel("Section Type:"))
        self.section_type_combo = QComboBox()
        self.section_type_combo.addItems([
            "specific_aims",
            "narrative",
            "budget_narrative"
        ])
        gen_layout.addWidget(self.section_type_combo)

        generate_btn = MaterialButton("Generate with AI", self.theme)
        generate_btn.clicked.connect(self.generate_section)
        gen_layout.addWidget(generate_btn)

        self.generation_progress = QProgressBar()
        self.generation_progress.setVisible(False)
        gen_layout.addWidget(self.generation_progress)

        generation_card.setLayout(gen_layout)
        left_layout.addWidget(generation_card)

        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(350)

        # Right panel - Section editor
        self.sections_tab_widget = QTabWidget()
        self.sections_tab_widget.setStyleSheet(
            f"QTabWidget::pane {{"
            f"  border: 1px solid {self.theme.outline_color};"
            f"  background-color: {self.theme.surface_color};"
            f"}}"
            f"QTabBar::tab {{"
            f"  background-color: {self.theme.surface_variant_color};"
            f"  color: {self.theme.on_surface_color};"
            f"  padding: 12px 16px;"
            f"  margin-right: 2px;"
            f"}}"
            f"QTabBar::tab:selected {{"
            f"  background-color: {self.theme.primary_container_color};"
            f"  color: {self.theme.on_primary_container_color};"
            f"}}"
        )

        splitter.addWidget(left_panel)
        splitter.addWidget(self.sections_tab_widget)
        splitter.setSizes([350, 800])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def load_proposals(self):
        """Load existing proposals"""
        proposals_file = DATA_DIR / "proposals.json"
        ai_writing_assistant.load_proposals(str(proposals_file))

        self.proposal_selector.clear()
        self.proposal_selector.addItem("Select a proposal...")

        for proposal_id in ai_writing_assistant.proposals.keys():
            proposal = ai_writing_assistant.proposals[proposal_id]
            display_text = f"{proposal.title} ({proposal.grant_id})"
            self.proposal_selector.addItem(display_text, proposal_id)

    def on_proposal_selected(self, text: str):
        """Handle proposal selection"""
        if text == "Select a proposal...":
            return

        # Get proposal ID from combo box data
        current_index = self.proposal_selector.currentIndex()
        if current_index <= 0:
            return

        proposal_id = self.proposal_selector.itemData(current_index)
        if not proposal_id:
            return

        self.current_proposal = ai_writing_assistant.proposals.get(proposal_id)
        if self.current_proposal:
            self.load_proposal_editor()

    def load_proposal_editor(self):
        """Load the proposal into the editor"""
        if not self.current_proposal:
            return

        # Clear existing tabs
        self.sections_tab_widget.clear()
        self.section_widgets.clear()

        # Add metadata widget to left panel if not already present
        if self.metadata_widget:
            self.metadata_widget.setParent(None)

        self.metadata_widget = ProposalMetadataWidget(self.current_proposal, self.theme)
        self.metadata_widget.metadata_changed.connect(self.on_metadata_changed)

        # Find the left panel layout and replace the placeholder
        left_panel = self.layout().itemAt(1).widget().widget(0)
        left_layout = left_panel.layout()
        left_layout.replaceWidget(left_layout.itemAt(0).widget(), self.metadata_widget)

        # Add section tabs
        for section_title, section in self.current_proposal.sections.items():
            section_widget = ProposalSectionWidget(section, self.theme)
            section_widget.content_changed.connect(self.on_section_changed)
            section_widget.review_requested.connect(self.review_section)

            self.section_widgets[section_title] = section_widget

            # Create scrollable area for the section
            scroll_area = QScrollArea()
            scroll_area.setWidget(section_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet(f"border: none; background-color: {self.theme.background_color};")

            self.sections_tab_widget.addTab(scroll_area, section_title)

    def create_new_proposal(self):
        """Create a new proposal"""
        from PyQt5.QtWidgets import QInputDialog

        title, ok = QInputDialog.getText(self, "New Proposal", "Proposal title:")
        if not ok or not title.strip():
            return

        grant_id, ok = QInputDialog.getText(self, "New Proposal", "Grant ID:")
        if not ok or not grant_id.strip():
            return

        organization, ok = QInputDialog.getText(self, "New Proposal", "Organization:")
        if not ok or not organization.strip():
            return

        # Create proposal
        proposal_id = ai_writing_assistant.create_proposal(title, grant_id, organization)

        # Refresh selector
        self.load_proposals()

        # Select the new proposal
        for i in range(self.proposal_selector.count()):
            if self.proposal_selector.itemData(i) == proposal_id:
                self.proposal_selector.setCurrentIndex(i)
                break

    def generate_section(self):
        """Generate a new section using AI"""
        if not self.current_proposal:
            QMessageBox.warning(self, "Warning", "Please select a proposal first.")
            return

        section_type = self.section_type_combo.currentText()

        # Show progress
        self.generation_progress.setVisible(True)
        self.generation_progress.setRange(0, 0)  # Indeterminate

        # Gather context (simplified for demo)
        context = {
            "title": self.current_proposal.title,
            "agency": self.current_proposal.metadata.get("agency", ""),
            "program": self.current_proposal.metadata.get("program", ""),
            "focus_area": "Education",  # Could be dynamic
            "budget": self.current_proposal.metadata.get("funding_amount", ""),
            "organization_profile": self.current_proposal.organization_id,
            "project_overview": "Innovative educational program"  # Could be dynamic
        }

        # Start generation worker
        self.generation_worker = AIGenerationWorker(section_type, context)
        self.generation_worker.finished.connect(self.on_generation_finished)
        self.generation_worker.error.connect(self.on_generation_error)
        self.generation_worker.start()

    @pyqtSlot(dict)
    def on_generation_finished(self, result):
        """Handle successful AI generation"""
        self.generation_progress.setVisible(False)

        section_type = self.section_type_combo.currentText()
        section_title = section_type.replace('_', ' ').title()

        # Create new section
        from ..services.ai_grant_writing import ProposalSection
        section = ProposalSection(
            title=section_title,
            content=result["content"],
            section_type=section_type
        )

        # Add to proposal
        self.current_proposal.add_section(section)

        # Refresh editor
        self.load_proposal_editor()

        # Show success message
        QMessageBox.information(
            self,
            "Success",
            f"Generated {section_title} with {result['word_count']} words using {result['ai_provider']}"
        )

    @pyqtSlot(str)
    def on_generation_error(self, error_msg):
        """Handle AI generation error"""
        self.generation_progress.setVisible(False)
        QMessageBox.critical(self, "Generation Error", f"Failed to generate content: {error_msg}")

    def review_section(self, section_title: str, review_type: str):
        """Review a section with AI"""
        if section_title not in self.current_proposal.sections:
            return

        section = self.current_proposal.sections[section_title]

        # Gather review context (simplified)
        context = {}
        if review_type == "alignment_analysis":
            from PyQt5.QtWidgets import QInputDialog
            funder, ok = QInputDialog.getText(self, "Review Context", "Funder name:")
            if not ok:
                return
            context["funder"] = funder
            context["program"] = self.current_proposal.metadata.get("program", "")
            context["priorities"] = "Innovation, Impact, Sustainability"

        # Start review worker
        self.review_worker = AIReviewWorker(section.content, review_type, context)
        self.review_worker.finished.connect(lambda result: self.on_review_finished(section_title, result))
        self.review_worker.error.connect(self.on_review_error)
        self.review_worker.start()

    def on_review_finished(self, section_title: str, result: dict):
        """Handle successful AI review"""
        # Show review feedback
        QMessageBox.information(
            self,
            f"AI Review: {section_title}",
            result["feedback"]
        )

        # Save feedback to section
        section = self.current_proposal.sections[section_title]
        section.review_feedback.append({
            "type": result["review_type"],
            "feedback": result["feedback"],
            "timestamp": result["reviewed_at"]
        })

    def on_review_error(self, error_msg: str):
        """Handle AI review error"""
        QMessageBox.critical(self, "Review Error", f"Failed to review content: {error_msg}")

    def on_section_changed(self, section_title: str, content: str):
        """Handle section content changes"""
        if self.current_proposal and section_title in self.current_proposal.sections:
            self.current_proposal.sections[section_title].content = content
            self.current_proposal.last_updated = datetime.now()

    def on_metadata_changed(self, metadata: dict):
        """Handle metadata changes"""
        if self.current_proposal:
            self.current_proposal.metadata.update(metadata)
            self.current_proposal.last_updated = datetime.now()

    def save_proposals(self):
        """Save all proposals to file"""
        proposals_file = DATA_DIR / "proposals.json"
        ai_writing_assistant.save_proposals(str(proposals_file))

        # Show success message briefly
        QMessageBox.information(self, "Saved", "Proposals saved successfully!")
            self.current_proposal.last_updated = datetime.now()

    def save_proposals(self):
        """Save all proposals to file"""
        proposals_file = DATA_DIR / "proposals.json"
        ai_writing_assistant.save_proposals(str(proposals_file))

        # Show success message briefly
        QMessageBox.information(self, "Saved", "Proposals saved successfully!")
