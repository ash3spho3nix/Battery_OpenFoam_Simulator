#!/usr/bin/env python3
"""
Main window implementation for Battery Simulator.

This module contains the MainWindow class, which loads the main application
window from mainwindow.ui and connects its signals to the appropriate handlers.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QMainWindow, QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from src.gui.ui_config import UIConfig

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
            ui_config: UI configuration for loading mode (supports all modes)
        """
        logger.debug("MainWindow.__init__() called")
        super().__init__(parent)
        
        # Store UI configuration
        self.ui_config = ui_config or self._get_ui_config()
        
        # Initialize properties
        self.project_path: Optional[str] = None
        self.project_name: Optional[str] = None
        self.current_interface: Optional[QWidget] = None
        
        # Initialize ProjectManager for project creation
        try:
            from src.core.project_manager_enhanced import EnhancedProjectManager
            self.project_manager = EnhancedProjectManager()
            logger.info("Enhanced ProjectManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ProjectManager: {e}")
            self.project_manager = None
        
        # Set window properties
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 640)
        self.setMaximumSize(800, 640)
        
        # Load UI based on configuration
        self._load_main_window_ui()
        
        # Connect UI signals to handlers
        self._connect_signals()
        
        logger.info("MainWindow initialized successfully")
        
    def _get_ui_config(self):
        """Lazy import of UIConfig to avoid circular imports."""
        logger.debug("MainWindow._get_ui_config() called")
        from ..gui.ui_config import UIConfig
        logger.debug("UIConfig imported successfully")
        return UIConfig()
        
    def _load_main_window_ui(self):
        """Load the main window UI based on configuration mode."""
        logger.debug(f"Loading MainWindow UI with mode: {self.ui_config.mode.name}")
        
        try:
            if self.ui_config.mode.name == 'UI_FILES':
                # Load from .ui file
                from ..gui.ui_loader_enhanced import EnhancedUiLoader
                EnhancedUiLoader.load_ui("mainwindow", self)
                logger.debug("Successfully loaded mainwindow.ui")
            elif self.ui_config.mode.name == 'HAND_CODED':
                # Create hand-coded UI
                self._create_hand_coded_ui()
                logger.debug("Successfully created hand-coded UI")
            else:  # AUTO_DETECT
                # Try .ui file first, fallback to hand-coded
                try:
                    from ..gui.ui_loader_enhanced import EnhancedUiLoader
                    EnhancedUiLoader.load_ui("mainwindow", self)
                    logger.debug("Successfully loaded mainwindow.ui (AUTO_DETECT)")
                except Exception as e:
                    logger.warning(f"Failed to load .ui file, falling back to hand-coded: {e}")
                    self._create_hand_coded_ui()
        except Exception as e:
            logger.error(f"Error loading main window UI: {e}", exc_info=True)
            raise

    def _create_hand_coded_ui(self):
        """Create hand-coded UI as fallback."""
        logger.debug("Creating hand-coded MainWindow UI")
        
        # This is a placeholder for hand-coded UI creation
        # In a real implementation, this would create all widgets programmatically
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add basic widgets
        title_label = QLabel("Battery Simulator - Main Window")
        layout.addWidget(title_label)
        
        # Store references to widgets that will be accessed later
        self.pro_name_editline = None  # Will be set when needed
        self.main_path_label = None    # Will be set when needed
        self.main_path_button = None   # Will be set when needed
        self.main_next_button = None   # Will be set when needed
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        logger.debug("Hand-coded MainWindow UI created")

    def _connect_signals(self):
        """Connect all UI signals to their corresponding slots."""
        logger.debug("Connecting MainWindow signals")
        
        try:
            # New Project Tab
            if hasattr(self, 'main_path_button') and self.main_path_button:
                self.main_path_button.clicked.connect(self._on_choose_path_clicked)
            else:
                logger.warning("main_path_button not found, cannot connect signal")
                
            if hasattr(self, 'main_next_button') and self.main_next_button:
                self.main_next_button.clicked.connect(self._on_next_button_clicked)
            else:
                logger.warning("main_next_button not found, cannot connect signal")
            
            # Enable 'Next' button only when path and name are set
            if hasattr(self, 'pro_name_editline') and self.pro_name_editline:
                self.pro_name_editline.textChanged.connect(self._update_next_button_state)
            else:
                logger.warning("pro_name_editline not found, cannot connect signal")
                
            # Open Project Tab
            if hasattr(self, 'main_path_button_2') and self.main_path_button_2:
                self.main_path_button_2.clicked.connect(self._on_open_project_clicked)
            else:
                logger.warning("main_path_button_2 not found, cannot connect signal")
                
        except Exception as e:
            logger.error(f"Error connecting signals: {e}", exc_info=True)
            raise

    def _update_next_button_state(self):
        """Enable or disable the 'Next' button based on input."""
        try:
            has_name = bool(self.pro_name_editline.text().strip())
            has_path = self.project_path is not None
            if hasattr(self, 'main_next_button') and self.main_next_button:
                self.main_next_button.setEnabled(has_name and has_path)
        except Exception as e:
            logger.error(f"Error updating next button state: {e}")

    @safe_slot
    def _on_choose_path_clicked(self, _=False):
