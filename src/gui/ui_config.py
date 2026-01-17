"""
Simple UI Configuration.

Stores UI file paths and settings.
Hardcoded to use existing .ui files only.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class UIConfig:
    """
    Simple UI configuration holder.
    Hardcoded to use .ui files only.
    """
    
    def __init__(self, ui_base_path: str = None):
        """
        Initialize UI configuration.
        
        Args:
            ui_base_path: Base path for .ui files
        """
        if ui_base_path:
            self.ui_base_path = Path(ui_base_path)
        else:
            # Default: src/resources/ui/files/
            self.ui_base_path = Path(__file__).parent.parent / "resources" / "ui" / "files"
        
        # Hardcoded to use .ui files only
        self.mode = "ui_files"
    
    def get_ui_path(self) -> str:
        """Get the UI base path as string."""
        return str(self.ui_base_path)
    
    def update_ui_path(self, new_path: str):
        """Update the UI base path."""
        self.ui_base_path = Path(new_path)
    
    def update_setting(self, key: str, value: str):
        """Update a configuration setting."""
        if key == 'ui_base_path':
            self.update_ui_path(value)
        else:
            logger.warning(f"Unknown setting: {key}")
