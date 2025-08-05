"""
Material Design Theme System for Grant-AI GUI
Provides modern, consistent styling across all components
"""
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import QApplication


class MaterialTheme:
    """Material Design 3.0 inspired theme for Grant-AI"""

    # Material Design Color Palette
    COLORS = {
        # Primary Colors (Grant-AI Blue-Green Theme)
        'primary': '#1976D2',           # Deep Blue
        'primary_variant': '#1565C0',   # Darker Blue
        'primary_light': '#42A5F5',     # Light Blue
        'secondary': '#00BCD4',         # Cyan
        'secondary_variant': '#0097A7',  # Dark Cyan
        'secondary_light': '#4DD0E1',   # Light Cyan

        # Surface Colors
        'background': '#FAFAFA',        # Light Gray Background
        'surface': '#FFFFFF',           # White Surface
        'surface_variant': '#F5F5F5',   # Light Gray Surface
        'elevated_surface': '#FFFFFF',  # Elevated White

        # Text Colors
        'on_primary': '#FFFFFF',        # White on Primary
        'on_secondary': '#FFFFFF',      # White on Secondary
        'on_background': '#212121',     # Dark on Background
        'on_surface': '#212121',        # Dark on Surface
        'on_surface_variant': '#757575',  # Medium Gray

        # State Colors
        'error': '#F44336',             # Red
        'warning': '#FF9800',           # Orange
        'success': '#4CAF50',           # Green
        'info': '#2196F3',              # Blue

        # Outline Colors
        'outline': '#E0E0E0',           # Light Gray Outline
        'outline_variant': '#BDBDBD',   # Medium Gray Outline

        # Interactive States
        'hover': '#E3F2FD',             # Light Blue Hover
        'pressed': '#BBDEFB',           # Medium Blue Pressed
        'focus': '#2196F3',             # Blue Focus
        'disabled': '#9E9E9E',          # Gray Disabled
    }

    # Typography Scale
    TYPOGRAPHY = {
        'headline_large': {'size': 32, 'weight': 'normal'},
        'headline_medium': {'size': 28, 'weight': 'normal'},
        'headline_small': {'size': 24, 'weight': 'normal'},
        'title_large': {'size': 22, 'weight': 'medium'},
        'title_medium': {'size': 16, 'weight': 'medium'},
        'title_small': {'size': 14, 'weight': 'medium'},
        'body_large': {'size': 16, 'weight': 'normal'},
        'body_medium': {'size': 14, 'weight': 'normal'},
        'body_small': {'size': 12, 'weight': 'normal'},
        'label_large': {'size': 14, 'weight': 'medium'},
        'label_medium': {'size': 12, 'weight': 'medium'},
        'label_small': {'size': 11, 'weight': 'medium'},
    }

    # Elevation Shadows
    ELEVATIONS = {
        'level_0': 'none',
        'level_1': ('0px 1px 3px rgba(0,0,0,0.12), '
                    '0px 1px 2px rgba(0,0,0,0.24)'),
        'level_2': ('0px 3px 6px rgba(0,0,0,0.16), '
                    '0px 3px 6px rgba(0,0,0,0.23)'),
        'level_3': ('0px 10px 20px rgba(0,0,0,0.19), '
                    '0px 6px 6px rgba(0,0,0,0.23)'),
        'level_4': ('0px 14px 28px rgba(0,0,0,0.25), '
                    '0px 10px 10px rgba(0,0,0,0.22)'),
        'level_5': ('0px 19px 38px rgba(0,0,0,0.30), '
                    '0px 15px 12px rgba(0,0,0,0.22)'),
    }

    @staticmethod
    def get_font(typography_scale: str) -> QFont:
        """Get a QFont for the specified typography scale"""
        if typography_scale not in MaterialTheme.TYPOGRAPHY:
            typography_scale = 'body_medium'

        config = MaterialTheme.TYPOGRAPHY[typography_scale]
        font = QFont("Roboto", config['size'])

        if config['weight'] == 'medium':
            font.setWeight(QFont.Medium)
        elif config['weight'] == 'bold':
            font.setWeight(QFont.Bold)
        else:
            font.setWeight(QFont.Normal)

        return font

    @staticmethod
    def get_color(color_name: str) -> str:
        """Get hex color value for the specified color name"""
        return MaterialTheme.COLORS.get(color_name, '#000000')

    @staticmethod
    def apply_material_palette(app: QApplication):
        """Apply Material Design color palette to the application"""
        palette = QPalette()

        # Window colors
        bg_color = QColor(MaterialTheme.COLORS['background'])
        palette.setColor(QPalette.Window, bg_color)

        text_color = QColor(MaterialTheme.COLORS['on_background'])
        palette.setColor(QPalette.WindowText, text_color)

        # Base colors (input fields)
        surface_color = QColor(MaterialTheme.COLORS['surface'])
        palette.setColor(QPalette.Base, surface_color)

        variant_color = QColor(MaterialTheme.COLORS['surface_variant'])
        palette.setColor(QPalette.AlternateBase, variant_color)

        on_surface_color = QColor(MaterialTheme.COLORS['on_surface'])
        palette.setColor(QPalette.Text, on_surface_color)

        # Button colors
        primary_color = QColor(MaterialTheme.COLORS['primary'])
        palette.setColor(QPalette.Button, primary_color)

        on_primary_color = QColor(MaterialTheme.COLORS['on_primary'])
        palette.setColor(QPalette.ButtonText, on_primary_color)

        # Highlight colors
        secondary_color = QColor(MaterialTheme.COLORS['secondary'])
        palette.setColor(QPalette.Highlight, secondary_color)

        on_secondary_color = QColor(MaterialTheme.COLORS['on_secondary'])
        palette.setColor(QPalette.HighlightedText, on_secondary_color)

        app.setPalette(palette)

