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
)

from grant_ai.models.questionnaire import (
    Question,
    Questionnaire,
    QuestionnaireResponse,
    QuestionType,
)
from grant_ai.services.questionnaire_manager import QuestionnaireManager


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
        self.questionnaire = None
        self.response = None
        self.question_widgets = {}
        self.setup_ui()
        self.load_questionnaire()
    
    def setup_ui(self):
        """Set up the questionnaire widget UI."""
        layout = QVBoxLayout()
        
        # Title and description
        self.title_label = QLabel("Organization Profile Questionnaire")
        self.title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # Scroll area for questions
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.questions_widget = QWidget()
        self.questions_layout = QFormLayout()
        self.questions_widget.setLayout(self.questions_layout)
        
        scroll_area.setWidget(self.questions_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_draft_btn = QPushButton("💾 Save Draft")
        self.save_draft_btn.clicked.connect(self.save_draft)
        button_layout.addWidget(self.save_draft_btn)
        
        self.load_draft_btn = QPushButton("📂 Load Draft")
        self.load_draft_btn.clicked.connect(self.load_draft)
        button_layout.addWidget(self.load_draft_btn)
        
        button_layout.addStretch()
        
        self.validate_btn = QPushButton("✅ Validate")
        self.validate_btn.clicked.connect(self.validate_responses)
        button_layout.addWidget(self.validate_btn)
        
        self.create_profile_btn = QPushButton("🎯 Create Profile")
        self.create_profile_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(self.create_profile_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_questionnaire(self):
        """Load the default questionnaire."""
        self.questionnaire = self.manager.get_questionnaire()
        self.response = self.manager.create_response("org_profile_v1")
        
        # Update UI
        self.title_label.setText(self.questionnaire.title)
        self.description_label.setText(self.questionnaire.description)
        
        # Create question widgets
        for question in self.questionnaire.questions:
            question_widget = QuestionWidget(question)
            question_widget.responseChanged.connect(self.on_response_changed)
            self.question_widgets[question.id] = question_widget
            self.questions_layout.addRow(question_widget)
    
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
