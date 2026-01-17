"""
Process Controller with WSL integration for OpenFOAM execution.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal
from src.openfoam.wsl_executor import WSLExecutor

logger = logging.getLogger(__name__)


class ProcessController(QObject):
    """Process controller using WSL for OpenFOAM commands."""
    
    # Signals
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_started = pyqtSignal()
    process_finished = pyqtSignal(int)  # exit code
    
    def __init__(self):
        super().__init__()
        self.wsl_executor = WSLExecutor()
        self.running = False
        logger.info("ProcessController initialized with WSL")
    
    def start_process(self, command: str, working_dir: str = None):
        """Start OpenFOAM process via WSL."""
        if self.running:
            logger.warning("Process already running")
            return False
         
        try:
            logger.info(f"Starting process: {command} in {working_dir}")
            self.running = True
            self.process_started.emit()
            
            # Execute via WSL with callbacks
            exit_code = self.wsl_executor.execute_command_with_callback(
                command,
                working_dir,
                self._on_stdout,
                self._on_stderr,
                self._on_completion
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start process: {e}", exc_info=True)
            self.error_received.emit(str(e))
            self.running = False
            return False
    
    def terminate_process(self):
        """Terminate running process."""
        if self.running:
            logger.info("Terminating process")
            # MSYS2Executor doesn't support termination yet
            self.running = False
    
    def is_running(self) -> bool:
        """Check if process is running."""
        return self.running
    
    def _on_stdout(self, text: str):
        """Handle stdout from MSYS2."""
        self.output_received.emit(text)
    
    def _on_stderr(self, text: str):
        """Handle stderr from MSYS2."""
        self.error_received.emit(text)
    
    def _on_completion(self, exit_code: int):
        """Handle process completion."""
        self.running = False
        logger.info(f"Process finished with exit code: {exit_code}")
        self.process_finished.emit(exit_code)
