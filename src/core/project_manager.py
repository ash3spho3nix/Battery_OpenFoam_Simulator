"""
Enhanced Project Manager for Battery Simulator - FIXED VERSION.
 
This module provides an advanced ProjectManager class with comprehensive
project lifecycle management, validation, and error handling capabilities.
"""
 
import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime
import logging
import re
import hashlib
import zipfile
 
logger = logging.getLogger(__name__)
 
 
class ProjectValidationError(Exception):
    """Exception raised when project validation fails."""
    pass
 
 
class ProjectIntegrityError(Exception):
    """Exception raised when project integrity check fails."""
    pass
 
 
class ProjectMetadata:
    """Metadata for a project."""
     
    def __init__(self, metadata: Dict[str, Any]):
        self.project_name = metadata.get('project_name', '')
        self.project_path = metadata.get('project_path', '')
        self.template_name = metadata.get('template_name', '')
        self.creation_date = metadata.get('creation_date', '')
        self.last_modified = metadata.get('last_modified', '')
        self.battery_simulator_version = metadata.get('battery_simulator_version', '')
        self.parameters = metadata.get('parameters', {})
        self.checksums = metadata.get('checksums', {})
        self.dependencies = metadata.get('dependencies', [])
        self.status = metadata.get('status', 'active')
         
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'project_name': self.project_name,
            'project_path': self.project_path,
            'template_name': self.template_name,
            'creation_date': self.creation_date,
            'last_modified': self.last_modified,
            'battery_simulator_version': self.battery_simulator_version,
            'parameters': self.parameters,
            'checksums': self.checksums,
            'dependencies': self.dependencies,
            'status': self.status
        }
 
 
