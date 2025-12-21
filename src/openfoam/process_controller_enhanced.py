"""
Enhanced Process controller for OpenFOAM solver execution - Enhanced for Windows MSYS2.

This module provides the enhanced ProcessController class with critical fixes
for missing methods and improved error handling.
"""

import subprocess
import threading
import time
import logging
import re
import platform
from typing import Optional, List, Dict, Callable
from PyQt6.QtCore import QObject, pyqtSignal
import os
from pathlib import Path
logger = logging.getLogger(__name__)


class ProcessController(QObject):
    """
    Enhanced controller for managing OpenFOAM solver processes.
    
    Provides real-time output streaming, process control, error detection,
    and cross-platform compatibility for OpenFOAM commands executed through
    MSYS2 on Windows.
    """
    
    # Signals for process events
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_started = pyqtSignal()
    process_finished = pyqtSignal(int)  # exit code
    resource_usage_signal = pyqtSignal(dict)  # memory, cpu
    
    def __init__(self, parent=None):
        """Initialize the enhanced process controller."""
        super().__init__(parent)
        
        self.process = None
        self.monitor_thread = None
        self._paused = False
        self._running = False
        self.output_buffer = []
        self.error_buffer = []
        
        # Get MSYS2 executor
        from src.openfoam.msys2_executor import get_executor
        self.executor = get_executor()
        
        # Error detection patterns
        self._compilation_error_patterns = [
            r'error:\s*(.+)',
            r'Error:\s*(.+)',
            r'#error\s*(.+)',
            r'undefined reference to\s*(.+)',
            r'cannot find\s*(.+)',
            r'fatal error:\s*(.+)\s*No such file or directory'
        ]
        
        self._runtime_error_patterns = [
            r'FOAM FATAL ERROR\s*(.+)',
            r'FOAM FATAL IO ERROR\s*(.+)',
            r'Time =\s*(\d+)\s*Time is not in ascending order',
            r'Courant Number\s*(\d+\.\d+)\s*increases over limit',
            r'divergence detected',
            r'segmentation fault',
            r'floating point exception'
        ]
        
    def start_process(self, command: str, working_dir: str = None):
        """Start a subprocess with the given command using MSYS2 executor.
        
        Args:
            command: OpenFOAM command to execute
            working_dir: Working directory (Windows path)
        """
        if self._running:
            logger.warning("Process already running, terminating before restart")
            self.terminate_process()
            time.sleep(0.5)  # Give time for cleanup
            
        try:
            logger.info(f"Starting process: {command}")
            logger.info(f"Working directory: {working_dir}")
            
            # Verify MSYS2 is available
            if not self.executor.verify_msys2():
                error_msg = "OpenFOAM-MSYS2 not found or not working. Please ensure OpenFOAM-MSYS2.bat is in PATH."
                logger.error(error_msg)
                self.error_received.emit(error_msg)
                return
            
            # Clear buffers
            self.output_buffer.clear()
            self.error_buffer.clear()
            
            # Create output callbacks with error detection
            def output_callback(line):
                self.output_received.emit(line)
                self.output_buffer.append(line)
                if len(self.output_buffer) > 1000:
                    self.output_buffer.pop(0)
                
                # Detect runtime errors in output
                runtime_errors = self._detect_runtime_errors(line)
                if runtime_errors:
                    for error in runtime_errors:
                        self.error_received.emit(f"Runtime Error: {error}")
                
            def error_callback(line):
                self.error_received.emit(line)
                self.error_buffer.append(line)
                if len(self.error_buffer) > 1000:
                    self.error_buffer.pop(0)
                
                # Detect compilation errors in stderr
                compilation_errors = self._detect_compilation_errors(line)
                if compilation_errors:
                    for error in compilation_errors:
                        self.error_received.emit(f"Compilation Error: {error}")
            
            self._running = True
            self._paused = False
            self.process_started.emit()
            
            # Start in separate thread to avoid blocking UI
            def run_command():
                try:
                    return_code = self.executor.execute_command_with_callback(
                        command, working_dir, output_callback, error_callback
                    )
                    logger.info(f"Process finished with return code: {return_code}")
                    self._running = False
                    self.process_finished.emit(return_code)
                except Exception as e:
                    logger.error(f"Process execution failed: {e}")
                    error_callback(f"Process execution failed: {str(e)}")
                    self._running = False
                    self.process_finished.emit(-1)
                    
            self.monitor_thread = threading.Thread(target=run_command, daemon=True)
            self.monitor_thread.start()
            logger.info("Process thread started")
            
        except Exception as e:
            error_msg = f"Failed to start process: {str(e)}"
            logger.error(error_msg)
            self.error_received.emit(error_msg)
            self._running = False
            
    def terminate_process(self):
        """Terminate the running process."""
        if self._running:
            logger.info("Terminating process")
            try:
                if self.process:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning("Process did not terminate, killing")
                        self.process.kill()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
                
            self._running = False
            self._paused = False
            logger.info("Process terminated")
            
    def pause_process(self):
        """Pause the running process (not fully supported on Windows)."""
        if self._running and not self._paused:
            logger.info("Pausing process (limited support on Windows)")
            self._paused = True
            # Note: SIGSTOP/SIGCONT not available on Windows
            # This is a placeholder for future implementation
            
    def resume_process(self):
        """Resume the paused process (not fully supported on Windows)."""
        if self._running and self._paused:
            logger.info("Resuming process")
            self._paused = False
            
    def send_signal(self, signal_num: int):
        """Send signal to running process - FIXED: Critical method for pause/resume."""
        if self.process and self._running:
            try:
                self.process.send_signal(signal_num)
                logger.info(f"Sent signal {signal_num} to process")
            except Exception as e:
                logger.error(f"Failed to send signal {signal_num}: {e}")
    
    def get_exit_code(self) -> int:
        """Get the exit code of the last process - FIXED: Critical method for error handling."""
        if self.process:
            return self.process.returncode
        return -1
            
    def is_running(self):
        """Check if process is running."""
        return self._running
        
    def is_paused(self):
        """Check if process is paused."""
        return self._paused
        
    def get_output_buffer(self):
        """Get buffered output."""
        return list(self.output_buffer)
        
    def get_error_buffer(self):
        """Get buffered errors."""
        return list(self.error_buffer)
    
    def _detect_compilation_errors(self, output: str) -> List[str]:
        """Detect common OpenFOAM compilation errors."""
        errors = []
        for pattern in self._compilation_error_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            errors.extend(matches)
        return errors
    
    def _detect_runtime_errors(self, output: str) -> List[str]:
        """Detect common OpenFOAM runtime errors."""
        errors = []
        for pattern in self._runtime_error_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            errors.extend(matches)
        return errors


