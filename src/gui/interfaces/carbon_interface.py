"""
Carbon Interface for SPM - Simplified with MSYS2 integration.
"""

import os
import logging
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal

from src.gui.ui_loader import UILoader
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager

logger = logging.getLogger(__name__)


class CarbonInterface(QDialog):
    """Carbon/SPM interface with MSYS2 OpenFOAM execution."""
    
    exit_signal = pyqtSignal()
    
    def __init__(self, parent=None, ui_config=None):
        super().__init__(parent)
        
        # Load UI
        ui_loader = UILoader()
        ui_loader.load_ui("carboninterface", self)
        
        # Initialize components
        self.process_controller = ProcessController()
        self.solver_manager = OpenFOAMSolverManager()
        
        # Project paths
        self.project_path = None
        self.project_name = None
        self.case_path = None
        
        # Connect signals
        self._connect_signals()
        
        logger.info("CarbonInterface initialized")
    
    def set_project_paths(self, project_path: str, project_name: str):
        """Set project paths - case is at project root now."""
        self.project_path = project_path
        self.project_name = project_name
        self.case_path = project_path  # Template already copied to project root
        
        self.solver_manager.set_case_path(self.case_path)
        self.solver_manager.set_solver("SPMFoam")
        
        logger.info(f"Project paths set: {self.case_path}")
    
    def _connect_signals(self):
        """Connect UI signals."""
        # Back button
        if hasattr(self, 'c_back_Button'):
            self.c_back_Button.clicked.connect(self._on_back_clicked)
        
        # Geometry
        if hasattr(self, 'run_geometry_button'):
            self.run_geometry_button.clicked.connect(self._on_run_geometry)
        
        # Control
        if hasattr(self, 'run_button'):
            self.run_button.clicked.connect(self._on_run_simulation)
        
        # Process signals
        self.process_controller.output_received.connect(self._on_process_output)
        self.process_controller.error_received.connect(self._on_process_error)
        self.process_controller.process_finished.connect(self._on_process_finished)
        
        logger.info("Signals connected")
    
    def _on_back_clicked(self):
        """Handle back button."""
        logger.info("Back clicked")
        self.exit_signal.emit()
        self.close()
    
    def _on_run_geometry(self):
        """Run blockMesh."""
        try:
            if not self.case_path:
                QMessageBox.warning(self, "Error", "Project path not set")
                return
            
            command = self.solver_manager.get_block_mesh_command()
            self._append_terminal(f"Running: {command}")
            self.process_controller.start_process(command, self.case_path)
            
        except Exception as e:
            logger.error(f"Error running blockMesh: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed: {e}")
    
    def _on_run_simulation(self):
        """Run complete SPM workflow."""
        try:
            if not self.case_path:
                QMessageBox.warning(self, "Error", "Project path not set")
                return
            
            if not self.solver_manager.validate_case():
                QMessageBox.warning(self, "Error", "Run geometry setup first")
                return
            
            # Run workflow: blockMesh → topoSet → splitMeshRegions → SPMFoam
            self._run_workflow()
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed: {e}")
    
    def _run_workflow(self):
        """Run SPM workflow steps."""
        self._append_terminal("Starting SPM workflow...")
        
        # Step 1: blockMesh
        command = self.solver_manager.get_block_mesh_command()
        self._append_terminal(f"Step 1: {command}")
        self.process_controller.start_process(command, self.case_path)
    
    def _on_process_output(self, output: str):
        """Handle process output."""
        self._append_terminal(output)
    
    def _on_process_error(self, error: str):
        """Handle process error."""
        self._append_terminal(f"ERROR: {error}")
    
    def _on_process_finished(self, exit_code: int):
        """Handle process completion."""
        if exit_code == 0:
            self._append_terminal("✓ Command completed")
        else:
            self._append_terminal(f"✗ Command failed (code: {exit_code})")
    
    def _append_terminal(self, text: str):
        """Append text to terminal."""
        if hasattr(self, 'terminal_output_window'):
            self.terminal_output_window.append(text)
