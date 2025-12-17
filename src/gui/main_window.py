"""
Main window implementation for Battery Simulator.

This module contains the MainWindow class, which loads the main application
window from mainwindow.ui and connects its signals to the appropriate handlers.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QMainWindow, QWidget, QFileDialog, QMessageBox
import logging

from src.utils.exception_handler import safe_slot

# Set up logging
logger = logging.getLogger(__name__)

from ..core.constants import APP_NAME, APP_VERSION


class MainWindow(QMainWindow):
    """
    Main application window for Battery Simulator.
    
    This class loads the main window from mainwindow.ui and implements
    all the logic for project creation and management.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, ui_config: Optional['UIConfig'] = None):
        """
        Initialize the main application window.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode (must be UI_FILES)
        """
        logger.debug("MainWindow.__init__() called")
        super().__init__(parent)
        
        # Store UI configuration
        self.ui_config = ui_config or self._get_ui_config()

        # Initialize properties
        self.project_path: Optional[str] = None
        self.project_name: Optional[str] = None
        self.current_interface: Optional[QWidget] = None
        self.project_manager = None # This should be initialized if needed
        
        # Validate that we're in UI_FILES mode
        if self.ui_config.mode.value != 'ui_files':
            error_msg = f"MainWindow requires UI_FILES mode, but got {self.ui_config.mode.value}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Set window properties
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 640)
        self.setMaximumSize(800, 640)
        
        # Load UI directly from mainwindow.ui
        self._load_main_window_ui()

        # Connect UI signals to handlers
        self._connect_signals()
        
    def _get_ui_config(self):
        """Lazy import of UIConfig to avoid circular imports."""
        logger.debug("MainWindow._get_ui_config() called")
        from ..gui.ui_config import UIConfig
        logger.debug("UIConfig imported successfully")
        return UIConfig()
        
    def _load_main_window_ui(self):
        """Load the main window UI directly from mainwindow.ui."""
        logger.debug("MainWindow._load_main_window_ui() called")
        
        # Import UiLoader
        from ..gui.ui_loader import UiLoader
        
        # Load mainwindow.ui
        try:
            # loadUi populates the 'self' instance with the UI from the file.
            # It also sets the central widget defined in the .ui file automatically.
            UiLoader.load_ui("mainwindow", self)
            logger.debug("Successfully loaded mainwindow.ui into MainWindow instance")
        except Exception as e:
            logger.error(f"Error loading mainwindow.ui: {e}", exc_info=True)
            raise

    def _connect_signals(self):
        """Connect all UI signals to their corresponding slots."""
        logger.debug("Connecting MainWindow signals")
        # New Project Tab
        self.main_path_button.clicked.connect(self._on_choose_path_clicked)
        self.main_next_button.clicked.connect(self._on_next_button_clicked)
        
        # Enable 'Next' button only when path and name are set
        self.pro_name_editline.textChanged.connect(self._update_next_button_state)
