"""
File operations for Battery Simulator.

This module provides utilities for template management, file copying,
parameter substitution, and project creation.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manager for OpenFOAM template files.
    
    Handles template loading, parameter substitution, and file generation.
    """
    
    def __init__(self, templates_path: str):
        """
        Initialize the template manager.
        
        Args:
            templates_path: Path to the templates directory
        """
        self.templates_path = Path(templates_path)
        self.parameters = {}
        
        if not self.templates_path.exists():
            logger.warning(f"Templates path does not exist: {self.templates_path}")
            
    def set_parameter(self, key: str, value: Any):
        """
        Set a parameter for substitution.
        
        Args:
            key: Parameter name
            value: Parameter value
        """
        self.parameters[key] = value
        
    def set_parameters(self, parameters: Dict[str, Any]):
        """
        Set multiple parameters at once.
        
        Args:
            parameters: Dictionary of parameter names and values
        """
        self.parameters.update(parameters)
        
    def load_template(self, template_name: str) -> Optional[str]:
        """
        Load a template file.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            str or None: Template content if found
        """
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return None
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded template: {template_name}")
            return content
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None
            
    def substitute_parameters(self, template_content: str) -> str:
        """
        Substitute parameters in template content.
        
        Args:
            template_content: Template content with placeholders
            
        Returns:
            str: Content with parameters substituted
        """
        result = template_content
        
        # Replace placeholders with parameter values
        for key, value in self.parameters.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
            
        return result
        
    def generate_file(self, template_name: str, output_path: str) -> bool:
        """
        Generate a file from a template.
        
        Args:
            template_name: Name of the template file
            output_path: Path where the generated file should be saved
            
        Returns:
            bool: True if successful
        """
        template_content = self.load_template(template_name)
        
        if template_content is None:
            return False
            
        # Substitute parameters
        content = self.substitute_parameters(template_content)
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Generated file: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate file {output_path}: {e}")
            return False
            
    def copy_template_directory(self, template_dir: str, output_dir: str) -> bool:
        """
        Copy an entire template directory structure.
        
        Args:
            template_dir: Name of the template directory
            output_dir: Path where the directory should be copied
            
        Returns:
            bool: True if successful
        """
        template_path = self.templates_path / template_dir
        output_path = Path(output_dir)
        
        if not template_path.exists():
            logger.error(f"Template directory not found: {template_path}")
            return False
            
        try:
            # Copy directory recursively
            if output_path.exists():
                shutil.rmtree(output_path)
            shutil.copytree(template_path, output_path)
            
            # Process all files in the copied directory
            self._process_directory(output_path)
            
            logger.debug(f"Copied template directory: {template_dir} -> {output_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy template directory: {e}")
            return False
            
    def _process_directory(self, directory_path: Path):
        """
        Process all files in a directory for parameter substitution.
        
        Args:
            directory_path: Path to the directory to process
        """
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = Path(root) / file
                
                # Skip binary files and certain file types
                if self._should_skip_file(file_path):
                    continue
                    
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Substitute parameters
                    new_content = self.substitute_parameters(content)
                    
                    # Write back if content changed
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        logger.debug(f"Processed file: {file_path}")
                        
                except Exception as e:
                    logger.warning(f"Failed to process file {file_path}: {e}")
                    
    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be skipped during processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file should be skipped
        """
        # Skip binary files and certain extensions
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.bin'}
        skip_files = {'Make', 'Allwmake', 'Allclean'}
        
        if file_path.suffix.lower() in skip_extensions:
            return True
            
        if file_path.name in skip_files:
            return True
            
        return False
        
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List[str]: List of template names
        """
        templates = []
        
        if self.templates_path.exists():
            for item in self.templates_path.iterdir():
                if item.is_file():
                    templates.append(item.name)
                    
        return sorted(templates)
        
    def list_template_directories(self) -> List[str]:
        """
        List all available template directories.
        
        Returns:
            List[str]: List of template directory names
        """
        directories = []
        
        if self.templates_path.exists():
            for item in self.templates_path.iterdir():
                if item.is_dir():
                    directories.append(item.name)
                    
        return sorted(directories)


class FileBackupManager:
    """
    Manager for file backup and restore operations.
    """
    
    def __init__(self, backup_suffix: str = ".backup"):
        """
        Initialize the backup manager.
        
        Args:
            backup_suffix: Suffix to add to backup files
        """
        self.backup_suffix = backup_suffix
        
    def backup_file(self, file_path: str) -> bool:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            bool: True if backup successful
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False
            
        backup_path = Path(str(file_path) + self.backup_suffix)
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {file_path} -> {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return False
            
    def restore_file(self, file_path: str) -> bool:
        """
        Restore a file from backup.
        
        Args:
            file_path: Path to the file to restore
            
        Returns:
            bool: True if restore successful
        """
        file_path = Path(file_path)
        backup_path = Path(str(file_path) + self.backup_suffix)
        
        if not backup_path.exists():
            logger.warning(f"Backup file does not exist: {backup_path}")
            return False
            
        try:
            shutil.copy2(backup_path, file_path)
            logger.debug(f"Restored file: {backup_path} -> {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore file {file_path}: {e}")
            return False
            
    def cleanup_backup(self, file_path: str) -> bool:
        """
        Remove backup file.
        
        Args:
            file_path: Path to the original file
            
        Returns:
            bool: True if cleanup successful
        """
        backup_path = Path(str(file_path) + self.backup_suffix)
        
        try:
            if backup_path.exists():
                backup_path.unlink()
                logger.debug(f"Removed backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove backup {backup_path}: {e}")
            return False


class PathValidator:
    """
    Validator for file and directory paths.
    """
    
    @staticmethod
    def validate_project_path(path: str) -> bool:
        """
        Validate a project path.
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if path is valid
        """
        path = Path(path)
        
        # Check if path is absolute
        if not path.is_absolute():
            logger.error("Project path must be absolute")
            return False
            
        # Check if path contains invalid characters
        invalid_chars = {'<', '>', ':', '"', '|', '?', '*'}
        if any(char in str(path) for char in invalid_chars):
            logger.error("Project path contains invalid characters")
            return False
            
        # Check if path is too long (Windows limit)
        if len(str(path)) > 260:
            logger.error("Project path is too long")
            return False
            
        return True
        
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """
        Validate a file path.
        
        Args:
            path: Path to validate
            
        Returns:
            bool: True if path is valid
        """
        path = Path(path)
        
        # Check if path is absolute
        if not path.is_absolute():
            logger.error("File path must be absolute")
            return False
            
        # Check parent directory exists
        if not path.parent.exists():
            logger.error(f"Parent directory does not exist: {path.parent}")
            return False
            
        return True
