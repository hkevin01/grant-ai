"""
PyQt5 GUI components for questionnaire system.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGroupBox,
)

from grant_ai.models.questionnaire import (
    Question,
    Questionnaire,
    QuestionnaireResponse,
    QuestionType,
)
from grant_ai.services.questionnaire_manager import QuestionnaireManager
from grant_ai.services.ai_questionnaire_filler import AIQuestionnaireFiller


class QuestionWidget(QWidget):
    """Widget for displaying and answering a single question."""
    
    responseChanged = pyqtSignal(str, object)  # question_id, response
    
    def __init__(self, question: Question, initial_value: Any = None):
        super().__init__()
        self.question = question
        self.input_widget = None
        self.setup_ui()
        
        if initial_value is not None:
            self.set_value(initial_value)
    
    def setup_ui(self):
        """Set up the question widget UI."""
        layout = QVBoxLayout()
        
        # Question text
        question_text = self.question.text
        if self.question.required:
            question_text += " *"
        
        question_label = QLabel(question_text)
        question_label.setWordWrap(True)
        layout.addWidget(question_label)
        
        # Help text
        if self.question.help_text:
            help_label = QLabel(self.question.help_text)
            help_label.setStyleSheet("color: gray; font-size: 10pt;")
            help_label.setWordWrap(True)
            layout.addWidget(help_label)
        
        # Input widget based on question type
        if self.question.question_type == QuestionType.TEXT:
            self.input_widget = QLineEdit()
            if self.question.field_mapping == "contact_phone":
                self.input_widget.setPlaceholderText("(555) 123-4567")
            elif self.question.field_mapping == "ein":
                self.input_widget.setPlaceholderText("12-3456789")
            self.input_widget.textChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.TEXTAREA:
            self.input_widget = QTextEdit()
            self.input_widget.setMaximumHeight(100)
            self.input_widget.textChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.EMAIL:
            self.input_widget = QLineEdit()
            self.input_widget.setPlaceholderText("name@example.org")
            self.input_widget.textChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.URL:
            self.input_widget = QLineEdit()
            self.input_widget.setPlaceholderText("https://www.example.org")
            self.input_widget.textChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.NUMBER:
            self.input_widget = QSpinBox()
            self.input_widget.setMinimum(int(self.question.min_value or 0))
            self.input_widget.setMaximum(int(self.question.max_value or 999999999))
            if self.question.field_mapping == "founded_year":
                self.input_widget.setMinimum(1800)
                self.input_widget.setMaximum(2024)
            self.input_widget.valueChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.MULTIPLE_CHOICE:
            self.input_widget = QComboBox()
            if self.question.options:
                self.input_widget.addItems(self.question.options)
            self.input_widget.currentTextChanged.connect(self._on_value_changed)
        
        elif self.question.question_type == QuestionType.CHECKBOX:
            # Create a container for checkboxes
            self.input_widget = QWidget()
            checkbox_layout = QVBoxLayout()
            self.checkboxes = {}
            
            if self.question.options:
                for option in self.question.options:
                    checkbox = QCheckBox(option)
                    checkbox.stateChanged.connect(self._on_checkbox_changed)
                    self.checkboxes[option] = checkbox
                    checkbox_layout.addWidget(checkbox)
            
            self.input_widget.setLayout(checkbox_layout)
        
        if self.input_widget:
            layout.addWidget(self.input_widget)
        
        self.setLayout(layout)
    
    def _on_value_changed(self):
        """Handle value changes in input widgets."""
        value = self.get_value()
        self.responseChanged.emit(self.question.id, value)
    
    def _on_checkbox_changed(self):
        """Handle checkbox changes."""
        selected_options = []
        for option, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                selected_options.append(option)
        self.responseChanged.emit(self.question.id, selected_options)
    
    def get_value(self) -> Any:
        """Get the current value from the input widget."""
        if self.question.question_type == QuestionType.TEXT:
            return self.input_widget.text()
        elif self.question.question_type == QuestionType.TEXTAREA:
            return self.input_widget.toPlainText()
        elif self.question.question_type == QuestionType.EMAIL:
            return self.input_widget.text()
        elif self.question.question_type == QuestionType.URL:
            return self.input_widget.text()
        elif self.question.question_type == QuestionType.NUMBER:
            return self.input_widget.value()
        elif self.question.question_type == QuestionType.MULTIPLE_CHOICE:
            return self.input_widget.currentText()
        elif self.question.question_type == QuestionType.CHECKBOX:
            selected_options = []
            for option, checkbox in self.checkboxes.items():
                if checkbox.isChecked():
                    selected_options.append(option)
            return selected_options
        return None
    
    def set_value(self, value: Any):
        """Set the value in the input widget."""
        if self.question.question_type == QuestionType.TEXT:
            self.input_widget.setText(str(value) if value else "")
        elif self.question.question_type == QuestionType.TEXTAREA:
            self.input_widget.setPlainText(str(value) if value else "")
        elif self.question.question_type == QuestionType.EMAIL:
            self.input_widget.setText(str(value) if value else "")
        elif self.question.question_type == QuestionType.URL:
            self.input_widget.setText(str(value) if value else "")
        elif self.question.question_type == QuestionType.NUMBER:
            self.input_widget.setValue(int(value) if value else 0)
        elif self.question.question_type == QuestionType.MULTIPLE_CHOICE:
            if value in self.question.options:
                self.input_widget.setCurrentText(str(value))
        elif self.question.question_type == QuestionType.CHECKBOX:
            if isinstance(value, list):
                for option, checkbox in self.checkboxes.items():
                    checkbox.setChecked(option in value)


class QuestionnaireWidget(QWidget):
    """Widget for displaying and completing a questionnaire."""
    
    profileCreated = pyqtSignal(object)  # OrganizationProfile
    
    def __init__(self):
        super().__init__()
        self.manager = QuestionnaireManager()
        self.ai_filler = AIQuestionnaireFiller()
        self.questionnaire = None
        self.response = None
        self.question_widgets = {}
        self.setup_ui()
        self.load_questionnaire()
    
    def setup_ui(self):
        """Set up the questionnaire widget UI."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("📋 Organization Profile Questionnaire")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "Complete this questionnaire to create a comprehensive organization profile. "
            "This information will be used to match you with relevant grants and funding opportunities."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 5px;")
        layout.addWidget(desc_label)
        
        # AI Auto-fill section
        ai_group = QGroupBox("🤖 AI-Powered Auto-Fill")
        ai_layout = QVBoxLayout()
        
        ai_desc = QLabel(
            "Enter basic organization information below and let AI intelligently fill out the entire questionnaire for you!"
        )
        ai_desc.setWordWrap(True)
        ai_desc.setStyleSheet("color: #666; margin: 5px;")
        ai_layout.addWidget(ai_desc)
        
        # Basic info inputs for AI
        basic_info_layout = QFormLayout()
        
        self.ai_org_name = QLineEdit()
        self.ai_org_name.setPlaceholderText("e.g., Coda Mountain Academy")
        basic_info_layout.addRow("Organization Name:", self.ai_org_name)
        
        self.ai_org_description = QTextEdit()
        self.ai_org_description.setMaximumHeight(80)
        self.ai_org_description.setPlaceholderText("Brief description of your organization (optional)")
        basic_info_layout.addRow("Description:", self.ai_org_description)
        
        self.ai_location = QLineEdit()
        self.ai_location.setPlaceholderText("e.g., Charleston, WV")
        basic_info_layout.addRow("Location:", self.ai_location)
        
        self.ai_website = QLineEdit()
        self.ai_website.setPlaceholderText("https://www.example.org")
        basic_info_layout.addRow("Website:", self.ai_website)
        
        ai_layout.addLayout(basic_info_layout)
        
        # AI Auto-fill button
        self.ai_fill_btn = QPushButton("🤖 AI Auto-Fill Questionnaire")
        self.ai_fill_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.ai_fill_btn.clicked.connect(self.ai_auto_fill_questionnaire)
        ai_layout.addWidget(self.ai_fill_btn)
        
        # AI status label
        self.ai_status_label = QLabel("")
        self.ai_status_label.setStyleSheet("color: #666; font-style: italic;")
        ai_layout.addWidget(self.ai_status_label)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Manual questionnaire section
        manual_group = QGroupBox("✏️ Manual Questionnaire")
        manual_layout = QVBoxLayout()
        
        # Scroll area for questions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.questions_widget = QWidget()
        self.questions_layout = QVBoxLayout()
        self.questions_widget.setLayout(self.questions_layout)
        
        scroll_area.setWidget(self.questions_widget)
        manual_layout.addWidget(scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_draft_btn = QPushButton("💾 Save Draft")
        self.save_draft_btn.clicked.connect(self.save_draft)
        button_layout.addWidget(self.save_draft_btn)
        
        self.load_draft_btn = QPushButton("📂 Load Draft")
        self.load_draft_btn.clicked.connect(self.load_draft)
        button_layout.addWidget(self.load_draft_btn)
        
        self.create_profile_btn = QPushButton("✅ Create Profile")
        self.create_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.create_profile_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(self.create_profile_btn)
        
        manual_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        manual_layout.addWidget(self.status_label)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        self.setLayout(layout)
    
    def ai_auto_fill_questionnaire(self):
        """Use AI to automatically fill out the entire questionnaire."""
        org_name = self.ai_org_name.text().strip()
        if not org_name:
            self.ai_status_label.setText("Please enter an organization name first.")
            return
        
        # Update UI
        self.ai_fill_btn.setEnabled(False)
        self.ai_fill_btn.setText("🤖 AI is filling questionnaire...")
        self.ai_status_label.setText("AI is analyzing your organization and filling out the questionnaire...")
        
        try:
            # Get basic info
            org_description = self.ai_org_description.toPlainText().strip()
            location = self.ai_location.text().strip()
            website = self.ai_website.text().strip()
            
            # Use AI to fill questionnaire
            ai_responses = self.ai_filler.fill_questionnaire(
                org_name=org_name,
                org_description=org_description,
                location=location,
                website=website
            )
            
            # Apply AI responses to questionnaire
            self._apply_ai_responses(ai_responses)
            
            self.ai_status_label.setText("✅ AI has successfully filled out the questionnaire! Review and adjust as needed.")
            
        except Exception as e:
            self.ai_status_label.setText(f"❌ Error: {str(e)}")
        finally:
            self.ai_fill_btn.setEnabled(True)
            self.ai_fill_btn.setText("🤖 AI Auto-Fill Questionnaire")
    
    def _apply_ai_responses(self, ai_responses: Dict[str, Any]):
        """Apply AI responses to the questionnaire widgets."""
        if not self.questionnaire:
            return
        
        # Map AI responses to questionnaire fields
        field_mapping = {
            'org_name': 'org_name',
            'org_description': 'org_description',
            'focus_areas': 'focus_areas',
            'program_types': 'program_types',
            'target_demographics': 'target_demographics',
            'annual_budget': 'annual_budget',
            'location': 'location',
            'website': 'website',
            'ein': 'ein',
            'founded_year': 'founded_year',
            'preferred_grant_min': 'preferred_grant_min',
            'preferred_grant_max': 'preferred_grant_max',
            'contact_name': 'contact_name',
            'contact_email': 'contact_email',
            'contact_phone': 'contact_phone'
        }
        
        # Apply responses to each question
        for question in self.questionnaire.questions:
            question_id = question.id
            field_name = question.field_mapping
            
            if field_name in ai_responses:
                value = ai_responses[field_name]
                
                # Set the value in the question widget
                if question_id in self.question_widgets:
                    widget = self.question_widgets[question_id]
                    widget.set_value(value)
                    
                    # Update the response
                    if self.response:
                        self.response.responses[question_id] = value
        
        # Update status
        self.status_label.setText("✅ Questionnaire filled with AI-generated responses. Review and adjust as needed.")
    
    def load_questionnaire(self):
        """Load the default questionnaire."""
        self.questionnaire = self.manager.get_questionnaire()
        self.response = self.manager.create_response("org_profile_v1")
        
        # Create question widgets
        for question in self.questionnaire.questions:
            question_widget = QuestionWidget(question)
            question_widget.responseChanged.connect(self.on_response_changed)
            self.question_widgets[question.id] = question_widget
            self.questions_layout.addWidget(question_widget)
    
    def on_response_changed(self, question_id: str, response: Any):
        """Handle response changes."""
        self.response.set_response(question_id, response)
    
    def save_draft(self):
        """Save current responses as draft."""
        try:
            self.manager.save_response(self.response)
            QMessageBox.information(
                self, 
                "Draft Saved", 
                "Your responses have been saved as a draft."
            )
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Save Error", 
                f"Failed to save draft: {str(e)}"
            )
    
    def load_draft(self):
        """Load saved draft responses."""
        try:
            saved_response = self.manager.load_response("org_profile_v1")
            if saved_response:
                self.response = saved_response
                # Update question widgets with saved values
                for question_id, value in self.response.responses.items():
                    if question_id in self.question_widgets:
                        self.question_widgets[question_id].set_value(value)
                
                QMessageBox.information(
                    self, 
                    "Draft Loaded", 
                    "Your draft responses have been loaded."
                )
            else:
                QMessageBox.information(
                    self, 
                    "No Draft", 
                    "No saved draft found."
                )
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Load Error", 
                f"Failed to load draft: {str(e)}"
            )
    
    def validate_responses(self):
        """Validate current responses."""
        errors = self.manager.validate_response(self.response, self.questionnaire)
        
        if errors:
            error_text = "Please fix the following issues:\n\n"
            error_text += "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Errors", error_text)
        else:
            QMessageBox.information(
                self, 
                "Validation Successful", 
                "All responses are valid! You can now create your profile."
            )
    
    def create_profile(self):
        """Create organization profile from responses."""
        # Validate first
        errors = self.manager.validate_response(self.response, self.questionnaire)
        
        if errors:
            error_text = "Please fix the following issues before creating profile:\n\n"
            error_text += "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, "Validation Errors", error_text)
            return
        
        try:
            # Convert to organization profile
            profile = self.manager.convert_to_organization_profile(
                self.response, 
                self.questionnaire
            )
            
            # Emit signal with new profile
            self.profileCreated.emit(profile)
            
            QMessageBox.information(
                self, 
                "Profile Created", 
                f"Organization profile '{profile.name}' has been created successfully!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Profile Creation Error", 
                f"Failed to create profile: {str(e)}"
            )
