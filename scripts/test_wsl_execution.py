#!/usr/bin/env python3
"""
Minimal test to verify WSL execution of OpenFOAM commands.
This script tests the execution of a simple OpenFOAM command in WSL.
"""

import os
import sys
from pathlib import Path
import logging

# Add src to path
current_dir = Path(os.getcwd())
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import WSLExecutor directly
sys.path.insert(0, str(current_dir / "src" / "openfoam"))
from wsl_executor import WSLExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSLExecutionTest")

def test_wsl_execution():
    """Test WSL execution of OpenFOAM commands."""
    executor = WSLExecutor()
    
    # Verify WSL is accessible
    if not executor.verify_wsl():
        logger.error("WSL verification failed. OpenFOAM may not be installed or accessible in WSL.")
        return False
    
    logger.info("WSL verification successful.")
    
    # Use one of the template directories for testing
    template_dir = current_dir / "src" / "resources" / "templates" / "SPM"
    if not template_dir.exists():
        logger.error(f"Template directory not found at {template_dir}")
        return False
    
    windows_path = str(template_dir.resolve())
    wsl_path = executor.convert_to_wsl_path(windows_path)
    logger.info(f"Testing in directory: {windows_path} (WSL: {wsl_path})")
    
    # Test a simple OpenFOAM command (e.g., blockMesh)
    command = "blockMesh"
    logger.info(f"Executing command: {command}")
    
    return_code, stdout, stderr = executor.execute_command(command, windows_path)
    
    logger.info(f"Return code: {return_code}")
    if stdout:
        logger.info(f"stdout: {stdout[:200]}")
    if stderr:
        logger.error(f"stderr: {stderr[:200]}")
    
    if return_code == 0:
        logger.info("OpenFOAM command executed successfully!")
        return True
    else:
        logger.error("OpenFOAM command failed.")
        return False

if __name__ == "__main__":
    success = test_wsl_execution()
    sys.exit(0 if success else 1)