class PlatformDetector:
    """Detect and configure platform-specific settings."""
    
    @staticmethod
    def get_platform_info():
        """Get detailed platform information."""
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'openfoam_compatible': PlatformDetector._check_openfoam_compatibility()
        }
    
    @staticmethod
    def _check_openfoam_compatibility():
        """Check if platform is compatible with OpenFOAM."""
        system = platform.system()
        if system == 'Windows':
            return PlatformDetector._check_windows_openfoam()
        elif system == 'Linux':
            return PlatformDetector._check_linux_openfoam()
        elif system == 'Darwin':
            return PlatformDetector._check_macos_openfoam()
        return False
    
    @staticmethod
    def _check_windows_openfoam():
        """Check Windows OpenFOAM installation."""
        # Check for MSYS2/OpenFOAM
        msys2_paths = [
            r'C:\msys64\mingw64\bin\OpenFOAM-MSYS2.bat',
            r'C:\OpenFOAM\OpenFOAM-MSYS2.bat',
            r'C:\Program Files\OpenFOAM\OpenFOAM-MSYS2.bat'
        ]
        
        for path in msys2_paths:
            if os.path.exists(path):
                return True
        return False
    
    @staticmethod
    def _check_linux_openfoam():
        """Check Linux OpenFOAM installation."""
        # Check environment variables
        return os.environ.get('WM_PROJECT_DIR') is not None
    
    @staticmethod
    def _check_macos_openfoam():
        """Check macOS OpenFOAM installation."""
        # Check for Docker or native installation
        docker_check = subprocess.run(['docker', '--version'], 
                                    capture_output=True, text=True)
        return docker_check.returncode == 0


