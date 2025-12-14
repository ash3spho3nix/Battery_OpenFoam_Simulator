"""OpenFOAM execution wrapper for Windows MSYS2 environment."""
import subprocess
import os
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)

class MSYS2Executor:
    """Execute OpenFOAM commands through MSYS2 on Windows."""
    
    def __init__(self, msys2_bat="OpenFOAM-MSYS2.bat"):
        self.msys2_bat = msys2_bat
        self.msys2_verified = False
        
    def verify_msys2(self):
        """Verify MSYS2 OpenFOAM is accessible."""
        if self.msys2_verified:
            return True
            
        try:
            logger.info("Verifying OpenFOAM-MSYS2 installation...")
            result = subprocess.run(
                [self.msys2_bat, "-c", "which blockMesh"],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info(f"OpenFOAM found: {result.stdout.strip()}")
                self.msys2_verified = True
                return True
            else:
                logger.warning(f"OpenFOAM verification returned non-zero: {result.returncode}")
                logger.warning(f"stdout: {result.stdout}")
                logger.warning(f"stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("MSYS2 verification timed out")
            return False
        except Exception as e:
            logger.error(f"MSYS2 verification failed: {e}")
            return False
            
    def convert_windows_path_to_msys2(self, windows_path):
        """Convert Windows path to MSYS2 path.
        
        Examples:
            C:\\Users\\name\\project -> /c/Users/name/project
            D:\\data\\simulation -> /d/data/simulation
        """
        try:
            path = Path(windows_path).resolve()
            
            # Get drive letter
            drive = path.drive.replace(':', '').lower()
            
            # Get path without drive
            path_str = str(path)
            if ':' in path_str:
                path_without_drive = path_str.split(':', 1)[1]
            else:
                path_without_drive = path_str
                
            # Convert backslashes to forward slashes
            path_without_drive = path_without_drive.replace('\\', '/')
            
            # Ensure no leading slash
            if path_without_drive.startswith('/'):
                path_without_drive = path_without_drive[1:]
            
            msys2_path = f"/{drive}/{path_without_drive}"
            logger.debug(f"Converted {windows_path} -> {msys2_path}")
            
            return msys2_path
            
        except Exception as e:
            logger.error(f"Path conversion failed for {windows_path}: {e}")
            # Return original path as fallback
            return str(windows_path).replace('\\', '/')
        
    def execute_command(self, command, working_dir=None, timeout=3600):
        """Execute OpenFOAM command through MSYS2.
        
        Args:
            command: OpenFOAM command to execute
            working_dir: Working directory (Windows path)
            timeout: Command timeout in seconds
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        try:
            if working_dir:
                msys2_path = self.convert_windows_path_to_msys2(working_dir)
                full_command = f"cd {msys2_path} && {command}"
            else:
                full_command = command
                
            logger.info(f"Executing via MSYS2: {full_command}")
            
            result = subprocess.run(
                [self.msys2_bat, "-c", full_command],
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )
            
            logger.info(f"Command completed with return code: {result.returncode}")
            
            if result.stdout:
                logger.debug(f"stdout: {result.stdout[:500]}")
            if result.stderr:
                logger.debug(f"stderr: {result.stderr[:500]}")
                
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command}")
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
            
    def execute_command_with_callback(self, command, working_dir, output_callback, error_callback):
        """Execute command with real-time output callbacks.
        
        Args:
            command: OpenFOAM command
            working_dir: Working directory (Windows path)
            output_callback: Function to call with stdout lines
            error_callback: Function to call with stderr lines
            
        Returns:
            int: Return code
        """
        try:
            if working_dir:
                msys2_path = self.convert_windows_path_to_msys2(working_dir)
                full_command = f"cd {msys2_path} && {command}"
            else:
                full_command = command
                
            logger.info(f"Executing with callbacks: {full_command}")
            
            process = subprocess.Popen(
                [self.msys2_bat, "-c", full_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )
            
            # Read output in real-time
            import threading
            
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
            
            # Wait for completion
            return_code = process.wait()
            
            # Wait for threads to finish
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            logger.info(f"Command completed with return code: {return_code}")
            
            return return_code
            
        except Exception as e:
            logger.error(f"Command execution with callbacks failed: {e}")
            error_callback(f"Execution failed: {str(e)}")
            return -1

# Global instance
_executor = None

def get_executor():
    """Get global MSYS2 executor instance."""
    global _executor
    if _executor is None:
        _executor = MSYS2Executor()
    return _executor
