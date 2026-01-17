import sys
import os
from pathlib import Path
import logging

# Add src to path
current_dir = Path(os.getcwd())
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.openfoam.wsl_executor import WSLExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSLVerifier")

def verify():
    executor = WSLExecutor()
    
    # Check WSL existence
    if not executor.verify_wsl():
        logger.error("WSL not verified/available.")
        # We proceed anyway to test path conversion logic at least
    
    # Check template path
    cwd = Path(os.getcwd())
    templates_path = cwd / "src" / "resources" / "templates"
    
    logger.info(f"Windows Template Path: {templates_path}")
    
    wsl_path = executor.convert_to_wsl_path(templates_path)
    logger.info(f"WSL Template Path: {wsl_path}")
    
    # Try to list files via WSL
    cmd = f"ls -R '{wsl_path}'"
    code, out, err = executor.execute_command(cmd)
    
    if code == 0:
        logger.info("Successfully listed templates in WSL:")
        print(out[:500] + "..." if len(out) > 500 else out)
    else:
        logger.error(f"Failed to list templates. Code: {code}")
        logger.error(f"Stderr: {err}")

if __name__ == "__main__":
    verify()
