import subprocess
import os
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class WSLExecutor:
    """Execute OpenFOAM commands through WSL on Windows."""

    def __init__(self):
        self.wsl_verified = False

    def verify_wsl(self):
        """Verify WSL OpenFOAM is accessible."""
        if self.wsl_verified:
            return True

        try:
            logger.info("Verifying WSL OpenFOAM installation...")
            # Check if WSL is installed and OpenFOAM is available
            result = subprocess.run(
                ['wsl', 'bash', '-c', 'which blockMesh'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"OpenFOAM found in WSL: {result.stdout.strip()}")
                self.wsl_verified = True
                return True
            else:
                logger.warning(f"OpenFOAM verification in WSL returned non-zero: {result.returncode}")
                logger.warning(f"stdout: {result.stdout}")
                logger.warning(f"stderr: {result.stderr}")
                # Try sourcing bashrc if generic 'which' fails?
                # OpenFOAM usually requires sourcing /opt/openfoam*/etc/bashrc
                # We can try to find where it is or assume user has it in .bashrc
                return False

        except subprocess.TimeoutExpired:
            logger.error("WSL verification timed out")
            return False
        except Exception as e:
            logger.error(f"WSL verification failed: {e}")
            return False

    def convert_to_wsl_path(self, windows_path):
        r"""Convert Windows path to WSL path.
         
        Examples:
            C:\Users\name\project -> /mnt/c/Users/name/project
        """
        try:
            path = Path(windows_path).resolve()
            drive = path.drive.replace(':', '').lower()
            path_str = str(path).replace('\\', '/')
            # Remove drive letter from path string (e.g. C:/Users... -> /Users...)
            if ':' in path_str:
                path_without_drive = path_str.split(':', 1)[1]
            else:
                path_without_drive = path_str
            
            wsl_path = f"/mnt/{drive}{path_without_drive}"
            return wsl_path
        except Exception as e:
            logger.error(f"Path conversion failed for {windows_path}: {e}")
            return str(windows_path)

    def execute_command(self, command, working_dir=None, timeout=3600):
        """Execute OpenFOAM command through WSL.

        Args:
            command: OpenFOAM command to execute
            working_dir: Working directory (Windows path)
            timeout: Command timeout in seconds

        Returns:
            tuple: (return_code, stdout, stderr)
        """
        try:
            wsl_command_parts = ['wsl', 'bash', '-c']
            
            # Construct the shell command string
            if working_dir:
                wsl_work_dir = self.convert_to_wsl_path(working_dir)
                # Source bashrc? Assuming user has OpenFOAM configured in .bashrc for now as per instructions "WSL path capture"
                # But safer to source if we knew where. 
                # For Phase 1, we just launch WSL.
                full_command = f"cd '{wsl_work_dir}' && {command}"
            else:
                full_command = command

            logger.info(f"Executing in WSL: {full_command}")

            result = subprocess.run(
                wsl_command_parts + [full_command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.stdout:
                logger.debug(f"stdout: {result.stdout[:200]}")
            if result.stderr:
                logger.debug(f"stderr: {result.stderr[:200]}")

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command}")
            return -1, "", "Command timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)

    def execute_command_with_callback(self, command, working_dir, output_callback, error_callback, completion_callback=None):
        """Execute command with real-time output callbacks via WSL (Asynchronous).
        
        Args:
            command: OpenFOAM command
            working_dir: Working directory (Windows path)
            output_callback: Function to call with stdout lines
            error_callback: Function to call with stderr lines
            completion_callback: Function to call when command completes (optional)
        
        Returns:
            int: 0 if started successfully, -1 if failed to start
        """
        logger.debug("Starting execute_command_with_callback method")
        try:
            logger.debug("Setting up WSL command parts")
            wsl_command_parts = ['wsl', 'bash', '-c']
            
            # Construct the shell command string
            if working_dir:
                wsl_work_dir = self.convert_to_wsl_path(working_dir)
                full_command = f"cd '{wsl_work_dir}' && {command}"
            else:
                full_command = command
            
            logger.info(f"Starting async execution via WSL: {full_command}")
            
            process = subprocess.Popen(
                wsl_command_parts + [full_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            def monitor_process():
                try:
                    def read_stdout():
                        try:
                            for line in process.stdout:
                                if line:
                                    output_callback(line.rstrip())
                        except Exception as e:
                            logger.error(f"Error reading stdout: {e}")
                    
                    def read_stderr():
                        try:
                            for line in process.stderr:
                                if line:
                                    error_callback(line.rstrip())
                        except Exception as e:
                            logger.error(f"Error reading stderr: {e}")
                    
                    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    
                    stdout_thread.start()
                    stderr_thread.start()
                    
                    # Wait for completion (blocks this thread, not main)
                    return_code = process.wait()
                    
                    # Wait for I/O threads to finish
                    stdout_thread.join(timeout=5)
                    stderr_thread.join(timeout=5)
                    
                    logger.info(f"Async command completed with return code: {return_code}")
                    
                    if completion_callback:
                        completion_callback(return_code)
                except Exception as e:
                    logger.error(f"Error in monitor thread: {e}")
                    if completion_callback:
                        completion_callback(-1)
            
            # Start the monitor thread
            monitor_thread = threading.Thread(target=monitor_process, daemon=True)
            monitor_thread.start()
            
            return 0 # Return success immediately
            
        except Exception as e:
            logger.error(f"Command execution with callbacks failed: {e}")
            error_callback(f"Execution failed: {str(e)}")
            return -1
