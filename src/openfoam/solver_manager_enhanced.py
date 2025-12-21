"""
Enhanced OpenFOAM Solver Manager for Battery Simulator.

This module provides the enhanced OpenFOAMSolverManager class with critical fixes
for missing methods and improved error handling.
"""

import os
import sys
import subprocess
import time
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal

from .process_controller_enhanced import ProcessController, OpenFOAMError, ErrorRecovery
from ..core.constants import SOLVER_NAMES, ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)

class OpenFOAMSolverManager(QObject):
    """
    Enhanced manager for OpenFOAM solver operations.
    
    Handles solver compilation, execution, and process control
    for different simulation modules with improved error handling
    and cross-platform support.
    """
    
    # Signals for solver events
    solver_started = pyqtSignal()
    solver_finished = pyqtSignal(int)  # exit code
    solver_output = pyqtSignal(str)
    solver_error = pyqtSignal(str)
    compilation_error = pyqtSignal(str)
    runtime_error = pyqtSignal(str)
    
    def __init__(self, solver_path: str, solver_name: str, parent=None):
        """
        Initialize the enhanced solver manager.
        
        Args:
            solver_path: Path to the solver directory
            solver_name: Name of the solver to use
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.solver_path = solver_path
        self.solver_name = solver_name
        self.project_path = None
        self.process_controller = ProcessController(self)
        
        # Connect process controller signals
        self.process_controller.output_received.connect(self.solver_output.emit)
        self.process_controller.error_received.connect(self.solver_error.emit)
        self.process_controller.process_started.connect(self.solver_started.emit)
        self.process_controller.process_finished.connect(self.solver_finished.emit)
        
        # Connect enhanced error signals
        self.process_controller.error_received.connect(self._on_enhanced_error)
        
    def _on_enhanced_error(self, error_message: str):
        """Handle enhanced error detection."""
        # Check if it's a compilation error
        if "Compilation Error:" in error_message:
            self.compilation_error.emit(error_message.replace("Compilation Error:", "").strip())
        
        # Check if it's a runtime error
        elif "Runtime Error:" in error_message:
            self.runtime_error.emit(error_message.replace("Runtime Error:", "").strip())
    
    def compile_solver(self) -> bool:
        """
        Compile the OpenFOAM solver with enhanced error detection.
        
        Returns:
            bool: True if compilation successful
        """
        try:
            logger.info(f"Starting solver compilation for {self.solver_name}")
            
            # Clean previous build
            clean_cmd = f"cd {self.solver_path} && wclean"
            logger.info(f"Running clean command: {clean_cmd}")
            
            self.process_controller.start_process(clean_cmd)
            
            # Wait for clean to complete
            while self.process_controller.is_running():
                time.sleep(0.1)
                
            clean_exit_code = self.process_controller.get_exit_code()
            if clean_exit_code != 0:
                logger.warning(f"Clean command failed with exit code: {clean_exit_code}")
                # Continue anyway, as there might be nothing to clean
            
            # Compile solver
            compile_cmd = f"cd {self.solver_path} && wmake"
            logger.info(f"Running compile command: {compile_cmd}")
            
            self.process_controller.start_process(compile_cmd)
            
            # Wait for compilation to complete
            while self.process_controller.is_running():
                time.sleep(0.1)
                
            exit_code = self.process_controller.get_exit_code()
            
            if exit_code == 0:
                logger.info(SUCCESS_MESSAGES["solver_built"])
                self.solver_output.emit(SUCCESS_MESSAGES["solver_built"])
                return True
            else:
                error_msg = f"Solver compilation failed with exit code: {exit_code}"
                logger.error(error_msg)
                self.solver_error.emit(error_msg)
                
                # Suggest recovery actions
                error = OpenFOAMError("COMPILATION_ERROR", error_msg, {
                    'solver_path': self.solver_path,
                    'exit_code': exit_code
                })
                recovery_actions = ErrorRecovery.suggest_recovery(error)
                for action in recovery_actions:
                    self.solver_output.emit(f"Recovery suggestion: {action}")
                
                return False
                
        except Exception as e:
            error_msg = f"Error compiling solver: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.solver_error.emit(error_msg)
            return False
            
    def run_simulation(self, case_path: str):
        """
        Run the OpenFOAM simulation with enhanced monitoring.
        
        Args:
            case_path: Path to the case directory
        """
        try:
            # Verify case path exists
            if not os.path.exists(case_path):
                error_msg = f"Case path does not exist: {case_path}"
                logger.error(error_msg)
                self.solver_error.emit(error_msg)
                return
            
            # Change to case directory and run solver
            run_cmd = f"cd {case_path} && {self.solver_name}"
            logger.info(f"Running simulation: {run_cmd}")
            
            self.process_controller.start_process(run_cmd, working_dir=case_path)
            
            # Start resource monitoring
            monitor = self.process_controller._get_monitor()
            if monitor:
                monitor.start_monitoring(interval=2.0)
            
            self.solver_started.emit()
            
        except Exception as e:
            error_msg = f"Error starting simulation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.solver_error.emit(error_msg)
            
    def stop_simulation(self):
        """Stop the running simulation."""
        logger.info("Stopping simulation")
        self.process_controller.terminate_process()
        
    def pause_simulation(self):
        """Pause the running simulation."""
        logger.info("Pausing simulation")
        self.process_controller.send_signal(19)  # SIGSTOP
        
    def resume_simulation(self):
        """Resume the paused simulation."""
        logger.info("Resuming simulation")
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
            logger.info(f"Solver executable found: {executable_path}")
            return True
            
        logger.info(f"Solver executable not found: {executable_path}")
        
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
            'executable_path': None,
            'platform_info': self._get_platform_info()
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
        
    def _get_platform_info(self) -> Dict[str, Any]:
        """Get platform information."""
        from .process_controller_enhanced import PlatformDetector
        return PlatformDetector.get_platform_info()
        
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
        if hasattr(self.process_controller, 'monitor') and self.process_controller.monitor:
            self.process_controller.monitor.stop_monitoring()
        self.process_controller.cleanup()
        
    def send_signal(self, signal_num: int):
        """Send signal to running simulation - FIXED: Critical method for pause/resume."""
        if self.process_controller:
            self.process_controller.send_signal(signal_num)
    
    def get_exit_code(self) -> int:
        """Get the exit code of the last simulation - FIXED: Critical method for error handling."""
        if self.process_controller:
            return self.process_controller.get_exit_code()
        return -1
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        if hasattr(self.process_controller, 'monitor') and self.process_controller.monitor:
            # This would need to be implemented to return current resource usage
            # For now, return empty dict
            return {}
        return {}
    
    def get_compilation_log(self) -> List[str]:
        """Get compilation output log."""
        return self.process_controller.get_output_buffer()
    
    def get_error_log(self) -> List[str]:
        """Get error output log."""
        return self.process_controller.get_error_buffer()


class SolverValidator:
    """Validate solver setup and configuration."""
    
    @staticmethod
    def validate_solver_setup(solver_manager: OpenFOAMSolverManager) -> Dict[str, Any]:
        """Validate solver setup and return validation report."""
        report = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check solver path
        if not os.path.exists(solver_manager.solver_path):
            report['valid'] = False
            report['issues'].append(f"Solver path does not exist: {solver_manager.solver_path}")
        
        # Check OpenFOAM environment
        platform_info = solver_manager._get_platform_info()
        if not platform_info['openfoam_compatible']:
            report['valid'] = False
            report['issues'].append("OpenFOAM environment not properly configured")
        
        # Check solver executable
        executable_path = solver_manager.get_solver_executable()
        if not os.path.exists(executable_path):
            report['warnings'].append(f"Solver executable not found: {executable_path}")
            report['recommendations'].append("Run wmake to compile the solver")
        
        # Check permissions
        if not os.access(solver_manager.solver_path, os.R_OK | os.X_OK):
            report['issues'].append(f"No read/execute permissions for solver path: {solver_manager.solver_path}")
        
        return report
    
    @staticmethod
    def validate_case_setup(case_path: str) -> Dict[str, Any]:
        """Validate case setup and return validation report."""
        report = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check case directory structure
        required_dirs = ['system', 'constant', '0']
        for dir_name in required_dirs:
            dir_path = os.path.join(case_path, dir_name)
            if not os.path.exists(dir_path):
                report['valid'] = False
                report['issues'].append(f"Missing required directory: {dir_path}")
        
        # Check required files
        required_files = [
            'system/blockMeshDict',
            'system/controlDict',
            'constant/LiProperties'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(case_path, file_path)
            if not os.path.exists(full_path):
                report['valid'] = False
                report['issues'].append(f"Missing required file: {full_path}")
        
        return report