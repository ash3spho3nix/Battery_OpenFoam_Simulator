"""
Simple UI Loader for .ui files only.

Loads PyQt6 .ui files directly without fallback mechanisms.
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi

logger = logging.getLogger(__name__)


class UILoader:
    """
    Simple UI loader that loads .ui files directly.
    """
    
    def __init__(self, ui_base_path: str = None):
        """
        Initialize the UI loader.
        
        Args:
            ui_base_path: Base path for .ui files (default: src/resources/ui/files/)
        """
        if ui_base_path:
            self.ui_base_path = Path(ui_base_path)
        else:
            # Default path: src/resources/ui/files/
            self.ui_base_path = Path(__file__).parent.parent / "resources" / "ui" / "files"
        
        logger.info(f"UILoader initialized with path: {self.ui_base_path}")
    
    def load_ui(self, ui_name: str, parent: QWidget = None) -> QWidget:
        """
        Load a .ui file and return the widget.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            parent: Parent widget (optional)
            
        Returns:
            Loaded widget
            
        Raises:
            FileNotFoundError: If .ui file doesn't exist
            Exception: If loading fails
        """
        # Add .ui extension if not present
        if not ui_name.endswith('.ui'):
            ui_name = f"{ui_name}.ui"
        
        ui_path = self.ui_base_path / ui_name
        
        # Check if file exists
        if not ui_path.exists():
            error_msg = f"UI file not found: {ui_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Load the UI file
            logger.info(f"Loading UI file: {ui_path}")
            widget = loadUi(str(ui_path), parent)
            
            if widget is None:
                raise Exception(f"Failed to load UI file: {ui_path}")
            
            logger.info(f"Successfully loaded UI: {ui_name}")
            return widget
            
        except Exception as e:
            logger.error(f"Error loading UI file {ui_path}: {e}", exc_info=True)
            raise
    
    def get_ui_path(self, ui_name: str) -> Path:
        """
        Get the full path to a .ui file.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            
        Returns:
            Full path to the .ui file
        """
        if not ui_name.endswith('.ui'):
            ui_name = f"{ui_name}.ui"
        
        return self.ui_base_path / ui_name
