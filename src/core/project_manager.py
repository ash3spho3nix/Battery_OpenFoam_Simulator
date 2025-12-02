"""
Project management for Battery Simulator.

This module contains the ProjectManager class, which handles project creation,
template management, and file operations. It's the Python equivalent of the
file operations in the C++ MainWindow class.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import re


class ProjectManager:
    """
    Manages project creation and template operations.
    
    Handles copying templates, updating file references, and managing
    project directories.
    """
    
    def __init__(self):
        """Initialize the project manager."""
        self.templates_path = self._get_templates_path()
        
    def _get_templates_path(self):
        """Lazy import of TEMPLATES_PATH to avoid circular imports."""
        from src.core.constants import TEMPLATES_PATH
        return TEMPLATES_PATH
        
    def create_project(
        self, 
        project_path: str, 
        project_name: str, 
        module: str
    ) -> bool:
        """
        Create a new project from template.
        
        Args:
            project_path: Path where the project should be created
            project_name: Name of the project
            module: Module type (SPM, halfCell, fullCell)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if module not in self._get_supported_modules():
            raise ValueError(f"Unsupported module: {module}")
            
        # Get template source
        template_source = self.templates_path / module
        if not template_source.exists():
            raise FileNotFoundError(f"Template not found: {template_source}")
            
        # Create project directory
        project_dir = os.path.join(project_path, project_name)
        if os.path.exists(project_dir):
            raise FileExistsError(f"Project already exists: {project_dir}")
            
        try:
            # Copy template files
            self._copy_template_files(template_source, project_dir, project_name)
            
            # Update file references
            self._update_file_references(project_dir, project_name, module)
            
            # Save recent project
            self._save_recent_project(project_path, project_name)
            
            return True
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            raise e
            
    def _copy_template_files(
        self, 
        source: Path, 
        destination: str, 
        project_name: str
    ):
        """
        Recursively copy template files to destination.
        
        Args:
            source: Source template directory
            destination: Destination project directory
            project_name: Name of the project
        """
        # Copy the entire template directory
        shutil.copytree(source, destination)
        
        # Rename the main solver directory
        old_solver_name = next((d for d in os.listdir(destination) 
                               if d in self._get_solver_names().values()), None)
        if old_solver_name:
            old_path = os.path.join(destination, old_solver_name)
            new_path = os.path.join(destination, project_name)
            os.rename(old_path, new_path)
            
    def _update_file_references(
        self, 
        project_path: str, 
        project_name: str, 
        module: str
    ):
        """
        Update file references in the project.
        
        Updates Make/files and other configuration files to reference
        the new project name.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            module: Module type
        """
        # Update Make/files
        make_file = os.path.join(project_path, project_name, "Make", "files")
        if os.path.exists(make_file):
            with open(make_file, 'r') as f:
                content = f.read()
                
            # Replace module references
            old_solver_name = self._get_solver_names()[module]
            content = content.replace(old_solver_name, project_name)
            
            with open(make_file, 'w') as f:
                f.write(content)
                
        # Update other configuration files as needed
        # This can be extended based on specific requirements
        
    def _save_recent_project(self, project_path: str, project_name: str):
        """
        Save the project to recent projects list.
        
        Args:
            project_path: Path to the project
            project_name: Name of the project
        """
        recent_file = Path(__file__).parent.parent / "resources" / "most_recent_file"
        recent_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(recent_file, 'w') as f:
            f.write(os.path.join(project_path, project_name))
            
    def open_project(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Open an existing project and determine its properties.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dict containing project info or None if invalid
        """
        if not os.path.exists(project_path):
            return None
            
        # Extract project name
        project_name = os.path.basename(project_path)
        
        # Determine module type
        module = self._detect_module(project_path)
        if not module:
            return None
            
        return {
            'path': project_path,
            'name': project_name,
            'module': module
        }
        
    def _detect_module(self, project_path: str) -> Optional[str]:
        """
        Detect the module type of a project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Module type or None if undetectable
        """
        for module in self._get_supported_modules():
            solver_dir = os.path.join(project_path, module)
            if os.path.exists(solver_dir):
                return module
        return None
        
    def validate_project_name(self, name: str) -> bool:
        """
        Validate a project name.
        
        Args:
            name: Project name to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Only allow letters, numbers, and underscores
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, name))
        
    def get_template_info(self, module: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a template.
        
        Args:
            module: Module type
            
        Returns:
            Dict containing template information
        """
        template_path = self.templates_path / module
        if not template_path.exists():
            return None
            
        return {
            'name': module,
            'description': self._get_module_descriptions().get(module, ''),
            'path': str(template_path),
            'exists': template_path.exists()
        }
        
    def list_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available templates.
        
        Returns:
            Dict mapping module names to template info
        """
        templates = {}
        for module in self._get_supported_modules():
            info = self.get_template_info(module)
            if info:
                templates[module] = info
        return templates
        
    def _get_supported_modules(self):
        """Lazy import of SUPPORTED_MODULES to avoid circular imports."""
        from src.core.constants import SUPPORTED_MODULES
        return SUPPORTED_MODULES
        
    def _get_solver_names(self):
        """Lazy import of SOLVER_NAMES to avoid circular imports."""
        from src.core.constants import SOLVER_NAMES
        return SOLVER_NAMES
        
    def _get_module_descriptions(self):
        """Lazy import of MODULE_DESCRIPTIONS to avoid circular imports."""
        from src.core.constants import MODULE_DESCRIPTIONS
        return MODULE_DESCRIPTIONS