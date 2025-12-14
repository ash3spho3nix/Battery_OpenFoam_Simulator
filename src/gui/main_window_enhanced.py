"""
Enhanced Main Window with Exception Handling and Project Management.

This file contains additions and modifications to main_window.py to add:
1. Exception handling on all button clicks
2. Proper OpenFOAM integration
3. Interface creation and navigation
"""

from src.utils.exception_handler import safe_slot
import logging

logger = logging.getLogger(__name__)

# Add these methods to MainWindow class:

@safe_slot
def _on_choose_path_clicked(self):
    """Handle path selection button click."""
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

@safe_slot
def _on_next_button_clicked(self):
    """Handle project creation 'Next' button click."""
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
    elif hasattr(self, 'halfcell_button') and self.halfcell_button.isChecked():
        selected_module = "halfCell"
    elif hasattr(self, 'fullcell_button') and self.fullcell_button.isChecked():
        selected_module = "fullCell"
        
    if not selected_module:
        QMessageBox.warning(self, "Warning", "Please select a simulation module")
        return
        
    # Create project
    self._create_project(project_name, selected_module)

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
        MainWindow.project_path = str(project_full_path)
        MainWindow.project_name = project_name
        
        # Open appropriate interface
        self._open_interface(module_type, str(project_full_path), project_name)
        
        QMessageBox.information(self, "Success", "Project created successfully")
        
    except Exception as e:
        logger.error(f"Project creation failed: {e}")
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
def _on_interface_exit(self):
    """Handle interface exit signal."""
    # Hide current interface
    if self.current_interface:
        self.current_interface.hide()
        self.current_interface = None
        
    # Show main window
    self.show()
    
    logger.info("Returned to main window")

@safe_slot
def _on_open_project_clicked(self):
    """Handle 'Open' project button click."""
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

def _detect_project_type(self, project_path):
    """Detect project type from directory structure."""
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