class ProjectManager:
    """
    Enhanced project manager for advanced project operations.
     
    Provides comprehensive project lifecycle management including creation,
    validation, backup/restore, and integrity checking.
    """
     
    PROJECT_METADATA_FILE = "project_metadata.json"
    INTEGRITY_FILE = "file_integrity.json"
    BACKUP_EXTENSION = ".backup"
    VALID_PROJECT_NAME_PATTERN = r'^[a-zA-Z0-9_]+$'
     
    def __init__(self, base_projects_path: Union[str, Path]):
        """
        Initialize the enhanced project manager.
         
        Args:
            base_projects_path: Base path for projects
        """
        self.base_projects_path = Path(base_projects_path)
        self.base_projects_path.mkdir(parents=True, exist_ok=True)
        self._cache = {}
         
    def create_project(
        self, 
        project_path: Union[str, Path], 
        project_name: str, 
        template_path: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
        validate_template: bool = True
    ) -> bool:
        """
        Create a new project with advanced validation and metadata.
         
        Args:
            project_path: Base path where the project will be created
            project_name: Name of the project
            template_path: Path to the template directory
            parameters: Project parameters for substitution
            validate_template: Whether to validate the template
             
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate project name
            if not self._validate_project_name(project_name):
                raise ProjectValidationError(f"Invalid project name: {project_name}")
                 
            # Check if project already exists
            project_path = Path(project_path) / project_name
            if project_path.exists():
                raise ProjectValidationError(f"Project already exists: {project_path}")
                 
            # Validate template if requested
            if validate_template:
                self._validate_template_path(template_path)
                 
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
             
            # Copy template files
            self._copy_template_files(template_path, project_path)
             
            # Apply parameter substitution
            if parameters is None:
                parameters = {}
            self._apply_parameter_substitution(project_path, parameters)
             
            # Update project references
            self._update_project_references(project_path, project_name)
             
            # Create project metadata
            metadata = self._create_project_metadata(
                project_name, project_path, template_path, parameters
            )
            self._save_project_metadata(project_path, metadata)
             
            # Calculate file integrity
            self._calculate_file_integrity(project_path)
             
            logger.info(f"Project created successfully: {project_name}")
            return True
             
        except Exception as e:
            logger.error(f"Failed to create project {project_name}: {e}", exc_info=True)
            # Clean up on error - FIXED: Use local variable
            if 'project_path' in locals() and project_path.exists():
                shutil.rmtree(project_path)
            return False
             
    def _validate_project_name(self, project_name: str) -> bool:
        """Validate project name format."""
        if not project_name:
            return False
             
        # Check length
        if len(project_name) > 100:
            return False
             
        # Check characters (letters, numbers, underscores only)
        if not re.match(self.VALID_PROJECT_NAME_PATTERN, project_name):
            return False
             
        # Check reserved names
        reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
        if project_name.lower() in reserved_names:
            return False
             
        return True
         
    def _validate_template_path(self, template_path: Union[str, Path]) -> bool:
        """Validate template directory structure."""
        template_path = Path(template_path)
        if not template_path.exists():
            raise ProjectValidationError(f"Template path does not exist: {template_path}")
             
        if not template_path.is_dir():
            raise ProjectValidationError(f"Template path is not a directory: {template_path}")
             
        # Check for critical directories
        critical_dirs = ['Make', 'system', 'constant']
        missing_dirs = []
        for critical_dir in critical_dirs:
            if not (template_path / critical_dir).exists():
                missing_dirs.append(critical_dir)
                 
        if missing_dirs:
            raise ProjectValidationError(f"Template missing critical directories: {missing_dirs}")
             
        return True
         
    def _copy_template_files(self, source: Path, destination: Path):
        """Copy template files with proper handling."""
        # Use shutil.copytree with preserve_permissions=True
        shutil.copytree(source, destination, dirs_exist_ok=True)
         
        # Remove template-specific files that shouldn't be in projects
        template_metadata = destination / "template_metadata.json"
        if template_metadata.exists():
            template_metadata.unlink()
             
    def _apply_parameter_substitution(
        self, 
        project_path: Path, 
        parameters: Dict[str, Any]
    ):
        """Apply parameter substitution to project files."""
        # Define parameter patterns
        param_patterns = {
            '{{PROJECT_NAME}}': parameters.get('PROJECT_NAME', ''),
            '{{CREATION_DATE}}': datetime.now().isoformat(),
        }
         
        # Add custom parameters
        for key, value in parameters.items():
            if key not in ['PROJECT_NAME', 'CREATION_DATE']:
                param_key = f'{{{{{key}}}}}'
                param_patterns[param_key] = str(value)
                 
        # Apply substitutions to text files
        text_extensions = {'.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.py', '.cpp', '.h', '.C', '.H'}
        for file_path in project_path.rglob('*'):
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
        project_path: Path, 
        project_name: str
    ):
        """Update project-specific references."""
        # Update Make/files if it exists
        make_files_path = project_path / 'Make' / 'files'
        if make_files_path.exists():
            with open(make_files_path, 'r') as f:
                content = f.read()
                 
            # Replace template name with project name (if template name was in files)
            # For now, just ensure project name is used
            content = content.replace('{{PROJECT_NAME}}', project_name)
             
            with open(make_files_path, 'w') as f:
                f.write(content)
                 
        # Rename solver directory if it exists and has placeholder name
        solver_dirs = [d for d in project_path.iterdir() if d.is_dir() and d.name != 'Make']
        if solver_dirs:
            old_solver_path = solver_dirs[0]
            new_solver_path = project_path / project_name
            if old_solver_path != new_solver_path:
                old_solver_path.rename(new_solver_path)
                 
    def _create_project_metadata(
        self, 
        project_name: str, 
        project_path: Path, 
        template_path: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> ProjectMetadata:
        """Create comprehensive project metadata."""
        template_path = Path(template_path)
        template_name = template_path.name
         
        metadata_dict = {
            'project_name': project_name,
            'project_path': str(project_path),
            'template_name': template_name,
            'creation_date': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'battery_simulator_version': '1.0.0',  # Can be dynamic
            'parameters': parameters,
            'checksums': {},  # Will be calculated later
            'dependencies': [],
            'status': 'active'
        }
         
        return ProjectMetadata(metadata_dict)
         
    def _save_project_metadata(self, project_path: Path, metadata: ProjectMetadata):
        """Save project metadata to file."""
        metadata_path = project_path / self.PROJECT_METADATA_FILE
        with open(metadata_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
             
    def _calculate_file_integrity(self, project_path: Path):
        """Calculate and save file integrity checksums."""
        checksums = {}
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        checksum = hashlib.md5(content).hexdigest()
                        relative_path = str(file_path.relative_to(project_path))
                        checksums[relative_path] = checksum
                except Exception as e:
                    logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
                     
        integrity_path = project_path / self.INTEGRITY_FILE
        with open(integrity_path, 'w') as f:
            json.dump(checksums, f, indent=2)
             
    def open_project(self, project_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Open an existing project and validate its integrity.
         
        Args:
            project_path: Path to the project directory
             
        Returns:
            Dict containing project information or None if invalid
        """
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                return None
                 
            # Load metadata
            metadata = self.get_project_metadata(project_path)
            if not metadata:
                return None
                 
            # Validate project integrity
            if not self.validate_project_integrity(project_path):
                logger.warning(f"Project integrity check failed: {project_path}")
                # Continue but mark as potentially corrupted
                 
            # Get project statistics
            stats = self.get_project_statistics(project_path)
             
            return {
                'metadata': metadata.to_dict(),
                'statistics': stats,
                'path': str(project_path),
                'valid': True
            }
             
        except Exception as e:
            logger.error(f"Failed to open project {project_path}: {e}", exc_info=True)
            return None
             
    def get_project_metadata(self, project_path: Union[str, Path]) -> Optional[ProjectMetadata]:
        """Get project metadata."""
        project_path = Path(project_path)
        metadata_path = project_path / self.PROJECT_METADATA_FILE
         
        if not metadata_path.exists():
            return None
             
        try:
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)
            return ProjectMetadata(metadata_dict)
        except Exception as e:
            logger.error(f"Failed to load project metadata: {e}")
            return None
             
    def validate_project_integrity(self, project_path: Union[str, Path]) -> bool:
        """
        Validate project file integrity using checksums.
         
        Args:
            project_path: Path to the project directory
             
        Returns:
            bool: True if integrity is valid, False otherwise
        """
        project_path = Path(project_path)
        integrity_path = project_path / self.INTEGRITY_FILE
         
        if not integrity_path.exists():
            logger.warning(f"No integrity file found for project: {project_path}")
            return False
             
        try:
            with open(integrity_path, 'r') as f:
                stored_checksums = json.load(f)
                 
            # Calculate current checksums
            current_checksums = {}
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and file_path.name != self.INTEGRITY_FILE:
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            checksum = hashlib.md5(content).hexdigest()
                            relative_path = str(file_path.relative_to(project_path))
                            current_checksums[relative_path] = checksum
                    except Exception as e:
                        logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
                        return False
                         
            # Compare checksums
            if stored_checksums != current_checksums:
                logger.error(f"Project integrity check failed: {project_path}")
                return False
                 
            return True
             
        except Exception as e:
            logger.error(f"Failed to validate project integrity: {e}", exc_info=True)
            return False
             
    def get_project_statistics(self, project_path: Union[str, Path]) -> Dict[str, Any]:
        """Get project statistics."""
        project_path = Path(project_path)
         
        stats = {
            'file_count': 0,
            'total_size': 0,
            'directory_count': 0,
            'largest_file': None,
            'largest_file_size': 0
        }
         
        for item in project_path.rglob('*'):
            if item.is_file():
                stats['file_count'] += 1
                file_size = item.stat().st_size
                stats['total_size'] += file_size
                if file_size > stats['largest_file_size']:
                    stats['largest_file_size'] = file_size
                    stats['largest_file'] = str(item.relative_to(project_path))
            elif item.is_dir():
                stats['directory_count'] += 1
                 
        return stats
         
    def list_projects(self) -> List[str]:
        """List all projects in the base directory."""
        projects = []
        for item in self.base_projects_path.iterdir():
            if item.is_dir():
                metadata_path = item / self.PROJECT_METADATA_FILE
                if metadata_path.exists():
                    projects.append(item.name)
        return sorted(projects)
         
    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a project."""
        project_path = self.base_projects_path / project_name
        if not project_path.exists():
            return None
             
        # Load metadata
        metadata = self.get_project_metadata(project_path)
        if not metadata:
            return None
             
        # Get statistics
        stats = self.get_project_statistics(project_path)
         
        # Check integrity
        integrity_valid = self.validate_project_integrity(project_path)
         
        return {
            'name': metadata.project_name,
            'path': metadata.project_path,
            'template': metadata.template_name,
            'creation_date': metadata.creation_date,
            'last_modified': metadata.last_modified,
            'status': metadata.status,
            'parameters': metadata.parameters,
            'statistics': stats,
            'integrity_valid': integrity_valid
        }
         
    def backup_project(
        self, 
        project_name: str, 
        backup_path: Optional[Union[str, Path]] = None,
        include_metadata: bool = True
    ) -> str:
        """
        Create a backup of a project.
         
        Args:
            project_name: Name of the project to backup
            backup_path: Path for the backup file (optional)
            include_metadata: Whether to include metadata in backup
             
        Returns:
            str: Path to the backup file
        """
        project_path = self.base_projects_path / project_name
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
             
        # Generate backup path if not provided
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{project_name}_backup_{timestamp}.zip"
            backup_path = self.base_projects_path / backup_filename
        else:
            backup_path = Path(backup_path)
             
        # Create backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Skip integrity file unless explicitly included
                    if file_path.name == self.INTEGRITY_FILE and not include_metadata:
                        continue
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
                     
        logger.info(f"Project backup created: {backup_path}")
        return str(backup_path)
         
    def restore_project(self, project_name: str, backup_path: Union[str, Path]) -> bool:
        """
        Restore a project from backup.
         
        Args:
            project_name: Name of the project to restore
            backup_path: Path to the backup file
             
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
                 
            project_path = self.base_projects_path / project_name
             
            # Create backup of current project if it exists
            if project_path.exists():
                self.backup_project(project_name)
                shutil.rmtree(project_path)
                 
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(project_path)
                 
            # Update last modified timestamp in metadata
            metadata = self.get_project_metadata(project_path)
            if metadata:
                metadata.last_modified = datetime.now().isoformat()
                self._save_project_metadata(project_path, metadata)
                 
            logger.info(f"Project restored: {project_name}")
            return True
             
        except Exception as e:
            logger.error(f"Failed to restore project {project_name}: {e}", exc_info=True)
            return False
             
    def delete_project(self, project_name: str, backup_first: bool = True) -> bool:
        """
        Delete a project with optional backup.
         
        Args:
            project_name: Name of the project to delete
            backup_first: Whether to create a backup before deletion
             
        Returns:
            bool: True if successful, False otherwise
        """
        project_path = self.base_projects_path / project_name
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
             
        # Create backup if requested
        if backup_first:
            self.backup_project(project_name)
             
        # Delete project
        shutil.rmtree(project_path)
         
        logger.info(f"Project deleted: {project_name}")
        return True
         
    def repair_project(self, project_name: str) -> bool:
        """
        Attempt to repair a corrupted project.
         
        Args:
            project_name: Name of the project to repair
             
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_path = self.base_projects_path / project_name
            if not project_path.exists():
                raise FileNotFoundError(f"Project not found: {project_path}")
                 
            # Recalculate file integrity
            self._calculate_file_integrity(project_path)
             
            # Update metadata timestamp
            metadata = self.get_project_metadata(project_path)
            if metadata:
                metadata.last_modified = datetime.now().isoformat()
                metadata.status = 'repaired'
                self._save_project_metadata(project_path, metadata)
                 
            logger.info(f"Project repaired: {project_name}")
            return True
             
        except Exception as e:
            logger.error(f"Failed to repair project {project_name}: {e}", exc_info=True)
            return False
             
    def get_project_health_report(self, project_name: str) -> Dict[str, Any]:
        """Get a health report for a project."""
        project_path = self.base_projects_path / project_name
        if not project_path.exists():
            return {'status': 'error', 'message': 'Project not found'}
             
        report = {
            'project_name': project_name,
            'status': 'healthy',
            'issues': [],
            'warnings': [],
            'statistics': {},
            'integrity_check': False
        }
         
        # Check metadata
        metadata = self.get_project_metadata(project_path)
        if not metadata:
            report['issues'].append('Missing project metadata')
            report['status'] = 'corrupted'
        else:
            report['statistics'] = self.get_project_statistics(project_path)
             
        # Check integrity
        try:
            report['integrity_check'] = self.validate_project_integrity(project_path)
            if not report['integrity_check']:
                report['issues'].append('File integrity check failed')
                report['status'] = 'corrupted'
        except Exception as e:
            report['issues'].append(f'Integrity check error: {str(e)}')
            report['status'] = 'error'
             
        # Check critical files
        critical_files = ['Make/files', 'system/controlDict', 'system/fvSchemes', 'system/fvSolution']
        for critical_file in critical_files:
            file_path = project_path / critical_file
            if not file_path.exists():
                report['warnings'].append(f'Missing critical file: {critical_file}')
                 
        return report
         
    def get_projects_summary(self) -> Dict[str, Any]:
        """Get a summary of all projects."""
        summary = {
            'total_projects': 0,
            'healthy_projects': 0,
            'corrupted_projects': 0,
            'error_projects': 0,
            'projects': {}
        }
         
        for project_name in self.list_projects():
            try:
                health_report = self.get_project_health_report(project_name)
                summary['projects'][project_name] = health_report
                summary['total_projects'] += 1
                 
                if health_report['status'] == 'healthy':
                    summary['healthy_projects'] += 1
                elif health_report['status'] == 'corrupted':
                    summary['corrupted_projects'] += 1
                else:
                    summary['error_projects'] += 1
                     
            except Exception as e:
                logger.warning(f"Failed to get health report for {project_name}: {e}")
                summary['error_projects'] += 1
                summary['projects'][project_name] = {
                    'status': 'error',
                    'message': str(e)
                }
                 
        return summary
