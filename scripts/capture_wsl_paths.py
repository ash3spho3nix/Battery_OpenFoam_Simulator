#!/usr/bin/env python3
"""
Script to capture WSL paths for OpenFOAM template files.
This script identifies the template files and converts their Windows paths to WSL paths.
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
logger = logging.getLogger("WSLPathCapture")

def capture_wsl_paths():
    """Capture WSL paths for OpenFOAM template files."""
    executor = WSLExecutor()
    
    # Identify template directories
    templates_dir = current_dir / "src" / "resources" / "templates"
    if not templates_dir.exists():
        logger.error(f"Templates directory not found at {templates_dir}")
        return
    
    logger.info(f"Templates directory: {templates_dir}")
    
    # List all template directories
    template_dirs = [d for d in templates_dir.iterdir() if d.is_dir()]
    logger.info(f"Found {len(template_dirs)} template directories: {template_dirs}")
    
    # Capture WSL paths for each template directory
    wsl_paths = {}
    for template_dir in template_dirs:
        windows_path = str(template_dir.resolve())
        wsl_path = executor.convert_to_wsl_path(windows_path)
        wsl_paths[windows_path] = wsl_path
        logger.info(f"Windows: {windows_path} -> WSL: {wsl_path}")
    
    # Save the mapping to a file
    mapping_file = current_dir / "wsl_path_mapping.txt"
    with open(mapping_file, "w") as f:
        for windows_path, wsl_path in wsl_paths.items():
            f.write(f"{windows_path}\t{wsl_path}\n")
    
    logger.info(f"WSL path mapping saved to {mapping_file}")
    return wsl_paths

if __name__ == "__main__":
    capture_wsl_paths()