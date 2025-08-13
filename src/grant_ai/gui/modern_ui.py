"""
Modernized Material Design Main Window for Grant-AI
"""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from grant_ai.gui.material_theme import MaterialStyles, MaterialTheme
from grant_ai.gui.qt_app import MainWindow


class MaterialCard(QFrame):
    """A Material Design card component"""

    def __init__(self, title: str = "", content_widget: QWidget = None,
                 elevation: str = "level_1"):
        super().__init__()

        # Apply Material Design card styling
        self.setStyleSheet(MaterialStyles.get_card_style(elevation))
        self.setFrameShape(QFrame.NoFrame)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setFont(MaterialTheme.get_font('title_medium'))
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {MaterialTheme.COLORS['on_surface']};
                    font-weight: 500;
                    margin-bottom: 8px;
                }}
            """)
            layout.addWidget(title_label)

        # Add content widget if provided
        if content_widget:
            layout.addWidget(content_widget)


class MaterialButton(QPushButton):
    """A Material Design button component"""

    def __init__(self, text: str, variant: str = "filled", icon: str = None):
        super().__init__(text)

        # Apply Material Design button styling
        self.setStyleSheet(MaterialStyles.get_button_style(variant))
        self.setCursor(Qt.PointingHandCursor)

        # Set font
        self.setFont(MaterialTheme.get_font('label_large'))

        # Add icon if provided
        if icon:
            self.setIcon(QIcon(icon))


class MaterialNavigationRail(QFrame):
    """A Material Design navigation rail for the sidebar"""

    def __init__(self):
        super().__init__()

        # Style the navigation rail
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {MaterialTheme.COLORS['surface']};
                border-right: 1px solid {MaterialTheme.COLORS['outline']};
                min-width: 80px;
                max-width: 80px;
            }}
        """)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(8)

        # Add navigation items
        self.nav_items = []
        self.create_nav_items(layout)

    def create_nav_items(self, layout):
        """Create navigation items"""
        nav_data = [
            ("🏠", "Dashboard", "dashboard"),
            ("🔍", "Search", "search"),
            ("🤖", "AI Writing", "ai_writing"),
            ("📊", "Analytics", "analytics"),
            ("🏢", "Organizations", "organizations"),
            ("📝", "Applications", "applications"),
            ("⚙️", "Settings", "settings"),
        ]

        for icon, tooltip, action in nav_data:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(64, 64)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 16px;
                    font-size: 24px;
                    color: {MaterialTheme.COLORS['on_surface_variant']};
                }}
                QPushButton:hover {{
                    background-color: {MaterialTheme.COLORS['hover']};
                    color: {MaterialTheme.COLORS['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {MaterialTheme.COLORS['pressed']};
                }}
            """)

            layout.addWidget(btn)
            self.nav_items.append((btn, action))

        # Add stretch at the bottom
        layout.addStretch()


class MaterialStatusBar(QStatusBar):
    """A Material Design status bar"""

    def __init__(self):
        super().__init__()

        # Style the status bar
        self.setStyleSheet(f"""
            QStatusBar {{
                background-color: {MaterialTheme.COLORS['surface_variant']};
                color: {MaterialTheme.COLORS['on_surface_variant']};
                border-top: 1px solid {MaterialTheme.COLORS['outline']};
                padding: 4px 8px;
            }}
        """)

        # Set font
        self.setFont(MaterialTheme.get_font('body_small'))

        # Add initial message
        self.showMessage("Ready")


class MaterialTabWidget(QTabWidget):
    """A Material Design tab widget"""

    def __init__(self):
        super().__init__()

        # Apply Material Design tab styling
        self.setStyleSheet(MaterialStyles.get_tab_style())

        # Set font for tabs
        self.setFont(MaterialTheme.get_font('label_large'))


class ModernGrantResearchWindow(QMainWindow):
    """Modern Material Design main window for Grant Research AI"""

    def __init__(self):
        super().__init__()

        # Initialize the original app logic
        self.grant_app = MainWindow()

        self.init_ui()
        self.setup_menu_bar()
        self.setup_tool_bar()
        self.setup_status_bar()
        self.setup_system_tray()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Grant Research AI - Modern Interface")
        self.setGeometry(100, 100, 1400, 900)

        # Set window icon
        self.setWindowIcon(QIcon("icons/app_icon.png"))

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create navigation rail
        self.nav_rail = MaterialNavigationRail()
        main_layout.addWidget(self.nav_rail)

        # Create main content area
        self.create_main_content(main_layout)

        # Connect navigation signals
        self.connect_navigation()

    def create_main_content(self, main_layout):
        """Create the main content area"""
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # Add header
        self.create_header(content_layout)

        # Create tab widget for main content
        self.tab_widget = MaterialTabWidget()
        content_layout.addWidget(self.tab_widget)

        # Add tabs from original app
        self.add_modernized_tabs()

        main_layout.addWidget(content_widget)

    def create_header(self, layout):
        """Create the header area"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {MaterialTheme.COLORS['primary']};
                color: {MaterialTheme.COLORS['on_primary']};
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 8px;
            }}
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 16, 16, 16)

        # Title and subtitle
        title_layout = QVBoxLayout()

        title_label = QLabel("Grant Research AI")
        title_label.setFont(MaterialTheme.get_font('headline_medium'))
        title_label.setStyleSheet(f"color: {MaterialTheme.COLORS['on_primary']};")

        subtitle_label = QLabel("Empowering nonprofits with intelligent grant discovery")
        subtitle_label.setFont(MaterialTheme.get_font('body_large'))
        subtitle_label.setStyleSheet(f"""
            color: {MaterialTheme.COLORS['on_primary']};
            opacity: 0.8;
        """)

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Quick action buttons
        self.create_quick_actions(header_layout)

        layout.addWidget(header_frame)

    def create_quick_actions(self, layout):
        """Create quick action buttons in the header"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        # New Search button
        new_search_btn = MaterialButton("🔍 New Search", "filled")
        new_search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MaterialTheme.COLORS['on_primary']};
                color: {MaterialTheme.COLORS['primary']};
                border: none;
                border-radius: 20px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {MaterialTheme.COLORS['surface']};
            }}
        """)

        # Analytics button
        analytics_btn = MaterialButton("📊 Analytics", "outlined")
        analytics_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {MaterialTheme.COLORS['on_primary']};
                border: 1px solid {MaterialTheme.COLORS['on_primary']};
                border-radius: 20px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {MaterialTheme.COLORS['on_primary']}20;
            }}
        """)

        actions_layout.addWidget(new_search_btn)
        actions_layout.addWidget(analytics_btn)

        layout.addLayout(actions_layout)

    def add_modernized_tabs(self):
        """Add modernized versions of the original tabs"""
        # Get tabs from the original app
        if hasattr(self.grant_app, 'tab_widget'):
            original_tabs = self.grant_app.tab_widget

            # Copy tabs to the new modern interface
            for i in range(original_tabs.count()):
                tab_widget = original_tabs.widget(i)
                tab_text = original_tabs.tabText(i)

                # Wrap in a material card
                card = MaterialCard(content_widget=tab_widget)

                # Add to new tab widget
                self.tab_widget.addTab(card, tab_text)
        else:
            # Create placeholder tabs if original app not ready
            self.create_placeholder_tabs()

    def create_placeholder_tabs(self):
        """Create placeholder tabs for demo"""
        # Dashboard tab
        dashboard_content = QLabel("Dashboard content will be displayed here")
        dashboard_card = MaterialCard("Dashboard Overview", dashboard_content)
        self.tab_widget.addTab(dashboard_card, "🏠 Dashboard")

        # Search tab
        search_content = QLabel("Grant search interface will be displayed here")
        search_card = MaterialCard("Grant Search", search_content)
        self.tab_widget.addTab(search_card, "🔍 Search Grants")

        # AI Writing tab
        try:
            from .ai_writing_widget import AIWritingAssistantWidget
            from .material_theme import MaterialTheme
            ai_writing_widget = AIWritingAssistantWidget(MaterialTheme())
            self.tab_widget.addTab(ai_writing_widget, "🤖 AI Writing")
        except ImportError:
            ai_writing_content = QLabel("AI Writing Assistant requires additional setup")
            ai_writing_card = MaterialCard("AI Writing Assistant", ai_writing_content)
            self.tab_widget.addTab(ai_writing_card, "🤖 AI Writing")

        # Analytics tab
        analytics_content = QLabel("Analytics and reports will be displayed here")
        analytics_card = MaterialCard("Analytics Dashboard", analytics_content)
        self.tab_widget.addTab(analytics_card, "📊 Analytics")

        # Organizations tab
        orgs_content = QLabel("Organization profiles will be displayed here")
        orgs_card = MaterialCard("Organization Management", orgs_content)
        self.tab_widget.addTab(orgs_card, "🏢 Organizations")

    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {MaterialTheme.COLORS['surface']};
                color: {MaterialTheme.COLORS['on_surface']};
                border-bottom: 1px solid {MaterialTheme.COLORS['outline']};
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {MaterialTheme.COLORS['hover']};
            }}
        """)

        # File menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New Search', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)

        open_action = QAction('Open Profile', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        dashboard_action = QAction('Dashboard', self)
        view_menu.addAction(dashboard_action)

        analytics_action = QAction('Analytics', self)
        view_menu.addAction(analytics_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_tool_bar(self):
        """Setup the tool bar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {MaterialTheme.COLORS['surface_variant']};
                border-bottom: 1px solid {MaterialTheme.COLORS['outline']};
                spacing: 8px;
                padding: 4px;
            }}
            QToolButton {{
                border: none;
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }}
            QToolButton:hover {{
                background-color: {MaterialTheme.COLORS['hover']};
            }}
        """)

        # Add toolbar actions
        new_action = toolbar.addAction("🔍", lambda: self.tab_widget.setCurrentIndex(1))
        new_action.setToolTip("New Search")

        analytics_action = toolbar.addAction("📊", lambda: self.tab_widget.setCurrentIndex(2))
        analytics_action.setToolTip("Analytics")

        settings_action = toolbar.addAction("⚙️", self.show_settings)
        settings_action.setToolTip("Settings")

        self.addToolBar(toolbar)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = MaterialStatusBar()
        self.setStatusBar(self.status_bar)

    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon("icons/app_icon.png"))

            # Create tray menu
            tray_menu = QMenu()

            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show)

            tray_menu.addSeparator()

            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(QApplication.quit)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def connect_navigation(self):
        """Connect navigation rail signals"""
        for btn, action in self.nav_rail.nav_items:
            if action == "dashboard":
                btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(0))
            elif action == "search":
                btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(1))
            elif action == "analytics":
                btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
            elif action == "organizations":
                btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(3))
            elif action == "settings":
                btn.clicked.connect(self.show_settings)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Grant Research AI",
                         "Grant Research AI v2.0\n\n"
                         "Empowering nonprofits with intelligent grant discovery\n"
                         "Built with Material Design 3.0")

    def show_settings(self):
        """Show settings dialog"""
        # Placeholder for settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")


def create_modern_app():
    """Create and run the modern Grant Research AI application"""
    # Create application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Apply Material Design theme
    MaterialTheme.apply_material_palette(app)
    app.setFont(MaterialTheme.get_font('body_medium'))

    # Create and show main window
    window = ModernGrantResearchWindow()
    window.show()

    return app, window


if __name__ == "__main__":
    app, window = create_modern_app()
    sys.exit(app.exec_())
