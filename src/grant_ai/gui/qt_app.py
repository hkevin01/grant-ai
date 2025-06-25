"""
PyQt5 GUI for Grant Research AI Project
"""
import json
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from grant_ai.analysis.grant_researcher import GrantResearcher
from grant_ai.core.db import SessionLocal
from grant_ai.models import Grant, OrganizationProfile
from grant_ai.models.grant import Grant as GrantModel

PROFILE_PATH = Path.home() / ".grant_ai_profile.json"
GRANTS_PATH = Path.home() / ".grant_ai_grants.json"


class GrantSearchTab(QWidget):
    def __init__(self, org_profile_tab):
        super().__init__()
        self.org_profile_tab = org_profile_tab
        layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords or filters...")
        self.focus_area_input = QLineEdit()
        self.focus_area_input.setPlaceholderText("Focus area (e.g. housing, education)")
        self.amount_min_input = QLineEdit()
        self.amount_min_input.setPlaceholderText("Min amount")
        self.amount_max_input = QLineEdit()
        self.amount_max_input.setPlaceholderText("Max amount")
        self.eligibility_input = QLineEdit()
        self.eligibility_input.setPlaceholderText("Eligibility (e.g. nonprofit)")
        self.search_btn = QPushButton("Search Grants (DB)")
        self.results_list = QListWidget()
        layout.addWidget(QLabel("Grant Search"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.focus_area_input)
        layout.addWidget(self.amount_min_input)
        layout.addWidget(self.amount_max_input)
        layout.addWidget(self.eligibility_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.results_list)
        self.setLayout(layout)
        self.search_btn.clicked.connect(self.search_grants_db)
        self.results_list.itemClicked.connect(self.show_grant_details)
        self.researcher = GrantResearcher()
        self.load_grants()

    def load_grants(self):
        if GRANTS_PATH.exists():
            with open(GRANTS_PATH, "r") as f:
                grants_data = json.load(f)
            grants = [Grant(**g) for g in grants_data]
            self.researcher.add_grants(grants)

    def search_grants_db(self):
        self.results_list.clear()
        org_profile = self.org_profile_tab.get_profile()
        if not org_profile:
            self.results_list.addItem("Please save/load an organization profile first.")
            return
        session = SessionLocal()
        query = self.search_input.text().strip()
        focus_area = self.focus_area_input.text().strip().lower()
        amount_min = self.amount_min_input.text().strip()
        amount_max = self.amount_max_input.text().strip()
        eligibility = self.eligibility_input.text().strip().lower()
        stmt = select(GrantModel)
        if query:
            stmt = stmt.where(GrantModel.title.ilike(f"%{query}%"))
        if focus_area:
            # Search in focus_areas JSON field
            stmt = stmt.where(GrantModel.focus_areas.contains(focus_area))
        if amount_min.isdigit():
            stmt = stmt.where(GrantModel.amount_min >= int(amount_min))
        if amount_max.isdigit():
            stmt = stmt.where(GrantModel.amount_max <= int(amount_max))
        if eligibility:
            # Search in eligibility_types JSON field
            stmt = stmt.where(GrantModel.eligibility_types.contains(eligibility))
        grants = session.execute(stmt).scalars().all()
        session.close()
        if not grants:
            self.results_list.addItem("No matching grants found in database.")
            return
        self.grant_map = {f"{g.title} ({g.funder_name})": g for g in grants}
        for grant in grants:
            self.results_list.addItem(f"{grant.title} ({grant.funder_name})")

    def show_grant_details(self, item):
        grant = self.grant_map.get(item.text())
        if not grant:
            return
        details = (
            f"Title: {grant.title}\n"
            f"Funder: {grant.funder_name}\n"
            f"Amount: {grant.amount_min} - {grant.amount_max}\n"
            f"Focus: {', '.join(grant.focus_areas)}\n"
            f"Eligibility: {', '.join(grant.eligibility_types)}\n"
            f"Description: {grant.description}\n"
            f"URL: {grant.application_url}"
        )
        dlg = QTextEdit(details)
        dlg.setReadOnly(True)
        dlg.setWindowTitle("Grant Details")
        dlg.resize(500, 400)
        dlg.show()
        dlg.exec_ = lambda: None  # Prevents closing the main app


class OrgProfileTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        
        # Add preset organizations dropdown
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Select Preset Organization --")
        self.preset_combo.addItem("Coda Mountain Academy")
        self.preset_combo.addItem("Custom Organization")
        self.preset_combo.currentTextChanged.connect(self.load_preset_profile)
        
        self.name_input = QLineEdit()
        self.mission_input = QTextEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["Education", "Arts", "Robotics", "Housing", "Community", "Other"])
        
        layout.addRow("Preset Organizations:", self.preset_combo)
        layout.addRow("Organization Name:", self.name_input)
        layout.addRow("Mission:", self.mission_input)
        layout.addRow("Type:", self.type_input)
        
        self.save_btn = QPushButton("Save Profile")
        self.load_btn = QPushButton("Load Profile")
        layout.addRow(self.save_btn, self.load_btn)
        
        self.setLayout(layout)
        self.save_btn.clicked.connect(self.save_profile)
        self.load_btn.clicked.connect(self.load_profile)

    def load_preset_profile(self, preset_name: str):
        """Load a preset organization profile."""
        if preset_name == "Coda Mountain Academy":
            self.load_coda_profile()
        elif preset_name == "Custom Organization":
            self.clear_form()

    def load_coda_profile(self):
        """Load Coda Mountain Academy profile."""
        coda_profile_path = (
            Path(__file__).parent.parent.parent.parent / "data" / 
            "profiles" / "coda_profile.json"
        )
        
        if coda_profile_path.exists():
            with open(coda_profile_path, "r") as f:
                data = json.load(f)
            
            self.name_input.setText(data.get("name", ""))
            self.mission_input.setPlainText(data.get("description", ""))
            
            # Set focus area based on the first focus area in the list
            focus_areas = data.get("focus_areas", [])
            if focus_areas:
                first_focus = focus_areas[0].replace("_", " ").title()
                idx = self.type_input.findText(first_focus)
                if idx >= 0:
                    self.type_input.setCurrentIndex(idx)
        else:
            # Fallback to hardcoded values if file doesn't exist
            self.name_input.setText("Coda Mountain Academy")
            self.mission_input.setPlainText(
                "Coda Mountain Academy is a non-profit organization dedicated to "
                "equipping and developing young students and their families through "
                "unique and outstanding educational opportunities. We use Arts "
                "Integration to develop exposure and opportunities that promote "
                "healthy goal setting, positive identity, strong character, "
                "resiliency, and life skills."
            )
            idx = self.type_input.findText("Education")
            if idx >= 0:
                self.type_input.setCurrentIndex(idx)

    def clear_form(self):
        """Clear the form for custom organization."""
        self.name_input.clear()
        self.mission_input.clear()
        self.type_input.setCurrentIndex(0)

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
            return
        with open(PROFILE_PATH, "w") as f:
            json.dump(profile.dict(), f, default=str)

    def load_profile(self):
        if PROFILE_PATH.exists():
            with open(PROFILE_PATH, "r") as f:
                data = json.load(f)
            self.name_input.setText(data.get("name", ""))
            self.mission_input.setPlainText(data.get("description", ""))
            idx = self.type_input.findText(data.get("focus_areas", [""])[0].capitalize())
            if idx >= 0:
                self.type_input.setCurrentIndex(idx)


class ApplicationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status_list = QListWidget()
        self.add_btn = QPushButton("Add New Application")
        layout.addWidget(QLabel("Application Tracking"))
        layout.addWidget(self.status_list)
        layout.addWidget(self.add_btn)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grant Research AI - PyQt GUI")
        self.resize(800, 600)
        tabs = QTabWidget()
        self.org_profile_tab = OrgProfileTab()
        self.grant_search_tab = GrantSearchTab(self.org_profile_tab)
        tabs.addTab(self.grant_search_tab, "Grant Search")
        tabs.addTab(self.org_profile_tab, "Organization Profile")
        tabs.addTab(ApplicationTab(), "Applications")
        self.setCentralWidget(tabs)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
