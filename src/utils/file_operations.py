"""
Simple File Operations for Battery Simulator.

Provides straightforward file operations for template management without over-engineering.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class FileOperationError(Exception):
    """Exception raised when file operations fail."""
    pass


class TemplateManager:
    """
    Simple template manager for copying OpenFOAM case templates.
    """
    
    def __init__(self, templates_path: str):
        """
        Initialize the template manager.
        
        Args:
            templates_path: Path to the templates directory (src/resources/templates)
        """
        self.templates_path = Path(templates_path)
        
        if not self.templates_path.exists():
            raise FileOperationError(f"Templates path does not exist: {templates_path}")
        
        logger.info(f"TemplateManager initialized with path: {templates_path}")
    
    def copy_template_directory(
        self, 
        template_name: str, 
        destination_path: str,
        overwrite: bool = False
    ) -> bool:
        """
        Copy a template directory to destination.
        
        Args:
            template_name: Name of template (e.g., 'SPM', 'halfCell', 'fullCell')
            destination_path: Where to copy the template
            overwrite: Whether to overwrite existing directory
            
        Returns:
            True if successful, False otherwise
        """
        template_path = self.templates_path / template_name
        dest_path = Path(destination_path)
        
        # Validate template exists
        if not template_path.exists():
            logger.error(f"Template not found: {template_name} at {template_path}")
            return False
        
        if not template_path.is_dir():
            logger.error(f"Template is not a directory: {template_name}")
            return False
        
        # Check destination
        if dest_path.exists() and not overwrite:
            logger.error(f"Destination already exists: {destination_path}")
            return False
        
        try:
            # Remove existing destination if overwrite
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            # Copy template
            shutil.copytree(template_path, dest_path)
            
            logger.info(f"Copied template {template_name} to {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy template {template_name}: {e}", exc_info=True)
            return False
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get basic information about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary with template info
        """
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            return {'exists': False, 'name': template_name}
        
        # Count files
        file_count = 0
        total_size = 0
        
        for root, dirs, files in os.walk(template_path):
            file_count += len(files)
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
        
        return {
            'exists': True,
            'name': template_name,
            'path': str(template_path),
            'file_count': file_count,
            'total_size_bytes': total_size
        }
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate that a template has required OpenFOAM structure.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Validation results
        """
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            return {
                'valid': False,
                'errors': ['Template not found']
            }
        
        # Check for required OpenFOAM directories
        required_dirs = ['system', 'constant']
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (template_path / dir_name).exists():
                missing_dirs.append(dir_name)
        
        # Check for critical files
        critical_files = {
            'system/controlDict': False,
            'system/fvSchemes': False,
            'system/fvSolution': False
        }
        
        for file_path in critical_files.keys():
            if (template_path / file_path).exists():
                critical_files[file_path] = True
        
        missing_files = [f for f, exists in critical_files.items() if not exists]
        
        valid = len(missing_dirs) == 0 and len(missing_files) == 0
        
        result = {
            'valid': valid,
            'template_name': template_name,
            'missing_dirs': missing_dirs,
            'missing_files': missing_files
        }
        
        if not valid:
            result['errors'] = []
            if missing_dirs:
                result['errors'].append(f"Missing directories: {', '.join(missing_dirs)}")
            if missing_files:
                result['errors'].append(f"Missing files: {', '.join(missing_files)}")
        
        return result
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template directories.
        
        Returns:
            List of template names
        """
        templates = []
        
        if self.templates_path.exists():
            for item in self.templates_path.iterdir():
                if item.is_dir():
                    templates.append(item.name)
        
        return sorted(templates)
    
    def create_directory(self, path: str) -> bool:
        """
        Create a directory if it doesn't exist.
        
        Args:
            path: Directory path to create
            
        Returns:
            True if successful
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False


def ensure_directory_exists(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to ensure directory exists {path}: {e}")
        return False
