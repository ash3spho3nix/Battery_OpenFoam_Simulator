"""
File operations utilities for Battery Simulator.

This module provides the TemplateManager class for handling template-based
project creation and file management operations.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import re


class TemplateManager:
    """
    Manager for template-based file operations.
    
    Handles copying templates, updating file references, and managing
    project directories.
    """
    
    def __init__(self, templates_path: str):
        """
        Initialize the template manager.
        
        Args:
            templates_path: Path to the templates directory
        """
        self.templates_path = Path(templates_path)
        
    def create_project_from_template(
        self, 
        template_name: str, 
        project_path: str, 
        project_name: str
    ) -> bool:
        """
        Create a new project from template.
        
        Args:
            template_name: Name of the template to use
            project_path: Path where the project should be created
            project_name: Name of the project
            
        Returns:
            bool: True if successful, False otherwise
        """
        template_source = self.templates_path / template_name
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
            self._update_file_references(project_dir, project_name, template_name)
            
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
        
        # Rename the main solver directory if it exists
        solver_dirs = [d for d in os.listdir(destination) if os.path.isdir(os.path.join(destination, d))]
        if solver_dirs:
            # Assume first directory is the solver directory
            old_solver_name = solver_dirs[0]
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
                
            # Replace module references (this would need to be customized based on actual file content)
            # For now, we'll just replace a generic placeholder
            content = content.replace("{{PROJECT_NAME}}", project_name)
            content = content.replace("{{MODULE_NAME}}", module)
            
            with open(make_file, 'w') as f:
                f.write(content)
                
        # Update other configuration files as needed
        # This can be extended based on specific requirements
        
    def copy_and_replace_folder_contents(
        self, 
        from_dir: str, 
        to_dir: str, 
        copy_and_remove: bool = False
    ):
        """
        Copy folder contents with optional removal of source.
        
        Args:
            from_dir: Source directory
            to_dir: Destination directory
            copy_and_remove: Whether to remove source after copying
        """
        from_path = Path(from_dir)
        to_path = Path(to_dir)
        
        # Create destination if it doesn't exist
        to_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files and directories
        for item in from_path.iterdir():
            if item.is_file():
                shutil.copy2(item, to_path / item.name)
            elif item.is_dir():
                shutil.copytree(item, to_path / item.name)
                
        # Remove source if requested
        if copy_and_remove:
            shutil.rmtree(from_dir)
            
    def change_folder_name(self, name1: str, name2: str):
        """
        Rename a folder.
        
        Args:
            name1: Current folder name
            name2: New folder name
        """
        os.rename(name1, name2)
        
    def change_make_file(self, suffix: str, module: str, project_name: str):
        """
        Update Make/files with project-specific information.
        
        Args:
            suffix: File path suffix
            module: Module type
            project_name: Project name
        """
        file_path = os.path.join(self.templates_path, suffix)
        
        if not os.path.exists(file_path):
            return
            
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Replace module-specific references
        replacements = {
            "SPMFoam_OF6": project_name,
            "halfCellFoam_OF6": project_name,
            "fullCellFoam_OF6": project_name
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
            
        with open(file_path, 'w') as f:
            f.write(content)
            
    def backup_file(self, file_path: str) -> str:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            str: Path to the backup file
        """
        backup_path = file_path + self._get_backup_suffix()
        shutil.copy2(file_path, backup_path)
        return backup_path
        
    def restore_file(self, backup_path: str) -> str:
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            str: Path to the restored file
        """
        original_path = backup_path.replace(self._get_backup_suffix(), "")
        shutil.copy2(backup_path, original_path)
        return original_path
        
    def list_template_files(self, template_name: str) -> list:
        """
        List all files in a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            list: List of file paths in the template
        """
        template_path = self.templates_path / template_name
        if not template_path.exists():
            return []
            
        file_list = []
        for root, dirs, files in os.walk(template_path):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(template_path)
                file_list.append(str(relative_path))
                
        return sorted(file_list)
        
    def _get_backup_suffix(self) -> str:
        """Get the backup file suffix."""
        from src.core.constants import BACKUP_SUFFIX
        return BACKUP_SUFFIX