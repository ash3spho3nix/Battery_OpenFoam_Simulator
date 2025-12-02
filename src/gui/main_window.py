"""
Main window implementation for Battery Simulator.

This module contains the MainWindow class, which is the Python equivalent
of the C++ MainWindow class. It manages the overall application state,
project creation, and navigation between different interfaces.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QMessageBox, QFileDialog, QLineEdit, 
    QRadioButton, QFrame, QTextBrowser
)
import logging

# Set up logging
logger = logging.getLogger(__name__)

from ..core.constants import (
    APP_NAME, APP_VERSION, SUPPORTED_MODULES, DEFAULT_PROJECT_PATH,
    ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES
)
from ..core.project_manager import ProjectManager


class MainWindow(QMainWindow):
    """
    Main application window for Battery Simulator.
    
    This class is the Python equivalent of the C++ MainWindow class.
    It manages project creation, opening, and navigation between interfaces.
    Supports both .ui file loading and hand-coded widget approaches.
    """
    
    # Class variables to store project state (equivalent to C++ static members)
    project_path: Optional[str] = None
    project_name: Optional[str] = None
    
    def __init__(self, parent: Optional[QWidget] = None, ui_config: Optional['UIConfig'] = None):
        """
        Initialize the main application window.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        logger.debug("MainWindow.__init__() called")
        super().__init__(parent)
        
        # Store UI configuration
        self.ui_config = ui_config or self._get_ui_config()
        
        # Set window properties
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 640)
        self.setMaximumSize(800, 640)
        
        # Initialize project state
        self.project_path = None
        self.project_name = None
        
        # Initialize interfaces
        self.carbon_interface = None
        self.halfcell_interface = None
        self.fullcell_interface = None
        self.current_interface = None
        
        # Initialize UI
        self._setup_ui()
        
        # Initialize project manager
        self.project_manager = ProjectManager()
        
    def _get_ui_config(self):
        """Lazy import of UIConfig to avoid circular imports."""
        logger.debug("MainWindow._get_ui_config() called")
        from ..gui.ui_config import UIConfig
        logger.debug("UIConfig imported successfully")
        return UIConfig()
        
    def _setup_ui(self):
        """
        Set up the main application UI.
        
        Creates the tabbed interface with "New" and "Open" tabs,
        similar to the C++ implementation.
        """
        logger.debug("MainWindow._setup_ui() called")
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setCurrentIndex(0)
        
        # Create tabs
        self._create_new_project_tab()
        self._create_open_project_tab()
        
        main_layout.addWidget(self.tab_widget)
        
    def _create_new_project_tab(self):
        """
        Create the "New" project tab.
        
        Contains project creation interface with module selection.
        """
        logger.debug("MainWindow._create_new_project_tab() called")
        new_tab = QWidget()
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Create a new project")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Path selection
        path_layout = QHBoxLayout()
        self.main_path_label = QLabel("Choose a folder to save your project files")
        self.main_path_button = QPushButton("Choose")
        self.main_path_button.clicked.connect(self.on_main_path_button_clicked)
        
        path_layout.addWidget(self.main_path_label)
        path_layout.addWidget(self.main_path_button)
        layout.addLayout(path_layout)
        
        # Project name
        name_layout = QHBoxLayout()
        name_label = QLabel("Enter your project name")
        self.pro_name_editline = QLineEdit("project1")
        self.main_name_hint = QPushButton("?")
        self.main_name_hint.clicked.connect(self.on_main_name_hint_clicked)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.pro_name_editline)
        name_layout.addWidget(self.main_name_hint)
        layout.addLayout(name_layout)
        
        # Module selection
        module_label = QLabel("Select a module")
        layout.addWidget(module_label)
        
        # Radio buttons for modules
        self.carbon_button = QRadioButton("Single Particle Model")
        self.halfcell_button = QRadioButton("P2D Model (Half Cell)")
        self.fullcell_button = QRadioButton("P2D Model (Full Cell)")
        
        # Set default selection
        self.carbon_button.setChecked(True)
        
        layout.addWidget(self.carbon_button)
        layout.addWidget(self.halfcell_button)
        layout.addWidget(self.fullcell_button)
        
        # Next button
        self.main_next_button = QPushButton("Next")
        self.main_next_button.setEnabled(False)
        self.main_next_button.clicked.connect(self.on_main_next_button_clicked)
        
        layout.addWidget(self.main_next_button)
        layout.addStretch()
        
        new_tab.setLayout(layout)
        self.tab_widget.addTab(new_tab, "New")
        
    def _create_open_project_tab(self):
        """
        Create the "Open" project tab.
        
        Contains project opening interface with recent projects.
        """
        logger.debug("MainWindow._create_open_project_tab() called")
        open_tab = QWidget()
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Open a project")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Path selection
        path_layout = QHBoxLayout()
        path_label = QLabel("Choose a project folder to open")
        self.main_path_label_2 = QLabel("Please choose...")
        self.main_path_button_2 = QPushButton("Choose")
        self.main_path_button_2.clicked.connect(self.on_main_path_button_2_clicked)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.main_path_label_2)
        path_layout.addWidget(self.main_path_button_2)
        layout.addLayout(path_layout)
        
        # Recent projects
        recent_label = QLabel("Open the last used project")
        layout.addWidget(recent_label)
        
        self.recent_path_label = QLabel("Last used...")
        self.recent_path_button = QPushButton("Open")
        self.recent_path_button.clicked.connect(self.on_recent_path_button_clicked)
        
        recent_layout = QHBoxLayout()
        recent_layout.addWidget(self.recent_path_label)
        recent_layout.addWidget(self.recent_path_button)
        layout.addLayout(recent_layout)
        
        # Next button
        self.main_next_button_2 = QPushButton("Next")
        self.main_next_button_2.setEnabled(False)
        self.main_next_button_2.clicked.connect(self.on_main_next_button_2_clicked)
        
        layout.addWidget(self.main_next_button_2)
        layout.addStretch()
        
        open_tab.setLayout(layout)
        self.tab_widget.addTab(open_tab, "Open")
        
    def on_main_path_button_clicked(self):
        """
        Handle path selection for new project.
        
        Opens file dialog to select project directory.
        """
        logger.debug("MainWindow.on_main_path_button_clicked() called")
        project_path = QFileDialog.getExistingDirectory(
            self, "Choose a position", DEFAULT_PROJECT_PATH
        )
        
        if project_path:
            self.project_path = project_path
            self.main_path_label.setText(project_path)
            
            # Enable next button if path is valid
            if self.main_path_label.text():
                self.main_next_button.setEnabled(True)
                self.main_next_button_2.setEnabled(False)
            else:
                self.main_next_button.setEnabled(False)
                
    def on_main_next_button_clicked(self):
        """
        Handle new project creation.
        
        Validates input and creates new project with selected module.
        Uses interface factory to create appropriate interface.
        """
        logger.debug("MainWindow.on_main_next_button_clicked() called")
        logger.debug(f"Project name: {self.pro_name_editline.text().strip()}")
        logger.debug(f"Project path: {self.project_path}")
        
        self.project_name = self.pro_name_editline.text().strip()
        
        if not self.project_name:
            logger.warning("Project name is empty")
            QMessageBox.information(self, "Hint", ERROR_MESSAGES["invalid_name"])
            return
            
        if not self.project_path:
            logger.warning("Project path is empty")
            QMessageBox.information(self, "Hint", ERROR_MESSAGES["invalid_path"])
            return
            
        # Create complete project path
        complete_project_path = os.path.join(self.project_path, self.project_name)
        logger.debug(f"Complete project path: {complete_project_path}")
        
        # Check if project already exists
        if os.path.exists(complete_project_path):
            logger.warning(f"Project already exists: {complete_project_path}")
            QMessageBox.warning(
                self, "BatteryFOAM", 
                ERROR_MESSAGES["name_exists"]
            )
            return
            
        # Determine selected module
        if self.carbon_button.isChecked():
            module = "SPM"
        elif self.halfcell_button.isChecked():
            module = "halfCell"
        elif self.fullcell_button.isChecked():
            module = "fullCell"
        else:
            logger.warning("No module selected")
            QMessageBox.warning(self, "Error", "Please select a module")
            return
            
        logger.info(f"Creating project: {self.project_name} with module: {module}")
            
        try:
            # Create project
            logger.debug("Calling project_manager.create_project()")
            self.project_manager.create_project(
                self.project_path, self.project_name, module
            )
            logger.debug("Project created successfully")
            
            # Hide main window and show appropriate interface
            logger.debug("Hiding main window")
            self.hide()
            
            # Use interface factory to create the appropriate interface
            logger.debug("Getting interface type")
            interface_type = self._get_interface_type(module)
            logger.debug(f"Interface type: {interface_type}")
            
            logger.debug("Getting interface factory")
            interface_factory = self._get_interface_factory()
            
            logger.debug(f"Creating interface with type: {interface_type}, parent: {self}, ui_config: {self.ui_config}")
            self.current_interface = interface_factory.create_interface(
                interface_type, self, self.ui_config
            )
            logger.debug(f"Interface created: {self.current_interface}")
            
            if self.current_interface:
                logger.debug(f"Interface type: {type(self.current_interface)}")
                logger.debug(f"Interface parent: {self.current_interface.parent()}")
                logger.debug(f"Interface geometry: {self.current_interface.geometry()}")
                
                logger.debug("Showing interface")
                self.current_interface.show()
                logger.debug("Interface shown")
                
                # Connect exit signal if available
                if hasattr(self.current_interface, 'exit_signal'):
                    logger.debug("Connecting exit signal")
                    self.current_interface.exit_signal.connect(self.show)
                    logger.debug("Exit signal connected")
                else:
                    logger.debug("No exit signal available")
            else:
                logger.error("Interface creation returned None!")
                
        except Exception as e:
            logger.error(f"Failed to create project: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")
            
    def on_main_name_hint_clicked(self):
        """
        Show project name constraints hint.
        """
        logger.debug("MainWindow.on_main_name_hint_clicked() called")
        QMessageBox.information(
            self, "Hint", 
            "Only supports upper&lower case letter, number and underscore\n"
            "Once confirmed, do not change the name arbitrarily"
        )
        
    def on_main_path_button_2_clicked(self):
        """
        Handle path selection for opening existing project.
        """
        logger.debug("MainWindow.on_main_path_button_2_clicked() called")
        project_path = QFileDialog.getExistingDirectory(
            self, "Choose a project", DEFAULT_PROJECT_PATH
        )
        
        if project_path:
            self.project_path = project_path
            self.main_path_label_2.setText(project_path)
            
            # Extract project name from path
            self.project_name = os.path.basename(project_path)
            
            # Update recent path
            self.recent_path_label.setText(os.path.join(self.project_path, self.project_name))
            
            # Enable next button
            self.main_next_button.setEnabled(False)
            self.main_next_button_2.setEnabled(True)
            
    def on_recent_path_button_clicked(self):
        """
        Open the most recently used project.
        """
        logger.debug("MainWindow.on_recent_path_button_clicked() called")
        recent_file_path = Path(__file__).parent.parent / "resources" / "most_recent_file"
        
        if recent_file_path.exists():
            with open(recent_file_path, 'r') as f:
                recent_path = f.read().strip()
                
            if recent_path:
                self.recent_path_label.setText(recent_path)
                
                # Extract project name and path
                self.project_name = os.path.basename(recent_path)
                self.project_path = os.path.dirname(recent_path)
                
                self.main_next_button.setEnabled(False)
                self.main_next_button_2.setEnabled(True)
                
    def on_main_next_button_2_clicked(self):
        """
        Handle opening existing project.
        Uses interface factory to create appropriate interface.
        """
        logger.debug("MainWindow.on_main_next_button_2_clicked() called")
        if not self.project_path or not self.project_name:
            logger.warning("Project path or name is empty")
            QMessageBox.information(self, "Hint", ERROR_MESSAGES["invalid_path"])
            return
            
        # Save recent project
        logger.debug("Saving recent project")
        recent_file_path = Path(__file__).parent.parent / "resources" / "most_recent_file"
        recent_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(recent_file_path, 'w') as f:
            f.write(os.path.join(self.project_path, self.project_name))
            
        # Determine which module to open
        logger.debug("Detecting module type")
        project_dir = os.path.join(self.project_path, self.project_name)
        
        if os.path.exists(os.path.join(project_dir, "SPMFoam")):
            module = "SPM"
        elif os.path.exists(os.path.join(project_dir, "halfCellFoam")):
            module = "halfCell"
        elif os.path.exists(os.path.join(project_dir, "fullCellFoam")):
            module = "fullCell"
        else:
            logger.warning("Invalid project structure")
            QMessageBox.information(self, "Hint", "The folder you chose is invalid.")
            return
            
        logger.info(f"Opening project: {self.project_name} with module: {module}")
            
        # Hide main window and show appropriate interface
        logger.debug("Hiding main window")
        self.hide()
        
        # Use interface factory to create the appropriate interface
        logger.debug("Creating interface for existing project")
        interface_type = self._get_interface_type(module)
        interface_factory = self._get_interface_factory()
        self.current_interface = interface_factory.create_interface(
            interface_type, self, self.ui_config
        )
        
        if self.current_interface:
            logger.debug(f"Interface created: {self.current_interface}")
            logger.debug(f"Interface type: {type(self.current_interface)}")
            
            logger.debug("Showing interface")
            self.current_interface.show()
            
            # Connect exit signal if available
            if hasattr(self.current_interface, 'exit_signal'):
                logger.debug("Connecting exit signal")
                self.current_interface.exit_signal.connect(self.show)
                
            # Clear labels
            self.recent_path_label.clear()
            self.main_path_label_2.clear()
        else:
            logger.error("Interface creation for existing project returned None!")
            
    def _get_interface_type(self, module: str) -> str:
        """
        Get the interface type for a module.
        
        Args:
            module: Module name (SPM, halfCell, fullCell)
            
        Returns:
            str: Corresponding interface type
        """
        logger.debug(f"MainWindow._get_interface_type() called with module: {module}")
        interface_map = {
            "SPM": "carbon",
            "halfCell": "halfcell", 
            "fullCell": "fullcell"
        }
        result = interface_map.get(module, "carbon")
        logger.debug(f"MainWindow._get_interface_type() returning: {result}")
        return result
        
    def _get_interface_factory(self):
        """Lazy import of InterfaceFactory to avoid circular imports."""
        logger.debug("MainWindow._get_interface_factory() called")
        from ..gui.interface_factory import InterfaceFactory
        logger.debug("InterfaceFactory imported successfully")
        return InterfaceFactory
