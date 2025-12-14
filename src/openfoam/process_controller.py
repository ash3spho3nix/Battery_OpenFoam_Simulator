"""
Process controller for OpenFOAM solver execution - Enhanced for Windows MSYS2.

This module provides the ProcessController class, which manages subprocess
execution for OpenFOAM solvers with real-time output streaming.
"""

import subprocess
import threading
import time
import logging
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class ProcessController(QObject):
    """
    Controller for managing OpenFOAM solver processes.
    
    Provides real-time output streaming, process control, and error handling
    for OpenFOAM commands executed through MSYS2 on Windows.
    """
    
    # Signals for process events
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_started = pyqtSignal()
    process_finished = pyqtSignal(int)  # exit code
    
    def __init__(self, parent=None):
        """Initialize the process controller."""
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
            
            # Create output callbacks
            def output_callback(line):
                self.output_received.emit(line)
                self.output_buffer.append(line)
                if len(self.output_buffer) > 1000:
                    self.output_buffer.pop(0)
                
            def error_callback(line):
                self.error_received.emit(line)
                self.error_buffer.append(line)
                if len(self.error_buffer) > 1000:
                    self.error_buffer.pop(0)
            
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
