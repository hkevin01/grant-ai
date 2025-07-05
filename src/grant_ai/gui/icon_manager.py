"""
Icon Manager for the Grant AI GUI Application.
Provides consistent icon handling with emoji and text fallbacks.
"""

import logging
import sys
from typing import Optional

from PyQt5.QtWidgets import QLabel, QPushButton

logger = logging.getLogger(__name__)


class IconManager:
    """Manages icons and emoji for the GUI application with fallbacks."""
    
    # Icon definitions with emoji and text fallbacks
    ICONS = {
        # Search and discovery
        'search': ('🔍', 'Search'),
        'filter': ('🔽', 'Filter'),
        'find': ('🔎', 'Find'),
        
        # Actions
        'add': ('➕', 'Add'),
        'remove': ('➖', 'Remove'),
        'delete': ('🗑️', 'Delete'),
        'edit': ('✏️', 'Edit'),
        'save': ('💾', 'Save'),
        'load': ('📂', 'Load'),
        'refresh': ('🔄', 'Refresh'),
        'copy': ('📋', 'Copy'),
        'export': ('📤', 'Export'),
        'import': ('📥', 'Import'),
        
        # View and display
        'view': ('👁️', 'View'),
        'details': ('📋', 'Details'),
        'preview': ('👀', 'Preview'),
        'expand': ('⬇️', 'Expand'),
        'collapse': ('⬆️', 'Collapse'),
        
        # Status and states
        'success': ('✅', 'Success'),
        'error': ('❌', 'Error'),
        'warning': ('⚠️', 'Warning'),
        'info': ('ℹ️', 'Info'),
        'pending': ('⏳', 'Pending'),
        'complete': ('✅', 'Complete'),
        'in_progress': ('⚙️', 'In Progress'),
        'draft': ('📝', 'Draft'),
        
        # Documents and files
        'document': ('📄', 'Document'),
        'documents': ('📄', 'Documents'),
        'file': ('📁', 'File'),
        'folder': ('📂', 'Folder'),
        'pdf': ('📕', 'PDF'),
        'excel': ('📊', 'Excel'),
        'word': ('📘', 'Word'),
        
        # Organizations and grants
        'organization': ('🏢', 'Organization'),
        'grant': ('💰', 'Grant'),
        'funding': ('💵', 'Funding'),
        'award': ('🏆', 'Award'),
        'application': ('📋', 'Application'),
        
        # Reports and analytics
        'report': ('📊', 'Report'),
        'analytics': ('📈', 'Analytics'),
        'chart': ('📊', 'Chart'),
        'stats': ('📊', 'Stats'),
        'metrics': ('📊', 'Metrics'),
        
        # Navigation
        'home': ('🏠', 'Home'),
        'back': ('⬅️', 'Back'),
        'forward': ('➡️', 'Forward'),
        'up': ('⬆️', 'Up'),
        'down': ('⬇️', 'Down'),
        
        # Time and scheduling
        'calendar': ('📅', 'Calendar'),
        'clock': ('🕒', 'Clock'),
        'deadline': ('⏰', 'Deadline'),
        'overdue': ('⚠️', 'Overdue'),
        
        # Communication
        'email': ('📧', 'Email'),
        'phone': ('📞', 'Phone'),
        'contact': ('👤', 'Contact'),
        'note': ('📝', 'Note'),
        'comment': ('💬', 'Comment'),
        
        # System
        'settings': ('⚙️', 'Settings'),
        'help': ('❓', 'Help'),
        'close': ('❌', 'Close'),
        'minimize': ('➖', 'Minimize'),
        'maximize': ('⬆️', 'Maximize'),
    }
    
    def __init__(self):
        """Initialize the icon manager."""
        self.emoji_support = self._test_emoji_support()
        self.use_emoji = self.emoji_support
        logger.info(
            f"Icon Manager initialized - Emoji support: {self.emoji_support}"
        )
    
    def _test_emoji_support(self) -> bool:
        """Test if the system supports emoji rendering in Qt."""
        try:
            # Check if we're on a system that typically has emoji issues
            if sys.platform.startswith('linux'):
                # Linux systems may have limited emoji support
                return False
            elif sys.platform == 'darwin':
                # macOS typically has good emoji support
                return True
            elif sys.platform.startswith('win'):
                # Windows 10+ has decent emoji support
                return True
            else:
                # Unknown platform, assume no emoji support
                return False
                
        except Exception as e:
            logger.warning(f"Error testing emoji support: {e}")
            return False
    
    def get_icon_text(self, icon_name: str, include_text: bool = False) -> str:
        """
        Get the icon text for a given icon name.
        
        Args:
            icon_name: Name of the icon
            include_text: Whether to include text fallback alongside emoji
            
        Returns:
            String containing emoji and/or text
        """
        if icon_name not in self.ICONS:
            logger.warning(f"Unknown icon name: {icon_name}")
            return icon_name
        
        emoji, text = self.ICONS[icon_name]
        
        if self.use_emoji and not include_text:
            return emoji
        elif self.use_emoji and include_text:
            return f"{emoji} {text}"
        else:
            return text
    
    def get_button_text(self, icon_name: str, label: str = None) -> str:
        """
        Get text for a button with icon.
        
        Args:
            icon_name: Name of the icon
            label: Additional label text
            
        Returns:
            Formatted button text
        """
        icon_text = self.get_icon_text(icon_name)
        
        if label:
            return f"{icon_text} {label}"
        else:
            # If no label provided, include text fallback
            return self.get_icon_text(icon_name, include_text=True)
    
    def set_button_icon(
        self, button: QPushButton, icon_name: str, text: Optional[str] = None
    ):
        """
        Set icon and text for a QPushButton.
        
        Args:
            button: The button to modify
            icon_name: Name of the icon
            text: Button text (if None, uses icon text)
        """
        if text is None:
            button_text = self.get_icon_text(icon_name, include_text=True)
        else:
            icon_text = self.get_icon_text(icon_name)
            button_text = f"{icon_text} {text}"
        
        button.setText(button_text)
        
        # Set tooltip with text fallback for accessibility
        if icon_name in self.ICONS:
            _, fallback_text = self.ICONS[icon_name]
            button.setToolTip(fallback_text)
    
    def set_label_icon(
        self, label: QLabel, icon_name: str, text: Optional[str] = None
    ):
        """
        Set icon and text for a QLabel.
        
        Args:
            label: The label to modify
            icon_name: Name of the icon
            text: Label text (if None, uses icon text)
        """
        if text is None:
            label_text = self.get_icon_text(icon_name, include_text=True)
        else:
            icon_text = self.get_icon_text(icon_name)
            label_text = f"{icon_text} {text}"
        
        label.setText(label_text)
    
    def create_button(
        self,
        icon_name: str,
        text: Optional[str] = None,
        tooltip: Optional[str] = None
    ) -> QPushButton:
        """
        Create a new QPushButton with icon.
        
        Args:
            icon_name: Name of the icon
            text: Button text
            tooltip: Button tooltip
            
        Returns:
            Configured QPushButton
        """
        button = QPushButton()
        self.set_button_icon(button, icon_name, text)
        
        if tooltip:
            button.setToolTip(tooltip)
        elif icon_name in self.ICONS:
            _, fallback_text = self.ICONS[icon_name]
            button.setToolTip(fallback_text)
        
        return button
    
    def create_label(
        self, icon_name: str, text: Optional[str] = None
    ) -> QLabel:
        """
        Create a new QLabel with icon.
        
        Args:
            icon_name: Name of the icon
            text: Label text
            
        Returns:
            Configured QLabel
        """
        label = QLabel()
        self.set_label_icon(label, icon_name, text)
        return label
    
    def toggle_emoji_mode(self, use_emoji: Optional[bool] = None):
        """
        Toggle emoji mode on/off.
        
        Args:
            use_emoji: If None, toggles current state. Otherwise sets to the
                specified value.
        """
        if use_emoji is None:
            self.use_emoji = not self.use_emoji
        else:
            self.use_emoji = use_emoji and self.emoji_support
        
        status = "enabled" if self.use_emoji else "disabled"
        logger.info("Emoji mode %s", status)
    
    def get_status_icon(self, status: str) -> str:
        """
        Get an appropriate icon for a status.
        
        Args:
            status: Status string
            
        Returns:
            Icon text for the status
        """
        status_lower = status.lower().replace('_', ' ').replace('-', ' ')
        
        # Map status keywords to icons
        status_mappings = {
            'draft': 'draft',
            'progress': 'in_progress',
            'submitted': 'export',
            'review': 'view',
            'approved': 'success',
            'rejected': 'error',
            'awarded': 'award',
            'declined': 'error',
            'withdrawn': 'remove',
            'complete': 'complete',
            'pending': 'pending',
            'overdue': 'overdue',
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
        }
        
        for keyword, icon_name in status_mappings.items():
            if keyword in status_lower:
                return self.get_icon_text(icon_name)
        
        # Default to info icon
        return self.get_icon_text('info')


# Global icon manager instance
icon_manager = IconManager()


def get_icon(icon_name: str, include_text: bool = False) -> str:
    """Convenience function to get icon text."""
    return icon_manager.get_icon_text(icon_name, include_text)


def create_icon_button(
    icon_name: str, text: Optional[str] = None, tooltip: Optional[str] = None
) -> QPushButton:
    """Convenience function to create a button with icon."""
    return icon_manager.create_button(icon_name, text, tooltip)


def create_icon_label(icon_name: str, text: Optional[str] = None) -> QLabel:
    """Convenience function to create a label with icon."""
    return icon_manager.create_label(icon_name, text)
