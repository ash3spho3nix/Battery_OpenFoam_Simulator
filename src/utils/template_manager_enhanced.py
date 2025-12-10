"""
Enhanced Template Manager for Battery Simulator.

This module provides an advanced TemplateManager class with comprehensive
template management capabilities including validation, versioning, and
advanced file operations.
"""

import os
import shutil
import json
import hashlib
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class TemplateValidationError(Exception):
    """Exception raised when template validation fails."""
    pass


class TemplateVersionError(Exception):
    """Exception raised when template version is incompatible."""
    pass


class TemplateMetadata:
    """Metadata for a template."""
    
    def __init__(self, metadata: Dict[str, Any]):
        self.name = metadata.get('name', '')
        self.version = metadata.get('version', '1.0.0')
        self.description = metadata.get('description', '')
        self.author = metadata.get('author', '')
        self.created_date = metadata.get('created_date', '')
        self.compatible_versions = metadata.get('compatible_versions', [])
        self.required_files = metadata.get('required_files', [])
        self.optional_files = metadata.get('optional_files', [])
        self.parameters = metadata.get('parameters', {})
        self.dependencies = metadata.get('dependencies', [])
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'created_date': self.created_date,
            'compatible_versions': self.compatible_versions,
            'required_files': self.required_files,
            'optional_files': self.optional_files,
            'parameters': self.parameters,
            'dependencies': self.dependencies
        }