class MaterialStyles:
    """Pre-defined Material Design component styles"""

    @staticmethod
    def get_card_style(elevation: str = 'level_1') -> str:
        """Get CSS style for a Material Design card"""
        shadow = MaterialTheme.ELEVATIONS.get(elevation, MaterialTheme.ELEVATIONS['level_1'])
        return f"""
            QFrame {{
                background-color: {MaterialTheme.COLORS['surface']};
                border: none;
                border-radius: 12px;
                padding: 16px;
                margin: 8px;
                {f'box-shadow: {shadow};' if shadow != 'none' else ''}
            }}
        """

    @staticmethod
    def get_button_style(variant: str = 'filled') -> str:
        """Get CSS style for Material Design buttons"""
        if variant == 'filled':
            return f"""
                QPushButton {{
                    background-color: {MaterialTheme.COLORS['primary']};
                    color: {MaterialTheme.COLORS['on_primary']};
                    border: none;
                    border-radius: 20px;
                    padding: 10px 24px;
                    font-weight: 500;
                    font-size: 14px;
                    min-height: 40px;
                }}
                QPushButton:hover {{
                    background-color: {MaterialTheme.COLORS['primary_variant']};
                }}
                QPushButton:pressed {{
                    background-color: {MaterialTheme.COLORS['primary_variant']};
                }}
                QPushButton:disabled {{
                    background-color: {MaterialTheme.COLORS['disabled']};
                    color: {MaterialTheme.COLORS['on_surface_variant']};
                }}
            """
        elif variant == 'outlined':
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {MaterialTheme.COLORS['primary']};
                    border: 1px solid {MaterialTheme.COLORS['outline']};
                    border-radius: 20px;
                    padding: 10px 24px;
                    font-weight: 500;
                    font-size: 14px;
                    min-height: 40px;
                }}
                QPushButton:hover {{
                    background-color: {MaterialTheme.COLORS['hover']};
                    border-color: {MaterialTheme.COLORS['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {MaterialTheme.COLORS['pressed']};
                }}
            """
        elif variant == 'text':
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {MaterialTheme.COLORS['primary']};
                    border: none;
                    border-radius: 20px;
                    padding: 10px 24px;
                    font-weight: 500;
                    font-size: 14px;
                    min-height: 40px;
                }}
                QPushButton:hover {{
                    background-color: {MaterialTheme.COLORS['hover']};
                }}
                QPushButton:pressed {{
                    background-color: {MaterialTheme.COLORS['pressed']};
                }}
            """
        return ""

    @staticmethod
    def get_input_style() -> str:
        """Get CSS style for Material Design input fields"""
        return f"""
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {MaterialTheme.COLORS['surface']};
                color: {MaterialTheme.COLORS['on_surface']};
                border: 1px solid {MaterialTheme.COLORS['outline']};
                border-radius: 4px;
                padding: 12px 16px;
                font-size: 16px;
                selection-background-color: {MaterialTheme.COLORS['secondary_light']};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid {MaterialTheme.COLORS['primary']};
                outline: none;
            }}
            QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
                border-color: {MaterialTheme.COLORS['on_surface_variant']};
            }}
        """

    @staticmethod
    def get_table_style() -> str:
        """Get CSS style for Material Design tables"""
        return f"""
            QTableWidget {{
                background-color: {MaterialTheme.COLORS['surface']};
                alternate-background-color: {MaterialTheme.COLORS['surface_variant']};
                selection-background-color: {MaterialTheme.COLORS['secondary_light']};
                gridline-color: {MaterialTheme.COLORS['outline']};
                border: 1px solid {MaterialTheme.COLORS['outline']};
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {MaterialTheme.COLORS['outline']};
            }}
            QTableWidget::item:selected {{
                background-color: {MaterialTheme.COLORS['secondary_light']};
                color: {MaterialTheme.COLORS['on_secondary']};
            }}
            QHeaderView::section {{
                background-color: {MaterialTheme.COLORS['primary']};
                color: {MaterialTheme.COLORS['on_primary']};
                padding: 12px;
                border: none;
                font-weight: 500;
            }}
        """

    @staticmethod
    def get_tab_style() -> str:
        """Get CSS style for Material Design tabs"""
        return f"""
            QTabWidget::pane {{
                background-color: {MaterialTheme.COLORS['surface']};
                border: 1px solid {MaterialTheme.COLORS['outline']};
                border-radius: 8px;
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background-color: {MaterialTheme.COLORS['surface_variant']};
                color: {MaterialTheme.COLORS['on_surface_variant']};
                border: none;
                padding: 12px 24px;
                margin: 2px;
                border-radius: 4px 4px 0px 0px;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background-color: {MaterialTheme.COLORS['primary']};
                color: {MaterialTheme.COLORS['on_primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {MaterialTheme.COLORS['hover']};
            }}
        """

    @staticmethod
    def get_progress_style() -> str:
        """Get CSS style for Material Design progress bars"""
        return f"""
            QProgressBar {{
                background-color: {MaterialTheme.COLORS['surface_variant']};
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {MaterialTheme.COLORS['primary']};
                border-radius: 4px;
            }}
        """

    @staticmethod
    def get_status_style(status_type: str = 'info') -> str:
        """Get CSS style for status indicators"""
        color_map = {
            'success': MaterialTheme.COLORS['success'],
            'error': MaterialTheme.COLORS['error'],
            'warning': MaterialTheme.COLORS['warning'],
            'info': MaterialTheme.COLORS['info'],
        }

        color = color_map.get(status_type, MaterialTheme.COLORS['info'])
        return f"""
            QLabel {{
                background-color: {color}20;
                color: {color};
                border: 1px solid {color};
                border-radius: 16px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 12px;
            }}
        """

class MaterialComponents:
    """Helper methods to create Material Design components"""

    @staticmethod
    def create_material_app() -> QApplication:
        """Create a QApplication with Material Design styling applied"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Apply Material Design palette
        MaterialTheme.apply_material_palette(app)

        # Set default font
        app.setFont(MaterialTheme.get_font('body_medium'))

        return app
