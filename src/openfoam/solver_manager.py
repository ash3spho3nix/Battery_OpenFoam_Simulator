"""
OpenFOAM Solver Manager for Battery Simulator.

This module provides the OpenFOAMSolverManager class, which manages
OpenFOAM solver execution, compilation, and process control.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal

from .process_controller import ProcessController
from src.core.constants import SOLVER_NAMES, ERROR_MESSAGES, SUCCESS_MESSAGES


class OpenFOAMSolverManager(QObject):
    """
    Manager for OpenFOAM solver operations.
    
    Handles solver compilation, execution, and process control
    for different simulation modules.
    """
    
    # Signals for solver events
    solver_started = pyqtSignal()
    solver_finished = pyqtSignal(int)  # exit code
    solver_output = pyqtSignal(str)
    solver_error = pyqtSignal(str)
    
    def __init__(self, solver_path: str, solver_name: str, parent=None):
        """
        Initialize the solver manager.
        
        Args:
            solver_path: Path to the solver directory
            solver_name: Name of the solver to use
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.solver_path = solver_path
        self.solver_name = solver_name
        self.project_path = None  # Add missing project_path attribute
        self.process_controller = ProcessController(self)
        
        # Connect process controller signals
        self.process_controller.output_received.connect(self.solver_output.emit)
        self.process_controller.error_received.connect(self.solver_error.emit)
        self.process_controller.process_started.connect(self.solver_started.emit)
        self.process_controller.process_finished.connect(self.solver_finished.emit)
        
    def compile_solver(self) -> bool:
        """
        Compile the OpenFOAM solver.
        
        Returns:
            bool: True if compilation successful
        """
        try:
            # Clean previous build
            clean_cmd = f"cd {self.solver_path} && wclean"
            self.solver_output.emit(f"Running: {clean_cmd}")
            
            self.process_controller.start_process(clean_cmd)
            
            # Wait for clean to complete
            while self.process_controller.is_running():
                time.sleep(0.1)
                
            # Compile solver
            compile_cmd = f"cd {self.solver_path} && wmake"
            self.solver_output.emit(f"Running: {compile_cmd}")
            
            self.process_controller.start_process(compile_cmd)
            
            # Wait for compilation to complete
            while self.process_controller.is_running():
                time.sleep(0.1)
                
            exit_code = self.process_controller.get_exit_code()
            
            if exit_code == 0:
                self.solver_output.emit(SUCCESS_MESSAGES["solver_built"])
                return True
            else:
                self.solver_error.emit(f"Solver compilation failed with exit code: {exit_code}")
                return False
                
        except Exception as e:
            self.solver_error.emit(f"Error compiling solver: {str(e)}")
            return False
            
    def run_simulation(self, case_path: str):
        """
        Run the OpenFOAM simulation.
        
        Args:
            case_path: Path to the case directory
        """
        try:
            # Change to case directory and run solver
            run_cmd = f"cd {case_path} && {self.solver_name}"
            self.solver_output.emit(f"Running: {run_cmd}")
            
            self.process_controller.start_process(run_cmd, working_dir=case_path)
            
            self.solver_started.emit()
            
        except Exception as e:
            self.solver_error.emit(f"Error starting simulation: {str(e)}")
            
    def stop_simulation(self):
        """Stop the running simulation."""
        self.process_controller.terminate_process()
        
    def pause_simulation(self):
        """Pause the running simulation."""
        self.process_controller.send_signal(19)  # SIGSTOP
        
    def resume_simulation(self):
        """Resume the paused simulation."""
        self.process_controller.send_signal(18)  # SIGCONT
        
    def is_running(self) -> bool:
        """
        Check if simulation is running.
        
        Returns:
            bool: True if simulation is running
        """
        return self.process_controller.is_running()
        
    def get_solver_path(self) -> str:
        """
        Get the solver path.
        
        Returns:
            str: Path to the solver directory
        """
        return self.solver_path
        
    def get_solver_name(self) -> str:
        """
        Get the solver name.
        
        Returns:
            str: Name of the solver
        """
        return self.solver_name
        
    def get_solver_executable(self) -> str:
        """
        Get the full path to the solver executable.
        
        Returns:
            str: Path to the solver executable
        """
        # Construct the path to the compiled solver executable
        # OpenFOAM typically places executables in platform-specific directories
        platform_dir = "platforms/linux64GccDPInt32Opt/bin"
        executable_path = os.path.join(self.solver_path, platform_dir, self.solver_name)
        
        # On Windows, add .exe extension
        if sys.platform == "win32":
            executable_path += ".exe"
            
        return executable_path
        
    def check_solver_ready(self) -> bool:
        """
        Check if the solver is compiled and ready to run.
        
        Returns:
            bool: True if solver is ready
        """
        executable_path = self.get_solver_executable()
        
        # Check if executable exists and is executable
        if os.path.exists(executable_path) and os.access(executable_path, os.X_OK):
            return True
            
        # Try to compile the solver if it's not ready
        self.solver_output.emit("Solver not ready, attempting to compile...")
        return self.compile_solver()
        
    def build_solver(self) -> bool:
        """
        Build the OpenFOAM solver.
        
        Returns:
            bool: True if build successful
        """
        return self.compile_solver()
        
    def get_openfoam_info(self) -> Dict[str, Any]:
        """
        Get information about the OpenFOAM installation.
        
        Returns:
            dict: OpenFOAM installation information
        """
        info = {
            'installation_path': None,
            'version': None,
            'solver_path': self.solver_path,
            'solver_name': self.solver_name,
            'executable_exists': False,
            'executable_path': None
        }
        
        # Check for OpenFOAM environment variables
        wm_project_dir = os.environ.get('WM_PROJECT_DIR')
        if wm_project_dir:
            info['installation_path'] = wm_project_dir
            
            # Try to determine version from directory name
            version_match = os.path.basename(wm_project_dir)
            if version_match:
                info['version'] = version_match
                
        # Check if solver executable exists
        executable_path = self.get_solver_executable()
        info['executable_path'] = executable_path
        info['executable_exists'] = os.path.exists(executable_path)
        
        return info
        
    def set_project_path(self, project_path: str):
        """
        Set the project path for the solver.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def get_project_path(self) -> Optional[str]:
        """
        Get the project path.
        
        Returns:
            str or None: Project path if set
        """
        return self.project_path
        
    def cleanup(self):
        """Clean up resources."""
        self.process_controller.cleanup()
