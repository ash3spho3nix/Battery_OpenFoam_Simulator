import sys
import os
import shutil
import time
from pathlib import Path
import logging

# Add src to path
current_dir = Path(os.getcwd())
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.openfoam.wsl_executor import WSLExecutor
from src.core.project_manager import ProjectManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSLTest")

def test_execution():
    executor = WSLExecutor()
    
    # 1. Setup a test project
    test_project_name = "wsl_test_project"
    projects_dir = current_dir / "projects"
    projects_dir.mkdir(exist_ok=True)
    
    # Clean up previous test
    project_path = projects_dir / test_project_name
    if project_path.exists():
        shutil.rmtree(project_path)
        
    # Create project from SPM template
    # We use ProjectManager manually or just copy
    logger.info("Creating test project...")
    template_path = current_dir / "src" / "resources" / "templates" / "SPM"
    if not template_path.exists():
        logger.error(f"Template not found at {template_path}")
        return

    shutil.copytree(template_path, project_path)
    logger.info(f"Project created at {project_path}")
    
    # 2. Run blockMesh via WSL
    logger.info("Running blockMesh...")
    # OpenFOAM commands usually need sourcing. 
    # If 'blockMesh' is not in path, we might need to source /opt/openfoam.../etc/bashrc
    # We will try 'blockMesh' first, assuming user has it in .bashrc
    
    code, out, err = executor.execute_command("blockMesh", str(project_path))
    
    if code == 0:
        logger.info("blockMesh successful!")
        logger.info(out)
    else:
        logger.warning("blockMesh failed (maybe not in path?)")
        logger.warning(err)
        
        # Try finding OpenFOAM environment
        logger.info("Attempting to source OpenFOAM...")
        # Common location: /opt/openfoam*/etc/bashrc or /usr/lib/openfoam/openfoam*/etc/bashrc
        # Or check env vars if available?
        # For now, let's try a common one if the first attempt failed
        source_cmd = "source /opt/openfoam*/etc/bashrc 2>/dev/null || source /usr/lib/openfoam/openfoam*/etc/bashrc 2>/dev/null && blockMesh"
        
        code, out, err = executor.execute_command(source_cmd, str(project_path))
        if code == 0:
             logger.info("blockMesh successful after sourcing!")
        else:
             logger.error("blockMesh failed even after sourcing attempts.")
             logger.error(err)

if __name__ == "__main__":
    test_execution()
