"""
Main window for Battery Simulator GUI.

This module contains the MainWindow class, which provides support for both
.ui file loading and hand-coded widget approaches based on configuration.
"""

import sys
import logging
from pathlib import Path

# Set up logging to help debug circular imports
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Loading main_window module")

# Add the src_py directory to Python path for imports
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Import modules using absolute imports to avoid packaging issues
from src_py.gui.ui_loader import UILoader
from src_py.gui.ui_config import UIConfig, UILoadingMode
from src_py.gui.interface_factory import InterfaceFactory
from src_py.core.application import BatterySimulatorApp

logger.debug("main_window: All imports completed successfully")


class MainWindow(QMainWindow):
    """
    Main window that supports both .ui file loading and hand-coded approaches.
    
    This class can load the main window from a .ui file or use the hand-coded
    approach based on the UI configuration. It provides automatic fallback
    capabilities for robust operation.
    """
    
    def __init__(self, parent=None, ui_config=None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        logger.debug("MainWindow.__init__() called")
        super().__init__(parent)
        
        self.ui_config = ui_config or UIConfig()
        
        # Try to load from .ui file first if configured
        if self._should_load_ui_file():
            try:
                self._load_from_ui_file()
            except Exception as e:
                print(f"Failed to load .ui file: {e}")
                if self.ui_config.should_fallback_to_hand_coded():
                    self._create_hand_coded_ui()
                else:
                    raise
        else:
            self._create_hand_coded_ui()
            
    def _should_load_ui_file(self) -> bool:
        """Determine if we should try loading from .ui file."""
        if self.ui_config.mode == UILoadingMode.UI_FILES:
            return True
        elif self.ui_config.mode == UILoadingMode.HAND_CODED:
            return False
        elif self.ui_config.mode == UILoadingMode.AUTO_DETECT:
            # Check if .ui file exists
            return UILoader.ui_file_exists("mainwindow", self.ui_config.get_ui_base_path())
        return False
        
    def _load_from_ui_file(self):
        """Load the main window from .ui file."""
        logger.debug("MainWindow._load_from_ui_file() called")
        # Load the .ui file using the interface factory
        self.ui_widget = InterfaceFactory.create_main_window(self.ui_config)
        
        # Set the loaded widget as central widget
        self.setCentralWidget(self.ui_widget)
        
        # Copy window properties if available
        if hasattr(self.ui_widget, 'windowTitle'):
            self.setWindowTitle(self.ui_widget.windowTitle())
        if hasattr(self.ui_widget, 'minimumSize'):
            self.setMinimumSize(self.ui_widget.minimumSize())
        if hasattr(self.ui_widget, 'maximumSize'):
            self.setMaximumSize(self.ui_widget.maximumSize())
        
        # Connect signals if needed
        self._connect_ui_signals()
        
    def _create_hand_coded_ui(self):
        """Create the hand-coded UI (existing implementation)."""
        logger.debug("MainWindow._create_hand_coded_ui() called")
        # Create the main application
        self.app = BatterySimulatorApp()
        
        # Set this window as the central widget
        self.setCentralWidget(self.app)
        
        # Copy window properties
        self.setWindowTitle(self.app.windowTitle())
        self.setMinimumSize(self.app.minimumSize())
        self.setMaximumSize(self.app.maximumSize())
        
    def _connect_ui_signals(self):
        """Connect signals for .ui-based interface."""
        # Connect signals from .ui file to handlers
        # This would need to be implemented based on the specific .ui file structure
        # For now, we'll leave it as a placeholder for future implementation
        
        # Example signal connections (to be implemented based on actual .ui file):
        # if hasattr(self.ui_widget, 'main_path_button'):
        #     self.ui_widget.main_path_button.clicked.connect(self._on_main_path_button_clicked)
        # if hasattr(self.ui_widget, 'main_next_button'):
        #     self.ui_widget.main_next_button.clicked.connect(self._on_main_next_button_clicked)
        pass
        
    def _on_main_path_button_clicked(self):
        """Handle main path button click (for .ui-based interface)."""
        # Implementation for .ui-based interface
        pass
        
    def _on_main_next_button_clicked(self):
        """Handle main next button click (for .ui-based interface)."""
        # Implementation for .ui-based interface
        pass
        
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Ensures proper cleanup of the application.
        """
        logger.debug("MainWindow.closeEvent() called")
        # Close any open interfaces
        if hasattr(self, 'app') and self.app:
            if hasattr(self.app, 'carbon_interface') and self.app.carbon_interface:
                self.app.carbon_interface.close()
            if hasattr(self.app, 'halfcell_interface') and self.app.halfcell_interface:
                self.app.halfcell_interface.close()
            if hasattr(self.app, 'fullcell_interface') and self.app.fullcell_interface:
                self.app.fullcell_interface.close()
                
        # Accept the close event
        event.accept()

logger.debug("main_window module loaded successfully")