<<<<<<< Updated upstream
        """Handle path selection button click with exception handling."""
=======
        """Handle path selection button click."""
>>>>>>> Stashed changes
        try:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Project Directory",
                str(Path.home()),
                QFileDialog.Option.ShowDirsOnly
            )
            
            if folder:
                self.project_path = folder
<<<<<<< Updated upstream
                self.main_path_label.setText(folder)
                logger.info(f"Selected project path: {folder}")
                self._update_next_button_state()
        except Exception as e:
            logger.error(f"Error selecting project path: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to select path: {str(e)}")

    @safe_slot
    def _on_next_button_clicked(self, _=False):
        """Handle project creation 'Next' button click with validation."""
=======
                if hasattr(self, 'main_path_label') and self.main_path_label:
                    self.main_path_label.setText(folder)
                logger.info(f"Selected project path: {folder}")
                self._update_next_button_state()
        except Exception as e:
            logger.error(f"Error in choose path clicked: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to choose path: {e}")

    @safe_slot
    def _on_next_button_clicked(self, _=False):
        """Handle project creation 'Next' button click."""
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            logger.error(f"Error in next button click: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")
=======
            logger.error(f"Error in next button clicked: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
>>>>>>> Stashed changes

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
        try:
            logger.info(f"Opening interface for module: {module_type}")
            
            # Create interface based on module type
            if module_type == "SPM" or module_type == "carbon":
                from src.gui.interfaces.carbon_interface import CarbonInterface
                interface = CarbonInterface(self, self.ui_config)
                self.carbon_interface = interface
                
            elif module_type == "halfCell":
                from src.gui.interfaces.halfcell_interface import HalfCellInterface
                interface = HalfCellInterface(self, self.ui_config)
                self.halfcell_interface = interface
                
            elif module_type == "fullCell":
                from src.gui.interfaces.fullcell_interface import FullCellInterface
                interface = FullCellInterface(self, self.ui_config)
                self.fullcell_interface = interface
            else:
                raise ValueError(f"Unknown module type: {module_type}")
                
            # Set project paths
            interface.set_project_paths(project_path, project_name)
            
            # Store current interface
            self.current_interface = interface
            
            # Show interface
            interface.show()
            self.hide()
            
            # Connect back signal
            interface.exit_signal.connect(self._on_interface_exit)
            
            logger.info("Interface opened successfully")
            
        except Exception as e:
            logger.error(f"Failed to open interface: {e}")
            raise

    @safe_slot
    def _on_open_project_clicked(self, _=False):
<<<<<<< Updated upstream
        """Handle 'Open' project button click with exception handling."""
=======
        """Handle 'Open' project button click."""
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            QMessageBox.critical(self, "Error", f"Failed to open project: {str(e)}")
=======
            QMessageBox.critical(self, "Error", f"Failed to open project: {e}")
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
=======
            
>>>>>>> Stashed changes
            # Hide current interface
            if self.current_interface:
                self.current_interface.close()  # Use close() to ensure proper cleanup
                self.current_interface = None

            # Show main window
            self.show()
            logger.info("Returned to main window")
        except Exception as e:
            logger.error(f"Error handling interface exit: {e}", exc_info=True)
<<<<<<< Updated upstream
            QMessageBox.critical(self, "Error", f"Failed to return to main window: {str(e)}")
            # Still try to show the main window even if cleanup failed
            self.show()
=======
            QMessageBox.critical(self, "Error", f"Failed to return to main window: {e}")

    @safe_slot
    def _on_interface_error(self, error_message: str):
        """Handle interface error signal."""
        try:
            logger.error(f"Interface error: {error_message}")
            QMessageBox.critical(self, "Interface Error", error_message)
        except Exception as e:
            logger.error(f"Error handling interface error: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            logger.info("MainWindow close event triggered")
            
            # Clean up current interface
            if self.current_interface:
                try:
                    # Disconnect signals
                    if hasattr(self.current_interface, 'exit_signal'):
                        self.current_interface.exit_signal.disconnect(self._on_interface_exit)
                    if hasattr(self.current_interface, 'error_signal'):
                        self.current_interface.error_signal.disconnect(self._on_interface_error)
                    
                    # Close interface
                    self.current_interface.close()
                    self.current_interface = None
                except Exception as e:
                    logger.warning(f"Error cleaning up interface: {e}")
            
            # Accept the close event
            event.accept()
            logger.info("MainWindow closed successfully")
            
        except Exception as e:
            logger.error(f"Error in closeEvent: {e}", exc_info=True)
            event.accept()  # Still close the window even if cleanup fails

    def get_project_info(self) -> Dict[str, Optional[str]]:
        """Get current project information."""
        return {
            'project_path': self.project_path,
            'project_name': self.project_name
        }
>>>>>>> Stashed changes
