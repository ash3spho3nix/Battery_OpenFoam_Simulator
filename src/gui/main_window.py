"""
Main application window for Battery Simulator.

This module contains the MainWindow class which is the entry point for the GUI application.
It handles project creation, interface navigation, and application lifecycle.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtCore import pyqtSignal, QObject

# Import UI loading components
from src.gui.ui_loader import UILoader
from src.gui.ui_config import UIConfig

# Import core components
from src.core.project_manager import ProjectManager
from src.core.config import DEFAULT_PROJECT_PATH, get_user_config

# Import interface factory
from src.gui.interface_factory import InterfaceFactory

# Import utility functions
#from src.utils.file_operations import ensure_directory_exists

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for Battery Simulator.
    
    Handles project creation, interface navigation, and application lifecycle.
    """
    
    def __init__(self, ui_config: Optional[UIConfig] = None):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize project manager with default project path
        self.project_manager = ProjectManager(DEFAULT_PROJECT_PATH)
        
        # Initialize user config
        self.user_config = get_user_config()
        
        # Initialize UI components
        self.ui_loader = UILoader()
        self.ui_config = ui_config or UIConfig()
        
        # Current interface state
        self.current_interface = None
        self.project_path = None
        self.project_name = None
        self.selected_module_type = None  # Initialize selected module type
        
        # Mapping from UI button names to template names
        self.module_to_template_map = {
            "carbon": "SPM",
            "halfCell": "halfCell", 
            "fullCell": "fullCell"
        }
        
        # Load main window UI
        self._load_main_window_ui()
        
        # Pre-fill project path from user config
        self._prefill_project_path()
        
        # Connect signals
        self._connect_signals()
        
        # Set window properties
        self.setWindowTitle("Battery Simulator")
        self.resize(800, 600)
        
        logger.info("MainWindow initialized")
    
    def _load_main_window_ui(self):
        """Load the main window UI."""
        try:
            # Load main window UI
            main_window_ui = self.ui_loader.load_ui("mainwindow")
            if main_window_ui:
                self.setCentralWidget(main_window_ui)
                logger.info("Main window UI loaded successfully")
            else:
                logger.error("Failed to load main window UI")
                 
        except Exception as e:
            logger.error(f"Error loading main window UI: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load UI: {e}")
    
    def _prefill_project_path(self):
        """Pre-fill the project path from user configuration."""
        try:
            last_path = self.user_config.get_last_project_path()
            main_window_ui = self.centralWidget()
            if hasattr(main_window_ui, 'main_path_label'):
                main_window_ui.main_path_label.setText(last_path)
                logger.info(f"Pre-filled project path: {last_path}")
        except Exception as e:
            logger.error(f"Error pre-filling project path: {e}")
              
    def _connect_signals(self):
        """Connect UI signals to slots."""
        try:
            # Get UI components
            main_window_ui = self.centralWidget()
             
            # Connect radio button signals for module selection
            if hasattr(main_window_ui, 'carbon_button'):
                main_window_ui.carbon_button.toggled.connect(
                    lambda checked: self._on_module_selected("carbon", checked)
                )
             
            if hasattr(main_window_ui, 'halfCell_button'):
                main_window_ui.halfCell_button.toggled.connect(
                    lambda checked: self._on_module_selected("halfCell", checked)
                )
                 
            if hasattr(main_window_ui, 'fullCell_button'):
                main_window_ui.fullCell_button.toggled.connect(
                    lambda checked: self._on_module_selected("fullCell", checked)
                )
                 
            if hasattr(main_window_ui, 'main_next_button'):
                main_window_ui.main_next_button.clicked.connect(
                    self._on_next_button_clicked
                )
                 
            if hasattr(main_window_ui, 'main_path_button'):
                main_window_ui.main_path_button.clicked.connect(
                    self._on_browse_path_clicked
                )
                 
            logger.info("Main window signals connected")
             
        except Exception as e:
            logger.error(f"Error connecting signals: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to connect signals: {e}")
     
    def _on_module_selected(self, module_type: str, checked: bool):
        """Handle module radio button selection."""
        if checked:
            logger.info(f"Module selected: {module_type}")
            self.selected_module_type = module_type
            
            # Enable the Next button when a module is selected
            main_window_ui = self.centralWidget()
            if hasattr(main_window_ui, 'main_next_button'):
                main_window_ui.main_next_button.setEnabled(True)
     
    def _on_next_button_clicked(self):
        """Handle next button click to create project and open interface."""
        try:
            logger.info("Next button clicked")
             
            # Validate that a module is selected
            if not hasattr(self, 'selected_module_type') or not self.selected_module_type:
                QMessageBox.warning(self, "Warning", "Please select a simulation module (SPM, Half Cell, or Full Cell)")
                return
             
            # Get project information from UI
            main_window_ui = self.centralWidget()
             
            # Get project name
            project_name = ""
            if hasattr(main_window_ui, 'pro_name_editline'):
                project_name = main_window_ui.pro_name_editline.text()
             
            # Get project path
            project_path = ""
            if hasattr(main_window_ui, 'main_path_label'):
                project_path = main_window_ui.main_path_label.text()
             
            # Validate inputs
            if not project_name:
                QMessageBox.warning(self, "Warning", "Please enter a project name")
                return
                 
            if not project_path:
                QMessageBox.warning(self, "Warning", "Please select a project path")
                return
                
            # Validate that the path exists and is writable
            if not os.path.exists(project_path):
                QMessageBox.warning(self, "Warning", f"The selected path does not exist: {project_path}")
                return
                
            if not os.access(project_path, os.W_OK):
                QMessageBox.warning(self, "Warning", f"The selected path is not writable: {project_path}")
                return
             
            # Create project
            self._create_project(project_name, project_path)
             
        except Exception as e:
            logger.error(f"Error in _on_next_button_clicked: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
     
    def _create_project(self, project_name: str, project_path: str):
        """Create a new project."""
        try:
            logger.info(f"Creating project: {project_name} at {project_path}")
            logger.info(f"Selected module: {self.selected_module_type}")
            template_name = self.module_to_template_map.get(self.selected_module_type, self.selected_module_type)
            logger.info(f"Using template: {template_name}")
            logger.info(f"Project path exists: {os.path.exists(project_path)}")
            logger.info(f"Project path writable: {os.access(project_path, os.W_OK)}")
             
            # Create a project manager for the selected path
            project_manager = ProjectManager(project_path)
            
            # Use project manager to create project
            template_name = self.module_to_template_map.get(self.selected_module_type, self.selected_module_type)
            success = project_manager.create_project(
                project_name=project_name,
                template_name=template_name
            )
             
            logger.info(f"Project creation result: {success}")
            
            if success:
                logger.info("Project created successfully")
                 
                # Store project information
                self.project_name = project_name
                self.project_path = os.path.join(project_path, project_name)
                
                # Add to recent projects
                self.user_config.add_recent_project(self.project_path)
                 
                # Open the appropriate interface
                self._open_interface(self.selected_module_type)
            else:
                logger.error("Project creation failed")
                QMessageBox.critical(self, "Error", "Failed to create project")
                 
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
     
    def _open_interface(self, interface_type: str):
        """Open the specified interface."""
        try:
            logger.info(f"Opening interface: {interface_type}")
             
            # Create interface factory instance
            factory = InterfaceFactory(self.ui_config)
            
            # Create interface using factory
            interface = factory.create_interface(
                interface_type=interface_type,
                parent=self
            )
             
            if interface:
                # Set project paths
                interface.set_project_paths(self.project_path, self.project_name)
                 
                # Connect exit signal
                interface.exit_signal.connect(self._on_interface_exit)
                 
                # Show interface and hide main window
                interface.show()
                self.hide()
                
                # Store current interface
                self.current_interface = interface
                 
                logger.info(f"Interface {interface_type} opened successfully")
            else:
                logger.error(f"Failed to create interface: {interface_type}")
                QMessageBox.critical(self, "Error", f"Failed to create interface: {interface_type}")
                 
        except Exception as e:
            logger.error(f"Error opening interface: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to open interface: {e}")
     
    def _on_interface_exit(self):
        """Handle interface exit signal."""
        logger.info("Interface exit signal received")
         
        # Show main window and clean up interface
        self.show()
         
        if self.current_interface:
            self.current_interface.close()
            self.current_interface = None
     
    def _on_browse_path_clicked(self):
        """Handle browse path button click."""
        try:
            logger.info("Browse path button clicked")
             
            # Open file dialog to select directory
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Project Directory",
                DEFAULT_PROJECT_PATH
            )
             
            if directory:
                # Update path label
                main_window_ui = self.centralWidget()
                if hasattr(main_window_ui, 'main_path_label'):
                    main_window_ui.main_path_label.setText(directory)
                    
                # Save the selected path to user config
                self.user_config.set_last_project_path(directory)
                     
            logger.info(f"Selected directory: {directory}")
             
        except Exception as e:
            logger.error(f"Error in browse path: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to browse path: {e}")
     
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            logger.info("Main window close event")
             
            # Clean up resources
            if self.current_interface:
                self.current_interface.close()
                 
            # Close event
            event.accept()
             
        except Exception as e:
            logger.error(f"Error in close event: {e}", exc_info=True)
            event.accept()

def create_main_window() -> MainWindow:
    """Create and return a MainWindow instance."""
    return MainWindow()