#        self.main_path_label.textChanged.connect(self._update_next_button_state)

        # Open Project Tab
        self.main_path_button_2.clicked.connect(self._on_open_project_clicked)

    def _update_next_button_state(self):
        """Enable or disable the 'Next' button based on input."""
        has_name = bool(self.pro_name_editline.text().strip())
        has_path = self.project_path is not None
        self.main_next_button.setEnabled(has_name and has_path)

    @safe_slot
    def _on_choose_path_clicked(self, _=False):
        """Handle path selection button click with exception handling."""
        try:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Project Directory",
                str(Path.home()),
                QFileDialog.Option.ShowDirsOnly
            )
            
            if folder:
                self.project_path = folder
                self.main_path_label.setText(folder)
                logger.info(f"Selected project path: {folder}")
                self._update_next_button_state()
        except Exception as e:
            logger.error(f"Error selecting project path: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to select path: {str(e)}")

    @safe_slot
    def _on_next_button_clicked(self, _=False):
        """Handle project creation 'Next' button click with validation."""
        try:
            # Get project name
            project_name = self.pro_name_editline.text().strip()
            
            if not project_name:
                QMessageBox.warning(self, "Warning", "Please enter a project name")
                return
                
            if not self.project_path:
                QMessageBox.warning(self, "Warning", "Please select a project path")
                return
                
            # Get selected module
            selected_module = None
            if hasattr(self, 'carbon_button') and self.carbon_button.isChecked():
                selected_module = "SPM"
            elif hasattr(self, 'halfCell_button') and self.halfCell_button.isChecked():
                selected_module = "halfCell"
            elif hasattr(self, 'fullCell_button') and self.fullCell_button.isChecked():
                selected_module = "fullCell"
                
            if not selected_module:
                QMessageBox.warning(self, "Warning", "Please select a simulation module")
                return
                
            # Create project
            self._create_project(project_name, selected_module)
        except Exception as e:
            logger.error(f"Error in next button click: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")

    @safe_slot
    def _create_project(self, project_name, module_type):
        """Create a new project and open its interface."""
        try:
            logger.info(f"Creating project: {project_name}, module: {module_type}")
            
            # Create project directory
            project_full_path = Path(self.project_path) / project_name
            
            if project_full_path.exists():
                reply = QMessageBox.question(
                    self,
                    "Project Exists",
                    f"Project '{project_name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
                    
            # Use project manager to create project
            if self.project_manager:
                success = self.project_manager.create_project(
                    project_name=project_name,
                    template_name=module_type,
                    project_path=str(project_full_path.parent)
                )
                
                if not success:
                    raise Exception("Project creation failed")
            else:
                # Fallback: manual project creation
                self._create_project_manual(project_full_path, module_type)
                
            # Store project info
            self.project_name = project_name
            self.project_path = str(project_full_path)
            
            # Open appropriate interface
            self._open_interface(module_type, str(project_full_path), project_name)
            
            QMessageBox.information(self, "Success", "Project created successfully")
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")

    def _create_project_manual(self, project_path, module_type):
        """Manual project creation as fallback."""
        import shutil
        
        # Get template path
        from src.core.constants import TEMPLATES_PATH
        template_path = Path(TEMPLATES_PATH) / module_type
        
        if not template_path.exists():
            raise Exception(f"Template not found: {template_path}")
            
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Copy template
        for item in template_path.iterdir():
            if item.is_dir():
                shutil.copytree(item, project_path / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, project_path / item.name)
                
        logger.info(f"Project created manually at {project_path}")

    def _open_interface(self, module_type, project_path, project_name):
        """Open the appropriate interface for the module type."""
        # This method is now part of MainWindow, but the logic to create
        # specific interface instances (CarbonInterface, etc.) is still valid.
        # The imports are kept inside the method to avoid circular dependencies.
        from src.gui.interface_factory import InterfaceFactory
        
        interface_map = {
            "SPM": "carbon",
            "carbon": "carbon",
            "halfCell": "halfcell",
            "fullCell": "fullcell"
        }
        interface_type = interface_map.get(module_type)
        if not interface_type:
            raise ValueError(f"Unknown module type: {module_type}")

        # Use the factory to create the interface
        self.current_interface = InterfaceFactory.create_interface(interface_type, parent=self, ui_config=self.ui_config)
        
        # Show interface and hide main window
        self.current_interface.show()
        self.hide()

        # Connect the exit signal from the new interface
        if hasattr(self.current_interface, 'exit_signal'):
            self.current_interface.exit_signal.connect(self._on_interface_exit)

    @safe_slot
    def _on_open_project_clicked(self, _=False):
        """Handle 'Open' project button click with exception handling."""
        try:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Project Folder",
                str(Path.home()),
                QFileDialog.Option.ShowDirsOnly
            )

            if not folder:
                return

            # Detect module type from project structure
            project_path = Path(folder)
            module_type = self._detect_project_type(project_path)

            if not module_type:
                QMessageBox.warning(
                    self,
                    "Invalid Project",
                    "Could not detect project type. Please select a valid project folder."
                )
                return

            # Open interface
            self._open_interface(module_type, str(project_path), project_path.name)
        except Exception as e:
            logger.error(f"Error opening project: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to open project: {str(e)}")

    def _detect_project_type(self, project_path: Path) -> Optional[str]:
        """Detect project type from directory structure."""
        # This is a simplified check. A more robust implementation might
        # look for specific file contents or a project metadata file.

        # Check for SPM
        if (project_path / "SPMFoam").exists() or (project_path / "Case" / "constant" / "ele").exists():
            return "SPM"

        # Check for HalfCell
        if (project_path / "halfCellFoam").exists() or (project_path / "Case" / "constant" / "WE").exists():
            return "halfCell"

        # Check for FullCell
        if (project_path / "fullCellFoam").exists() or (project_path / "Case" / "constant" / "anode").exists():
            return "fullCell"

        return None

    @safe_slot
    def _on_interface_exit(self):
        """Handle interface exit signal to show the main window again."""
        try:
            logger.info("Interface exit signal received, returning to main window.")
            # Hide current interface
            if self.current_interface:
                self.current_interface.close()  # Use close() to ensure proper cleanup
                self.current_interface = None

            # Show main window
            self.show()
            logger.info("Returned to main window")
        except Exception as e:
            logger.error(f"Error handling interface exit: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to return to main window: {str(e)}")
            # Still try to show the main window even if cleanup failed
            self.show()