"""
Process controller for OpenFOAM solver execution.

This module provides the ProcessController class, which manages subprocess
execution for OpenFOAM solvers with real-time output streaming.
"""

import subprocess
import threading
import time
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.constants import PROCESS_TIMEOUT


class ProcessController(QObject):
    """
    Controller for managing OpenFOAM solver processes.
    
    Provides real-time output streaming, process control, and error handling
    similar to QProcess in the C++ implementation.
    """
    
    # Signals for process events
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_started = pyqtSignal()
    process_finished = pyqtSignal(int)  # exit code
    
    def __init__(self, parent=None):
        """
        Initialize the process controller.
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self._running = False
        
    def start_process(self, command: str, working_dir: str = None):
        """
        Start a subprocess with the given command.
        
        Args:
            command: Command to execute
            working_dir: Working directory for the process
        """
        if self._running:
            self.terminate_process()
            
        try:
            # Start the process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                cwd=working_dir,
                shell=True
            )
            
            self._running = True
            self.process_started.emit()
            
            # Start output monitoring threads
            self._start_output_monitoring()
            
        except Exception as e:
            self.error_received.emit(f"Failed to start process: {str(e)}")
            
    def _start_output_monitoring(self):
        """
        Start threads to monitor process output.
        """
        # Thread for reading stdout
        self.stdout_thread = threading.Thread(
            target=self._read_stream, 
            args=(self.process.stdout, False)
        )
        self.stdout_thread.daemon = True
        self.stdout_thread.start()
        
        # Thread for reading stderr
        self.stderr_thread = threading.Thread(
            target=self._read_stream, 
            args=(self.process.stderr, True)
        )
        self.stderr_thread.daemon = True
        self.stderr_thread.start()
        
        # Thread for monitoring process completion
        self.monitor_thread = threading.Thread(target=self._monitor_process)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _read_stream(self, stream, is_error: bool):
        """
        Read from a process stream and emit signals.
        
        Args:
            stream: Stream to read from
            is_error: True if this is stderr, False for stdout
        """
        try:
            for line in iter(stream.readline, ''):
                if line:
                    if is_error:
                        self.error_received.emit(line.rstrip())
                    else:
                        self.output_received.emit(line.rstrip())
                        
        except Exception as e:
            if self._running:
                self.error_received.emit(f"Error reading stream: {str(e)}")
                
    def _monitor_process(self):
        """
        Monitor process completion and emit finished signal.
        """
        try:
            # Wait for process to complete
            exit_code = self.process.wait()
            self._running = False
            self.process_finished.emit(exit_code)
            
        except Exception as e:
            if self._running:
                self.error_received.emit(f"Error monitoring process: {str(e)}")
                
    def terminate_process(self):
        """
        Terminate the running process.
        """
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                # Wait for process to terminate with timeout
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self.process.kill()
                self.process.wait()
            except Exception as e:
                self.error_received.emit(f"Error terminating process: {str(e)}")
                
        self._running = False
        
    def is_running(self) -> bool:
        """
        Check if a process is currently running.
        
        Returns:
            bool: True if process is running
        """
        return self._running
        
    def get_exit_code(self) -> Optional[int]:
        """
        Get the exit code of the last process.
        
        Returns:
            int or None: Exit code if process has finished
        """
        if self.process:
            return self.process.returncode
        return None
        
    def send_signal(self, signal_num: int):
        """
        Send a signal to the running process.
        
        Args:
            signal_num: Signal number to send
        """
        if self.process and self._running:
            try:
                self.process.send_signal(signal_num)
            except Exception as e:
                self.error_received.emit(f"Error sending signal: {str(e)}")
                
    def write_to_stdin(self, data: str):
        """
        Write data to the process stdin.
        
        Args:
            data: Data to write
        """
        if self.process and self._running:
            try:
                self.process.stdin.write(data + '\n')
                self.process.stdin.flush()
            except Exception as e:
                self.error_received.emit(f"Error writing to stdin: {str(e)}")
                
    def cleanup(self):
        """
        Clean up resources.
        """
        self.terminate_process()
        if self.process:
            self.process = None
        self._running = False