class PathHandler:
    """Handle platform-specific path operations."""
    
    @staticmethod
    def convert_path_for_openfoam(path: str) -> str:
        """Convert path to OpenFOAM-compatible format."""
        system = platform.system()
        
        if system == 'Windows':
            return PathHandler._windows_to_msys2_path(path)
        elif system == 'Linux' or system == 'Darwin':
            return str(Path(path).resolve())
        
        return path
    
    @staticmethod
    def _windows_to_msys2_path(windows_path: str) -> str:
        """Convert Windows path to MSYS2 path."""
        path = Path(windows_path).resolve()
        drive = path.drive.replace(':', '').lower()
        path_str = str(path)
        
        if ':' in path_str:
            path_without_drive = path_str.split(':', 1)[1]
        else:
            path_without_drive = path_str
            
        path_without_drive = path_without_drive.replace('\\', '/')
        
        if path_without_drive.startswith('/'):
            path_without_drive = path_without_drive[1:]
            
        return f"/{drive}/{path_without_drive}"


class ProcessMonitor:
    """Monitor process health and resource usage."""
    
    def __init__(self, process_controller: ProcessController):
        self.process_controller = process_controller
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 1.0):
        """Start monitoring process health."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring process health."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring and self.process_controller.is_running():
            try:
                # Check process status
                process = self.process_controller.process
                if process:
                    # Check if process is still alive
                    poll_result = process.poll()
                    if poll_result is not None:
                        # Process has terminated
                        logger.info(f"Process terminated with code: {poll_result}")
                        break
                        
                # Check resource usage (if psutil available)
                self._check_resource_usage()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                break
                
    def _check_resource_usage(self):
        """Check process resource usage."""
        try:
            import psutil
            process = self.process_controller.process
            if process:
                psutil_process = psutil.Process(process.pid)
                
                # Get memory usage
                memory_info = psutil_process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Get CPU usage
                cpu_percent = psutil_process.cpu_percent()
                
                # Emit resource usage signal
                if hasattr(self.process_controller, 'resource_usage_signal'):
                    self.process_controller.resource_usage_signal.emit({
                        'memory_mb': memory_mb,
                        'cpu_percent': cpu_percent
                    })
                    
        except ImportError:
            # psutil not available, skip resource monitoring
            pass
        except Exception as e:
            logger.warning(f"Failed to get resource usage: {e}")


class OpenFOAMError:
    """Structured error information for OpenFOAM operations."""
    
    def __init__(self, error_type: str, message: str, details: Dict = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict:
        """Convert error to dictionary format."""
        return {
            'type': self.error_type,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }
        
    def __str__(self) -> str:
        """String representation of error."""
        return f"{self.error_type}: {self.message}"


class ErrorRecovery:
    """Handle error recovery for OpenFOAM operations."""
    
    @staticmethod
    def suggest_recovery(error: OpenFOAMError) -> List[str]:
        """Suggest recovery actions for specific errors."""
        recovery_actions = []
        
        if error.error_type == 'COMPILATION_ERROR':
            recovery_actions.extend([
                "Check OpenFOAM installation and environment variables",
                "Verify solver source code for syntax errors",
                "Ensure all required dependencies are installed",
                "Try cleaning and rebuilding: wclean && wmake"
            ])
            
        elif error.error_type == 'RUNTIME_ERROR':
            recovery_actions.extend([
                "Check case setup and boundary conditions",
                "Verify mesh quality and topology",
                "Reduce time step size if Courant number is high",
                "Check available disk space and memory"
            ])
            
        elif error.error_type == 'PATH_ERROR':
            recovery_actions.extend([
                "Verify case path exists and is accessible",
                "Check file permissions",
                "Ensure OpenFOAM environment is properly sourced"
            ])
            
        return recovery_actions