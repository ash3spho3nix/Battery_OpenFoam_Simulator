"""
Enhanced Project Manager with Advanced Safety Features - PRIORITY 2 IMPLEMENTED.

This module provides an enhanced ProjectManager with advanced template validation,
progress tracking, and improved error recovery mechanisms.
"""

import os
import json
import shutil
import zipfile
import tempfile
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime
import re
import hashlib

from src.utils.file_operations_enhanced import (
    EnhancedTemplateManager, 
    TemplateProgressTracker,
    FileOperationError
)

logger = logging.getLogger(__name__)


class ProjectValidationError(Exception):
    """Exception raised when project validation fails."""
    pass


class ProjectIntegrityError(Exception):
    """Exception raised when project integrity check fails."""
    pass


class ProjectMetadata:
    """Enhanced metadata for a project with additional safety information."""
    
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
        self.template_version = metadata.get('template_version', '1.0.0')
        self.operation_history = metadata.get('operation_history', [])
        self.backup_count = metadata.get('backup_count', 0)
        self.file_permissions = metadata.get('file_permissions', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enhanced safety information."""
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
            'status': self.status,
            'template_version': self.template_version,
            'operation_history': self.operation_history,
            'backup_count': self.backup_count,
            'file_permissions': self.file_permissions
        }


class EnhancedProjectManager:
    """
    Enhanced Project Manager with advanced safety features.
    
    Provides enterprise-grade project lifecycle management with comprehensive
    validation, progress tracking, and error recovery.
    """
    
    PROJECT_METADATA_FILE = "project_metadata.json"
    INTEGRITY_FILE = "file_integrity.json"
    BACKUP_EXTENSION = ".backup"
    VALID_PROJECT_NAME_PATTERN = r'^[a-zA-Z0-9_]+$'
    OPERATION_TIMEOUT = 300  # 5 minutes timeout for operations
    
    def __init__(
        self, 
        base_projects_path: Union[str, Path], 
        templates_path: Union[str, Path] = None,
        progress_tracker: Optional[TemplateProgressTracker] = None
    ):
        """
        Initialize the enhanced project manager with safety features.
        
        Args:
            base_projects_path: Base path for projects
            templates_path: Path to templates directory
            progress_tracker: Optional progress tracker for operations
        """
        self.base_projects_path = Path(base_projects_path)
        self.base_projects_path.mkdir(parents=True, exist_ok=True)
        
        # Set templates path - default to src/resources/templates
        if templates_path is None:
            templates_path = Path(__file__).parent.parent / "resources" / "templates"
        self.templates_path = Path(templates_path)
        
        # Initialize enhanced template manager with progress tracking
        self.template_manager = EnhancedTemplateManager(
            str(self.templates_path),
            progress_tracker
        )
        self.progress_tracker = progress_tracker or TemplateProgressTracker()
        self._cache = {}
        self._operation_lock = threading.Lock()
        self._validation_cache = {}
        
    def create_project_safe(
        self, 
        project_path: Union[str, Path], 
        project_name: str, 
        template_name: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
        validate_template: bool = True,
        create_backup: bool = True
    ) -> bool:
        """
        Create a new project with enhanced safety features and progress tracking.
        
        Args:
            project_path: Base path where the project will be created
            project_name: Name of the project
            template_name: Name of the template or full path
            parameters: Project parameters for substitution
            validate_template: Whether to validate the template
            create_backup: Whether to create a backup before operation
            
        Returns:
            bool: True if successful, False otherwise
        """
        with self._operation_lock:
            return self._create_project_with_safety(
                project_path, project_name, template_name, 
                parameters, validate_template, create_backup
            )
    
    def _create_project_with_safety(
        self, 
        project_path: Union[str, Path], 
        project_name: str, 
        template_name: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None,
        validate_template: bool = True,
        create_backup: bool = True
    ) -> bool:
        """Create project with comprehensive safety measures."""
        start_time = time.time()
        operation_id = f"{project_name}_{int(start_time)}"
        
        try:
            # Resolve template path
            template_path = self._resolve_template_path(template_name)
            logger.info(f"Starting project creation: {project_name} from {template_path.name}")
            
            # Start progress tracking
            self.progress_tracker.start_operation(f"Creating project {project_name}")
            
            # Validate project name
            if not self._validate_project_name(project_name):
                raise ProjectValidationError(f"Invalid project name: {project_name}")
                
            # Check if project already exists
            project_path = Path(project_path) / project_name
            if project_path.exists():
                raise ProjectValidationError(f"Project already exists: {project_path}")
                
            # Validate template with enhanced checks
            if validate_template:
                validation_result = self._validate_template_enhanced(template_path)
                if not validation_result['valid']:
                    raise ProjectValidationError(
                        f"Template validation failed: {validation_result['issues']}"
                    )
                
                # Log template information
                logger.info(f"Template validated: {validation_result['template_type']}")
                logger.info(f"Template files: {validation_result['file_count']}")
                logger.info(f"Template size: {validation_result['size']} bytes")
                
            # Calculate total operations for progress tracking
            total_files = sum(len(files) for _, _, files in os.walk(template_path))
            self.progress_tracker.set_total_operations(total_files + 5)  # +5 for metadata, integrity, etc.
            
            # Create project directory with proper permissions
            project_path.mkdir(parents=True, exist_ok=True)
            self._set_project_permissions(project_path)
            self.progress_tracker.update_progress(1)
            
            # Copy template files with atomic operations
            if not self.template_manager.copy_template_directory_atomic(
                template_path.name, str(project_path)
            ):
                raise FileOperationError("Template copying failed")
            self.progress_tracker.update_progress(1)
            
            # Apply parameter substitution
            if parameters is None:
                parameters = {}
            self._apply_parameter_substitution_safe(project_path, parameters)
            self.progress_tracker.update_progress(1)
            
            # Update project references
            self._update_project_references_safe(project_path, project_name)
            self.progress_tracker.update_progress(1)
            
            # Create enhanced project metadata
            metadata = self._create_enhanced_metadata(
                project_name, project_path, template_path, parameters, operation_id
            )
            self._save_project_metadata(project_path, metadata)
            self.progress_tracker.update_progress(1)
            
            # Calculate file integrity with enhanced checksums
            self._calculate_enhanced_integrity(project_path)
            self.progress_tracker.update_progress(1)
            
            # Create initial backup if requested
            if create_backup:
                self._create_initial_backup(project_path, project_name)
                self.progress_tracker.update_progress(1)
            
            # Complete operation
            elapsed_time = time.time() - start_time
            logger.info(f"Project created successfully: {project_name} (took {elapsed_time:.2f}s)")
            self.progress_tracker.complete_operation(True)
            return True
            
        except Exception as e:
            logger.error(f"Project creation failed for {project_name}: {e}", exc_info=True)
            self.progress_tracker.fail_operation(str(e))
            
            # Clean up on error
            if 'project_path' in locals() and project_path.exists():
                try:
                    shutil.rmtree(project_path)
                    logger.info(f"Cleaned up failed project: {project_path}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up project: {cleanup_error}")
                    
            return False
    
    def _validate_template_enhanced(self, template_path: Path) -> Dict[str, Any]:
        """Enhanced template validation with detailed analysis."""
        if template_path in self._validation_cache:
            return self._validation_cache[template_path]
            
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'critical_files': [],
            'openfoam_structure': False,
            'template_type': 'unknown',
            'file_count': 0,
            'size': 0,
            'dependencies': [],
            'compatibility': {}
        }
        
        try:
            if not template_path.exists():
                validation_result['valid'] = False
                validation_result['issues'].append(f"Template path does not exist: {template_path}")
                return validation_result
                
            if not template_path.is_dir():
                validation_result['valid'] = False
                validation_result['issues'].append(f"Template path is not a directory: {template_path}")
                return validation_result
            
            # Calculate statistics
            total_size = 0
            file_count = 0
            for item in template_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                    
            validation_result['file_count'] = file_count
            validation_result['size'] = total_size
            
            # Check critical directories
            critical_dirs = ['system', 'constant']
            for critical_dir in critical_dirs:
                if (template_path / critical_dir).exists():
                    validation_result['critical_files'].append(critical_dir)
                else:
                    validation_result['warnings'].append(f"Missing critical directory: {critical_dir}")
            
            # Check OpenFOAM files
            openfoam_files = ['blockMeshDict', 'controlDict', 'fvSchemes', 'fvSolution']
            openfoam_count = 0
            for file in openfoam_files:
                if (template_path / 'system' / file).exists():
                    openfoam_count += 1
                    
            validation_result['openfoam_structure'] = openfoam_count >= 3
            if not validation_result['openfoam_structure']:
                validation_result['warnings'].append("Template may not be a complete OpenFOAM case")
            
            # Determine template type
            if (template_path / 'SPMFoam').exists():
                validation_result['template_type'] = 'SPM'
            elif (template_path / 'halfCellFoam').exists():
                validation_result['template_type'] = 'halfCell'
            elif (template_path / 'fullCellFoam').exists():
                validation_result['template_type'] = 'fullCell'
            else:
                validation_result['template_type'] = 'generic'
                
            # Check dependencies
            self._check_template_dependencies(template_path, validation_result)
            
            # Check compatibility
            self._check_template_compatibility(template_path, validation_result)
            
            # Final validation
            if validation_result['template_type'] != 'generic':
                validation_result['valid'] = True
            else:
                validation_result['issues'].append("Unknown template type")
                validation_result['valid'] = False
                
        except Exception as e:
            logger.error(f"Enhanced template validation failed: {e}")
            validation_result['issues'].append(f"Validation error: {str(e)}")
            validation_result['valid'] = False
            
        # Cache result
        self._validation_cache[template_path] = validation_result
        return validation_result
    
    def _check_template_dependencies(self, template_path: Path, validation_result: Dict[str, Any]):
        """Check template dependencies and requirements."""
        dependencies = []
        
        # Check for solver files
        solver_dirs = ['SPMFoam', 'halfCellFoam', 'fullCellFoam']
        for solver_dir in solver_dirs:
            if (template_path / solver_dir).exists():
                dependencies.append(f"solver_{solver_dir}")
                
        # Check for required OpenFOAM files
        required_files = [
            'system/controlDict',
            'system/fvSchemes', 
            'system/fvSolution'
        ]
        for file_path in required_files:
            if (template_path / file_path).exists():
                dependencies.append(f"required_{file_path.replace('/', '_')}")
                
        validation_result['dependencies'] = dependencies
    
    def _check_template_compatibility(self, template_path: Path, validation_result: Dict[str, Any]):
        """Check template compatibility with current system."""
        compatibility = {
            'openfoam_version': 'unknown',
            'platform_compatible': True,
            'python_version': 'unknown'
        }
        
        # Check for version files
        version_files = ['VERSION', 'version.txt', 'template_version.json']
        for version_file in version_files:
            if (template_path / version_file).exists():
                try:
                    with open(template_path / version_file, 'r') as f:
                        content = f.read().strip()
                        compatibility['openfoam_version'] = content
                        break
                except Exception:
                    pass
        
        # Check platform compatibility
        import sys
        if sys.platform == 'win32':
            # Check for Windows-specific files
            if not (template_path / 'Allwmake.win').exists() and not (template_path / 'Make').exists():
                compatibility['platform_compatible'] = False
                validation_result['warnings'].append("Template may not be Windows-compatible")
                
        validation_result['compatibility'] = compatibility
    
    def _apply_parameter_substitution_safe(
        self, 
        project_path: Path, 
        parameters: Dict[str, Any]
    ):
        """Apply parameter substitution with enhanced safety."""
        try:
            # Define parameter patterns with validation
            param_patterns = {
                '{{PROJECT_NAME}}': parameters.get('PROJECT_NAME', ''),
                '{{CREATION_DATE}}': datetime.now().isoformat(),
                '{{PROJECT_PATH}}': str(project_path),
                '{{TEMPLATE_NAME}}': parameters.get('TEMPLATE_NAME', ''),
            }
            
            # Add custom parameters with validation
            for key, value in parameters.items():
                if key not in ['PROJECT_NAME', 'CREATION_DATE', 'PROJECT_PATH', 'TEMPLATE_NAME']:
                    # Validate parameter value
                    if self._validate_parameter_value(key, value):
                        param_key = f'{{{{{key}}}}}'
                        param_patterns[param_key] = str(value)
                    else:
                        logger.warning(f"Invalid parameter value for {key}: {value}")
                        validation_result['warnings'].append(f"Invalid parameter: {key}")
                        
            # Apply substitutions to text files with backup
            text_extensions = {'.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.py', '.cpp', '.h', '.C', '.H'}
            backup_files = []
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                    try:
                        # Create backup before modification
                        backup_path = file_path.with_suffix(f"{file_path.suffix}.bak")
                        shutil.copy2(file_path, backup_path)
                        backup_files.append((file_path, backup_path))
                        
                        # Read and modify content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Apply substitutions
                        for pattern, replacement in param_patterns.items():
                            content = content.replace(pattern, replacement)
                            
                        # Write modified content
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_path}: {e}")
                        # Restore from backup on error
                        if backup_files:
                            for original, backup in backup_files:
                                if original == file_path:
                                    shutil.move(str(backup), str(original))
                                    break
                                    
        except Exception as e:
            logger.error(f"Parameter substitution failed: {e}")
            raise FileOperationError(f"Parameter substitution failed: {e}")
    
    def _validate_parameter_value(self, key: str, value: Any) -> bool:
        """Validate parameter value based on type and constraints."""
        # Basic validation rules
        validation_rules = {
            'PROJECT_NAME': {'type': str, 'min_length': 3, 'max_length': 50},
            'PROJECT_PATH': {'type': str, 'pattern': r'^[a-zA-Z0-9_/.-]+$'},
            'TEMPLATE_NAME': {'type': str, 'min_length': 1, 'max_length': 100},
        }
        
        if key in validation_rules:
            rules = validation_rules[key]
            
            # Type check
            if 'type' in rules and not isinstance(value, rules['type']):
                return False
                
            # Length check
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                return False
                
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                return False
                
            # Pattern check
            if 'pattern' in rules and not re.match(rules['pattern'], str(value)):
                return False
                
        return True
    
    def _create_enhanced_metadata(
        self, 
        project_name: str, 
        project_path: Path, 
        template_path: Path,
        parameters: Dict[str, Any],
        operation_id: str
    ) -> ProjectMetadata:
        """Create enhanced project metadata with safety information."""
        template_name = template_path.name
        template_info = self._validate_template_enhanced(template_path)
        
        metadata_dict = {
            'project_name': project_name,
            'project_path': str(project_path),
            'template_name': template_name,
            'creation_date': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'battery_simulator_version': '1.0.0',
            'parameters': parameters,
            'checksums': {},  # Will be calculated later
            'dependencies': template_info.get('dependencies', []),
            'status': 'active',
            'template_version': template_info.get('compatibility', {}).get('openfoam_version', '1.0.0'),
            'operation_history': [{
                'operation_id': operation_id,
                'operation_type': 'create',
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'details': {
                    'template_type': template_info.get('template_type', 'unknown'),
                    'file_count': template_info.get('file_count', 0),
                    'template_size': template_info.get('size', 0)
                }
            }],
            'backup_count': 0,
            'file_permissions': self._get_directory_permissions(project_path)
        }
        
        return ProjectMetadata(metadata_dict)
    
    def _get_directory_permissions(self, directory_path: Path) -> Dict[str, str]:
        """Get file permissions for directory and key files."""
        permissions = {}
        try:
            # Get directory permissions
            stat_info = directory_path.stat()
            permissions['directory'] = oct(stat_info.st_mode)[-3:]
            
            # Get permissions for key files
            key_files = ['system/controlDict', 'system/fvSchemes', 'system/fvSolution']
            for file_path in key_files:
                full_path = directory_path / file_path
                if full_path.exists():
                    file_stat = full_path.stat()
                    permissions[file_path] = oct(file_stat.st_mode)[-3:]
                    
        except Exception as e:
            logger.warning(f"Failed to get permissions: {e}")
            permissions['error'] = str(e)
            
        return permissions
    
    def _set_project_permissions(self, project_path: Path):
        """Set appropriate permissions for project directory."""
        try:
            # Set directory permissions (read, write, execute for owner and group)
            os.chmod(project_path, 0o755)
            
            # Set permissions for all files and subdirectories
            for item in project_path.rglob('*'):
                if item.is_file():
                    os.chmod(item, 0o644)
                elif item.is_dir():
                    os.chmod(item, 0o755)
                    
        except Exception as e:
            logger.warning(f"Failed to set permissions: {e}")
    
    def _calculate_enhanced_integrity(self, project_path: Path):
        """Calculate enhanced file integrity with multiple hash algorithms."""
        checksums = {}
        try:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            
                        # Calculate multiple hash algorithms
                        md5_hash = hashlib.md5(content).hexdigest()
                        sha256_hash = hashlib.sha256(content).hexdigest()
                        
                        relative_path = str(file_path.relative_to(project_path))
                        checksums[relative_path] = {
                            'md5': md5_hash,
                            'sha256': sha256_hash,
                            'size': len(content),
                            'modified': file_path.stat().st_mtime
                        }
                        
                    except Exception as e:
                        logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
                        checksums[str(file_path.relative_to(project_path))] = {'error': str(e)}
                        
            integrity_path = project_path / self.INTEGRITY_FILE
            with open(integrity_path, 'w') as f:
                json.dump(checksums, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to calculate enhanced integrity: {e}")
            raise ProjectIntegrityError(f"Integrity calculation failed: {e}")
    
    def _create_initial_backup(self, project_path: Path, project_name: str):
        """Create initial backup of the project."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{project_name}_initial_backup_{timestamp}.zip"
            backup_path = self.base_projects_path / backup_filename
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_path)
                        zipf.write(file_path, arcname)
                        
            # Update metadata with backup information
            metadata = self.get_project_metadata(project_path)
            if metadata:
                metadata.backup_count += 1
                metadata.operation_history.append({
                    'operation_id': f"backup_{timestamp}",
                    'operation_type': 'backup',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'details': {'backup_path': str(backup_path)}
                })
                self._save_project_metadata(project_path, metadata)
                
            logger.info(f"Initial backup created: {backup_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create initial backup: {e}")
    
    def get_project_health_report_enhanced(self, project_name: str) -> Dict[str, Any]:
        """Get enhanced health report with detailed analysis."""
        project_path = self.base_projects_path / project_name
        if not project_path.exists():
            return {'status': 'error', 'message': 'Project not found'}
            
        report = {
            'project_name': project_name,
            'status': 'healthy',
            'issues': [],
            'warnings': [],
            'statistics': {},
            'integrity_check': False,
            'performance_metrics': {},
            'security_analysis': {},
            'recommendations': []
        }
        
        try:
            # Get metadata
            metadata = self.get_project_metadata(project_path)
            if not metadata:
                report['issues'].append('Missing project metadata')
                report['status'] = 'corrupted'
            else:
                # Get statistics
                report['statistics'] = self.get_project_statistics(project_path)
                
                # Performance metrics
                report['performance_metrics'] = self._calculate_performance_metrics(project_path, metadata)
                
                # Security analysis
                report['security_analysis'] = self._analyze_security(project_path, metadata)
                
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
                        
                # Generate recommendations
                report['recommendations'] = self._generate_recommendations(report, metadata)
                
        except Exception as e:
            logger.error(f"Enhanced health report failed: {e}")
            report['status'] = 'error'
            report['message'] = str(e)
            
        return report
    
    def _calculate_performance_metrics(self, project_path: Path, metadata: ProjectMetadata) -> Dict[str, Any]:
        """Calculate performance metrics for the project."""
        metrics = {
            'creation_time': metadata.creation_date,
            'last_modified': metadata.last_modified,
            'file_count': 0,
            'total_size': 0,
            'largest_file': None,
            'operation_count': len(metadata.operation_history),
            'backup_count': metadata.backup_count
        }
        
        # Calculate current statistics
        stats = self.get_project_statistics(project_path)
        metrics.update(stats)
        
        return metrics
    
    def _analyze_security(self, project_path: Path, metadata: ProjectMetadata) -> Dict[str, Any]:
        """Analyze security aspects of the project."""
        security = {
            'permissions_ok': True,
            'sensitive_files': [],
            'backup_security': 'unknown',
            'integrity_verified': False
        }
        
        # Check file permissions
        try:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Check for overly permissive files
                    file_stat = file_path.stat()
                    permissions = oct(file_stat.st_mode)[-3:]
                    if permissions.endswith('77'):  # World writable
                        security['permissions_ok'] = False
                        security['sensitive_files'].append(str(file_path))
                        
        except Exception as e:
            logger.warning(f"Security analysis failed: {e}")
            security['permissions_ok'] = False
            
        # Check backup security
        if metadata.backup_count > 0:
            security['backup_security'] = 'protected'
        else:
            security['backup_security'] = 'none'
            
        return security
    
    def _generate_recommendations(self, report: Dict[str, Any], metadata: ProjectMetadata) -> List[str]:
        """Generate recommendations based on health report."""
        recommendations = []
        
        # Based on issues
        if report['issues']:
            recommendations.append("Address critical issues before proceeding with simulations")
            
        # Based on warnings
        if report['warnings']:
            recommendations.append("Review and fix warnings to improve project stability")
            
        # Based on file count
        if report['statistics'].get('file_count', 0) > 1000:
            recommendations.append("Consider organizing files into subdirectories for better management")
            
        # Based on backup count
        if metadata.backup_count == 0:
            recommendations.append("Create regular backups to protect your work")
        elif metadata.backup_count > 10:
            recommendations.append("Consider cleaning up old backups to save disk space")
            
        # Based on last modified
        import datetime
        last_modified = metadata.last_modified
        if last_modified:
            last_modified_time = datetime.datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
            days_since_modified = (datetime.datetime.now(datetime.timezone.utc) - last_modified_time).days
            if days_since_modified > 30:
                recommendations.append("Project hasn't been modified recently - consider reviewing or archiving")
                
        return recommendations


# Backward compatibility alias
ProjectManager = EnhancedProjectManager
