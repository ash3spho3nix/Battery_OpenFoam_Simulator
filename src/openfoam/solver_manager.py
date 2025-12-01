"""
OpenFOAM solver manager.

This module provides the OpenFOAMSolverManager class, which handles
solver building and execution for different simulation modules.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from .process_controller import ProcessController
from core.constants import SOLVER_NAMES, ERROR_MESSAGES, SUCCESS_MESSAGES


class OpenFOAMSolverManager:
    """
    Manager for OpenFOAM solver operations.
    
    Handles solver building (wclean, wmake) and execution for different
    simulation modules.
    """
    
    def __init__(self, project_path: str, solver_name: str):
        """
        Initialize the solver manager.
        
        Args:
            project_path: Path to the project directory
            solver_name: Name of the solver to manage
        """
        self.project_path = project_path
        self.solver_name = solver_name
        self.process_controller = ProcessController()
        
        # Connect process signals
        self.process_controller.output_received.connect(self._on_output)
        self.process_controller.error_received.connect(self._on_error)
        self.process_controller.process_finished.connect(self._on_finished)
        
    def build_solver(self) -> bool:
        """
        Build the OpenFOAM solver using wclean and wmake.
        
        Returns:
            bool: True if build successful, False otherwise
        """
        solver_path = os.path.join(self.project_path, self.solver_name)
        if not os.path.exists(solver_path):
            self._on_error(f"Solver directory not found: {solver_path}")
            return False
            
        try:
            # Change to solver directory
            old_cwd = os.getcwd()
            os.chdir(solver_path)
            
            # Clean previous build
            self._on_output("Cleaning previous build...")
            self.process_controller.start_process("wclean")
            
            # Wait for clean to complete
            while self.process_controller.is_running():
                import time
                time.sleep(0.1)
                
            # Build solver
            self._on_output("Building solver...")
            self.process_controller.start_process("wmake")
            
            # Wait for build to complete
            while self.process_controller.is_running():
                import time
                time.sleep(0.1)
                
            # Restore working directory
            os.chdir(old_cwd)
            
            return self.process_controller.get_exit_code() == 0
            
        except Exception as e:
            self._on_error(f"Build failed: {str(e)}")
            return False
            
    def run_simulation(self, case_path: str) -> bool:
        """
        Run the OpenFOAM simulation.
        
        Args:
            case_path: Path to the case directory
            
        Returns:
            bool: True if simulation started successfully, False otherwise
        """
        if not os.path.exists(case_path):
            self._on_error(f"Case directory not found: {case_path}")
            return False
            
        try:
            # Change to case directory and run solver
            command = f"cd {case_path} && {self.solver_name}"
            self._on_output(f"Starting simulation with {self.solver_name}...")
            self.process_controller.start_process(command)
            
            return True
            
        except Exception as e:
            self._on_error(f"Failed to start simulation: {str(e)}")
            return False
            
    def stop_simulation(self):
        """
        Stop the running simulation.
        """
        self.process_controller.terminate_process()
        
    def is_running(self) -> bool:
        """
        Check if simulation is currently running.
        
        Returns:
            bool: True if simulation is running
        """
        return self.process_controller.is_running()
        
    def get_solver_path(self) -> str:
        """
        Get the path to the solver directory.
        
        Returns:
            str: Path to solver directory
        """
        return os.path.join(self.project_path, self.solver_name)
        
    def get_solver_executable(self) -> Optional[str]:
        """
        Get the path to the solver executable.
        
        Returns:
            str or None: Path to executable if it exists
        """
        solver_path = self.get_solver_path()
        executable = os.path.join(solver_path, self.solver_name)
        if os.path.exists(executable):
            return executable
        return None
        
    def check_solver_ready(self) -> bool:
        """
        Check if the solver is built and ready to run.
        
        Returns:
            bool: True if solver is ready
        """
        executable = self.get_solver_executable()
        return executable is not None and os.path.isfile(executable)
        
    def _on_output(self, output: str):
        """
        Handle process output.
        
        Args:
            output: Output string
        """
        # This can be overridden by subclasses or connected to UI elements
        print(output)
        
    def _on_error(self, error: str):
        """
        Handle process errors.
        
        Args:
            error: Error string
        """
        # This can be overridden by subclasses or connected to UI elements
        print(f"ERROR: {error}")
        
    def _on_finished(self, exit_code: int):
        """
        Handle process completion.
        
        Args:
            exit_code: Process exit code
        """
        # This can be overridden by subclasses or connected to UI elements
        print(f"Process finished with exit code: {exit_code}")