class TemplateManager:
    """
    Enhanced template manager for advanced template operations.
    
    Provides comprehensive template management including validation,
    versioning, backup/restore, and advanced file operations.
    """
    
    METADATA_FILE = "template_metadata.json"
    BACKUP_EXTENSION = ".backup"
    VERSION_PATTERN = r'^\d+\.\d+\.\d+$'
    
    def __init__(self, templates_path: Union[str, Path]):
        """
        Initialize the enhanced template manager.
        
        Args:
            templates_path: Path to the templates directory
        """
        self.templates_path = Path(templates_path)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        
    def create_template(
        self, 
        template_name: str, 
        source_path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new template from an existing directory.
        
        Args:
            template_name: Name of the new template
            source_path: Path to the source directory
            metadata: Template metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate source path
            source_path = Path(source_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {source_path}")
                
            # Create template directory
            template_path = self.templates_path / template_name
            if template_path.exists():
                raise FileExistsError(f"Template already exists: {template_path}")
                
            # Copy source to template directory
            shutil.copytree(source_path, template_path)
            
            # Create metadata
            if metadata is None:
                metadata = self._generate_metadata(template_name, source_path)
            else:
                metadata = self._validate_and_complete_metadata(metadata, template_name)
                
            # Save metadata
            self._save_metadata(template_path, metadata)
            
            # Validate template
            self.validate_template(template_name)
            
            logger.info(f"Template created successfully: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template {template_name}: {e}", exc_info=True)
            # Clean up on error
            if template_path.exists():
                shutil.rmtree(template_path)
            return False
            
    def _generate_metadata(self, template_name: str, source_path: Path) -> Dict[str, Any]:
        """Generate metadata for a template."""
        return {
            'name': template_name,
            'version': '1.0.0',
            'description': f'Template {template_name}',
            'author': 'Battery Simulator',
            'created_date': datetime.now().isoformat(),
            'compatible_versions': ['1.0.0'],
            'required_files': self._scan_required_files(source_path),
            'optional_files': self._scan_optional_files(source_path),
            'parameters': self._scan_parameters(source_path),
            'dependencies': []
        }
        
    def _validate_and_complete_metadata(self, metadata: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Validate and complete template metadata."""
        # Validate version format
        version = metadata.get('version', '1.0.0')
        if not re.match(self.VERSION_PATTERN, version):
            raise TemplateValidationError(f"Invalid version format: {version}")
            
        # Set default values
        metadata.setdefault('name', template_name)
        metadata.setdefault('description', f'Template {template_name}')
        metadata.setdefault('author', 'Battery Simulator')
        metadata.setdefault('created_date', datetime.now().isoformat())
        metadata.setdefault('compatible_versions', ['1.0.0'])
        metadata.setdefault('required_files', [])
        metadata.setdefault('optional_files', [])
        metadata.setdefault('parameters', {})
        metadata.setdefault('dependencies', [])
        
        return metadata
        
    def _scan_required_files(self, source_path: Path) -> List[str]:
        """Scan for required files in template."""
        required_files = []
        critical_dirs = ['Make', 'system', 'constant', '0']
        
        for critical_dir in critical_dirs:
            dir_path = source_path / critical_dir
            if dir_path.exists():
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        relative_path = str(file_path.relative_to(source_path))
                        required_files.append(relative_path)
                        
        return required_files
        
    def _scan_optional_files(self, source_path: Path) -> List[str]:
        """Scan for optional files in template."""
        optional_files = []
        # Add logic to identify optional files
        # For now, return empty list
        return optional_files
        
    def _scan_parameters(self, source_path: Path) -> Dict[str, Any]:
        """Scan for parameters in template files."""
        parameters = {}
        parameter_patterns = {
            'project_name': r'\{\{PROJECT_NAME\}\}',
            'module_name': r'\{\{MODULE_NAME\}\}',
            'solver_name': r'\{\{SOLVER_NAME\}\}',
        }
        
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for param_name, pattern in parameter_patterns.items():
                        if re.search(pattern, content):
                            if param_name not in parameters:
                                parameters[param_name] = {
                                    'description': f'{param_name} parameter',
                                    'pattern': pattern,
                                    'files': []
                                }
                            parameters[param_name]['files'].append(str(file_path.relative_to(source_path)))
                            
                except Exception as e:
                    logger.warning(f"Failed to scan file {file_path}: {e}")
                    
        return parameters
        
    def validate_template(self, template_name: str) -> bool:
        """
        Validate a template for completeness and correctness.
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            bool: True if valid, raises exception otherwise
        """
        template_path = self.templates_path / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        # Load metadata
        metadata = self.get_template_metadata(template_name)
        
        # Check required files
        missing_files = []
        for required_file in metadata.required_files:
            file_path = template_path / required_file
            if not file_path.exists():
                missing_files.append(required_file)
                
        if missing_files:
            raise TemplateValidationError(f"Missing required files: {missing_files}")
            
        # Validate metadata
        self._validate_metadata(metadata)
        
        # Check file integrity
        self._validate_file_integrity(template_path, metadata)
        
        logger.info(f"Template validation successful: {template_name}")
        return True
        
    def _validate_metadata(self, metadata: TemplateMetadata):
        """Validate template metadata."""
        if not metadata.name:
            raise TemplateValidationError("Template name is required")
            
        if not re.match(self.VERSION_PATTERN, metadata.version):
            raise TemplateValidationError(f"Invalid version format: {metadata.version}")
            
        # Check compatibility (can be extended based on application version)
        # For now, just validate format
        
    def _validate_file_integrity(self, template_path: Path, metadata: TemplateMetadata):
        """Validate file integrity using checksums."""
        # For now, just check that files exist and are readable
        # Can be extended to include checksum validation
        for required_file in metadata.required_files:
            file_path = template_path / required_file
            if not file_path.exists():
                raise TemplateValidationError(f"Required file missing: {required_file}")
            if not os.access(file_path, os.R_OK):
                raise TemplateValidationError(f"Required file not readable: {required_file}")
                
    def get_template_metadata(self, template_name: str) -> TemplateMetadata:
        """
        Get metadata for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            TemplateMetadata: Template metadata
        """
        if template_name in self._cache:
            return self._cache[template_name]
            
        metadata_path = self.templates_path / template_name / self.METADATA_FILE
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
            
        with open(metadata_path, 'r') as f:
            metadata_dict = json.load(f)
            
        metadata = TemplateMetadata(metadata_dict)
        self._cache[template_name] = metadata
        return metadata
        
    def list_templates(self) -> List[str]:
        """List all available templates."""
        templates = []
        for item in self.templates_path.iterdir():
            if item.is_dir():
                metadata_path = item / self.METADATA_FILE
                if metadata_path.exists():
                    templates.append(item.name)
        return sorted(templates)
        
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get detailed information about a template."""
        metadata = self.get_template_metadata(template_name)
        template_path = self.templates_path / template_name
        
        # Calculate statistics
        file_count = sum(1 for _ in template_path.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in template_path.rglob('*') if f.is_file())
        
        return {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'author': metadata.author,
            'created_date': metadata.created_date,
            'file_count': file_count,
            'total_size': total_size,
            'required_files': metadata.required_files,
            'optional_files': metadata.optional_files,
            'parameters': metadata.parameters,
            'dependencies': metadata.dependencies
        }
        
    def create_project_from_template(
        self, 
        template_name: str, 
        project_path: Union[str, Path], 
        project_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new project from template with advanced features.
        
        Args:
            template_name: Name of the template to use
            project_path: Path where the project should be created
            project_name: Name of the project
            parameters: Additional parameters for substitution
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate template
            self.validate_template(template_name)
            
            # Check project path
            project_path = Path(project_path)
            project_dir = project_path / project_name
            if project_dir.exists():
                raise FileExistsError(f"Project already exists: {project_dir}")
                
            # Create project directory
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy template files
            template_path = self.templates_path / template_name
            self._copy_template_files(template_path, project_dir)
            
            # Apply parameter substitution
            if parameters is None:
                parameters = {}
            parameters.update({
                'PROJECT_NAME': project_name,
                'TEMPLATE_NAME': template_name,
                'CREATION_DATE': datetime.now().isoformat()
            })
            self._apply_parameter_substitution(project_dir, parameters)
            
            # Update file references
            self._update_project_references(project_dir, project_name, template_name)
            
            # Create project metadata
            self._create_project_metadata(project_dir, template_name, project_name, parameters)
            
            logger.info(f"Project created successfully: {project_name} from template {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project {project_name}: {e}", exc_info=True)
            # Clean up on error
            if project_dir.exists():
                shutil.rmtree(project_dir)
            return False
            
    def _copy_template_files(self, source: Path, destination: Path):
        """Copy template files to destination with preservation of attributes."""
        # Use shutil.copytree with preserve_permissions=True
        shutil.copytree(source, destination, dirs_exist_ok=True)
        
        # Remove metadata file from project (not needed in project)
        metadata_path = destination / self.METADATA_FILE
        if metadata_path.exists():
            metadata_path.unlink()
            
    def _apply_parameter_substitution(
        self, 
        project_dir: Path, 
        parameters: Dict[str, Any]
    ):
        """Apply parameter substitution to project files."""
        # Define parameter patterns
        param_patterns = {
            '{{PROJECT_NAME}}': parameters.get('PROJECT_NAME', ''),
            '{{TEMPLATE_NAME}}': parameters.get('TEMPLATE_NAME', ''),
            '{{CREATION_DATE}}': parameters.get('CREATION_DATE', ''),
        }
        
        # Add custom parameters
        for key, value in parameters.items():
            if key not in ['PROJECT_NAME', 'TEMPLATE_NAME', 'CREATION_DATE']:
                param_key = f'{{{{{key}}}}}'
                param_patterns[param_key] = str(value)
                
        # Apply substitutions to text files
        text_extensions = {'.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.py', '.cpp', '.h', '.C', '.H'}
        for file_path in project_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Apply substitutions
                    for pattern, replacement in param_patterns.items():
                        content = content.replace(pattern, replacement)
                        
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as e:
                    logger.warning(f"Failed to process file {file_path}: {e}")
                    
    def _update_project_references(
        self, 
        project_dir: Path, 
        project_name: str, 
        template_name: str
    ):
        """Update project-specific references."""
        # Update Make/files if it exists
        make_files_path = project_dir / 'Make' / 'files'
        if make_files_path.exists():
            with open(make_files_path, 'r') as f:
                content = f.read()
                
            # Replace template name with project name
            content = content.replace(template_name, project_name)
            
            with open(make_files_path, 'w') as f:
                f.write(content)
                
        # Rename solver directory if it exists
        solver_dirs = [d for d in project_dir.iterdir() if d.is_dir() and d.name != 'Make']
        if solver_dirs:
            old_solver_path = solver_dirs[0]
            new_solver_path = project_dir / project_name
            if old_solver_path != new_solver_path:
                old_solver_path.rename(new_solver_path)
                
    def _create_project_metadata(
        self, 
        project_dir: Path, 
        template_name: str, 
        project_name: str,
        parameters: Dict[str, Any]
    ):
        """Create project metadata file."""
        project_metadata = {
            'project_name': project_name,
            'template_name': template_name,
            'creation_date': datetime.now().isoformat(),
            'parameters': parameters,
            'battery_simulator_version': '1.0.0'  # Can be dynamic
        }
        
        metadata_path = project_dir / 'project_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(project_metadata, f, indent=2)
            
    def backup_template(self, template_name: str, backup_path: Optional[Union[str, Path]] = None) -> str:
        """
        Create a backup of a template.
        
        Args:
            template_name: Name of the template to backup
            backup_path: Path for the backup file (optional)
            
        Returns:
            str: Path to the backup file
        """
        template_path = self.templates_path / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        # Generate backup path if not provided
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{template_name}_backup_{timestamp}.zip"
            backup_path = self.templates_path / backup_filename
        else:
            backup_path = Path(backup_path)
            
        # Create backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in template_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(template_path)
                    zipf.write(file_path, arcname)
                    
        logger.info(f"Template backup created: {backup_path}")
        return str(backup_path)
        
    def restore_template(self, template_name: str, backup_path: Union[str, Path]) -> bool:
        """
        Restore a template from backup.
        
        Args:
            template_name: Name of the template to restore
            backup_path: Path to the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
        template_path = self.templates_path / template_name
        
        # Create backup of current template if it exists
        if template_path.exists():
            self.backup_template(template_name)
            shutil.rmtree(template_path)
            
        # Extract backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(template_path)
            
        logger.info(f"Template restored: {template_name}")
        return True
        
    def export_template(self, template_name: str, export_path: Union[str, Path]) -> bool:
        """
        Export a template to a compressed archive.
        
        Args:
            template_name: Name of the template to export
            export_path: Path for the exported archive
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            template_path = self.templates_path / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
                
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create export archive
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in template_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(template_path)
                        zipf.write(file_path, arcname)
                        
            logger.info(f"Template exported: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export template {template_name}: {e}", exc_info=True)
            return False
            
    def import_template(self, import_path: Union[str, Path], template_name: Optional[str] = None) -> bool:
        """
        Import a template from a compressed archive.
        
        Args:
            import_path: Path to the template archive
            template_name: Name for the imported template (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
                
            # Extract archive to temporary location
            temp_dir = self.templates_path / "temp_import"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            with zipfile.ZipFile(import_path, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Determine template name
            if template_name is None:
                # Use the first directory name in the archive
                subdirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if subdirs:
                    template_name = subdirs[0].name
                else:
                    template_name = import_path.stem
                    
            # Move to templates directory
            template_path = self.templates_path / template_name
            if template_path.exists():
                shutil.rmtree(template_path)
            shutil.move(str(temp_dir), str(template_path))
            
            # Validate imported template
            self.validate_template(template_name)
            
            logger.info(f"Template imported: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import template: {e}", exc_info=True)
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
            
    def delete_template(self, template_name: str, backup_first: bool = True) -> bool:
        """
        Delete a template with optional backup.
        
        Args:
            template_name: Name of the template to delete
            backup_first: Whether to create a backup before deletion
            
        Returns:
            bool: True if successful, False otherwise
        """
        template_path = self.templates_path / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        # Create backup if requested
        if backup_first:
            self.backup_template(template_name)
            
        # Delete template
        shutil.rmtree(template_path)
        
        # Clear cache
        if template_name in self._cache:
            del self._cache[template_name]
            
        logger.info(f"Template deleted: {template_name}")
        return True
        
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about all templates."""
        stats = {
            'total_templates': 0,
            'total_files': 0,
            'total_size': 0,
            'templates': {}
        }
        
        for template_name in self.list_templates():
            try:
                info = self.get_template_info(template_name)
                stats['templates'][template_name] = info
                stats['total_templates'] += 1
                stats['total_files'] += info['file_count']
                stats['total_size'] += info['total_size']
            except Exception as e:
                logger.warning(f"Failed to get info for template {template_name}: {e}")
                
        return stats
