"""
Enhanced File Operations for Battery Simulator - ATOMIC OPERATIONS IMPLEMENTED.

This module provides enhanced file operations with atomic operations, file locking,
rollback mechanisms, and progress tracking for template management.
"""

import os
import shutil
import re
import tempfile
import logging

import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from PyQt6.QtCore import QObject, pyqtSignal
import time

logger = logging.getLogger(__name__)


class FileOperationError(Exception):
    """Exception raised when file operations fail."""
    pass


class TemplateProgressTracker(QObject):
    """
    Progress tracker for template operations with PyQt6 signals.
    
    Provides real-time progress updates for long-running template operations.
    """
    progress_updated = pyqtSignal(int, int)  # current, total
    operation_started = pyqtSignal(str)      # operation name
    operation_completed = pyqtSignal(bool)   # success
    operation_failed = pyqtSignal(str)       # error message
    
    def __init__(self):
        """Initialize the progress tracker."""
        super().__init__()
        self.total_operations = 0
        self.current_operation = 0
        self.operation_name = ""
        self._lock = threading.Lock()
        
    def set_total_operations(self, count: int):
        """Set the total number of operations."""
        with self._lock:
            self.total_operations = count
            self.current_operation = 0
            
    def update_progress(self, increment: int = 1):
        """Update progress by increment."""
        with self._lock:
            self.current_operation += increment
            if self.total_operations > 0:
                self.progress_updated.emit(self.current_operation, self.total_operations)
                
    def start_operation(self, operation_name: str):
        """Start a new operation."""
        with self._lock:
            self.operation_name = operation_name
            self.operation_started.emit(operation_name)
            
    def complete_operation(self, success: bool = True):
        """Complete the current operation."""
        with self._lock:
            self.operation_completed.emit(success)
            
    def fail_operation(self, error_message: str):
        """Mark operation as failed."""
        with self._lock:
            self.operation_failed.emit(error_message)


class FileLock:
    """
    Cross-platform file locking mechanism.
    
    Uses fcntl on Unix systems and msvcrt on Windows.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize file lock.
        
        Args:
            file_path: Path to the file to lock
        """
        self.file_path = file_path
        self.lock_file = None
        self.lock_fd = None
        
    def acquire(self, timeout: float = 30.0) -> bool:
        """
        Acquire exclusive lock on file.
        
        Args:
            timeout: Maximum time to wait for lock in seconds
            
        Returns:
            bool: True if lock acquired successfully
        """
        try:
            # Create lock file if it doesn't exist
            self.lock_file = self.file_path.with_suffix('.lock')
            self.lock_file.touch()
            
            # Open lock file for writing
            self.lock_fd = open(self.lock_file, 'w')
            
            # Try to acquire lock with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    if os.name == 'nt':  # Windows
                        import msvcrt
                        msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                    else:  # Unix
                        import fcntl
                        fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    
                    logger.debug(f"Acquired lock for {self.file_path}")
                    return True
                    
                except (IOError, OSError):
                    time.sleep(0.1)  # Wait before retry
                    
            logger.warning(f"Timeout acquiring lock for {self.file_path}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to acquire lock for {self.file_path}: {e}")
            self.release()
            return False
            
    def release(self):
        """Release the file lock."""
        try:
            if self.lock_fd:
                if os.name == 'nt':  # Windows
                    import msvcrt
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:  # Unix
                    fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                self.lock_fd.close()
                self.lock_fd = None
                
            if self.lock_file and self.lock_file.exists():
                self.lock_file.unlink()
                
            logger.debug(f"Released lock for {self.file_path}")
            
        except Exception as e:
            logger.error(f"Failed to release lock for {self.file_path}: {e}")
            
    def __enter__(self):
        """Context manager entry."""
        if self.acquire():
            return self
        else:
            raise FileOperationError(f"Could not acquire lock for {self.file_path}")
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


class AtomicFileOperation:
    """
    Atomic file operations with rollback capabilities.
    
    Ensures file operations are atomic and provides rollback on failure.
    """
    
    def __init__(self, progress_tracker: Optional[TemplateProgressTracker] = None):
        """
        Initialize atomic file operation.
        
        Args:
            progress_tracker: Optional progress tracker
        """
        self.progress_tracker = progress_tracker
        self.operations = []  # Stack of operations for rollback
        self._lock = threading.Lock()
        
    def execute_with_rollback(self, operation_func: Callable, *args, **kwargs):
        """
        Execute operation with automatic rollback on failure.
        
        Args:
            operation_func: Function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the operation function
            
        Raises:
            FileOperationError: If operation fails and rollback is attempted
        """
        operation_id = len(self.operations)
        
        try:
            # Execute operation
            result = operation_func(*args, **kwargs)
            
            # If successful, add to operations stack (for potential rollback later)
            self.operations.append({
                'id': operation_id,
                'type': 'success',
                'func': operation_func,
                'args': args,
                'kwargs': kwargs
            })
            
            if self.progress_tracker:
                self.progress_tracker.update_progress(1)
                
            return result
            
        except Exception as e:
            logger.error(f"Operation failed, attempting rollback: {e}")
            
            # Rollback all previous operations
            self._rollback_operations()
            
            # Clear operations stack
            self.operations.clear()
            
            raise FileOperationError(f"Operation failed and rolled back: {e}")
            
    def _rollback_operations(self):
        """Rollback all operations in reverse order."""
        logger.info(f"Rolling back {len(self.operations)} operations")
        
        # Rollback in reverse order
        for operation in reversed(self.operations):
            try:
                self._rollback_operation(operation)
            except Exception as e:
                logger.error(f"Rollback failed for operation {operation['id']}: {e}")
                
    def _rollback_operation(self, operation: Dict[str, Any]):
        """Rollback a single operation."""
        op_type = operation['type']
        
        if op_type == 'create_file':
            # Remove created file
            file_path = operation['file_path']
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Removed file during rollback: {file_path}")
                
        elif op_type == 'create_directory':
            # Remove created directory (if empty)
            dir_path = operation['dir_path']
            if dir_path.exists():
                try:
                    dir_path.rmdir()  # Only removes empty directories
                    logger.debug(f"Removed directory during rollback: {dir_path}")
                except OSError:
                    logger.warning(f"Directory not empty, cannot remove: {dir_path}")
                    
        elif op_type == 'move_file':
            # Move file back to original location
            original_path = operation['original_path']
            new_path = operation['new_path']
            if new_path.exists():
                shutil.move(str(new_path), str(original_path))
                logger.debug(f"Moved file back during rollback: {new_path} -> {original_path}")
                
        elif op_type == 'copy_file':
            # Remove copied file
            dest_path = operation['dest_path']
            if dest_path.exists():
                dest_path.unlink()
                logger.debug(f"Removed copied file during rollback: {dest_path}")
                
    def clear_operations(self):
        """Clear the operations stack after successful completion."""
        with self._lock:
            self.operations.clear()
            logger.debug("Cleared operations stack")


class EnhancedTemplateManager:
    """
    Enhanced Template Manager with atomic operations, file locking, and rollback.
    
    Provides enterprise-grade template operations with comprehensive error handling
    and recovery mechanisms.
    """
    
    def __init__(self, templates_path: str, progress_tracker: Optional[TemplateProgressTracker] = None):
        """
        Initialize the enhanced template manager.
        
        Args:
            templates_path: Path to the templates directory
            progress_tracker: Optional progress tracker for operations
        """
        self.templates_path = Path(templates_path)
        self.parameters = {}
        self.progress_tracker = progress_tracker or TemplateProgressTracker()
        self.atomic_ops = AtomicFileOperation(self.progress_tracker)
        
        if not self.templates_path.exists():
            logger.warning(f"Templates path does not exist: {self.templates_path}")
            
    def set_parameter(self, key: str, value: Any):
        """Set a parameter for substitution."""
        self.parameters[key] = value
        
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set multiple parameters at once."""
        self.parameters.update(parameters)
        
    def load_template(self, template_name: str) -> Optional[str]:
        """Load a template file with file locking."""
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return None
            
        try:
            # Use file lock when reading template
            with FileLock(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.debug(f"Loaded template: {template_name}")
                return content
                
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None
            
    def substitute_parameters(self, template_content: str) -> str:
        """Substitute parameters in template content."""
        result = template_content
        
        # Replace placeholders with parameter values
        for key, value in self.parameters.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
            
        return result
        
    def generate_file_atomic(self, template_name: str, output_path: str) -> bool:
        """
        Generate a file from a template using atomic operations.
        
        Args:
            template_name: Name of the template file
            output_path: Path where the generated file should be saved
            
        Returns:
            bool: True if successful
        """
        def _generate_to_temp(template_name: str, temp_path: Path) -> bool:
            """Generate file to temporary location."""
            template_content = self.load_template(template_name)
            
            if template_content is None:
                return False
                
            # Substitute parameters
            content = self.substitute_parameters(template_content)
            
            # Write to temporary file
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.debug(f"Generated temporary file: {temp_path}")
            return True
            
        def _move_to_final(temp_path: Path, final_path: Path):
            """Move temporary file to final location."""
            # Ensure output directory exists
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Atomic move
            shutil.move(str(temp_path), str(final_path))
            
            # Record operation for potential rollback
            self.atomic_ops.operations.append({
                'type': 'create_file',
                'file_path': final_path
            })
            
            logger.debug(f"Atomic move completed: {temp_path} -> {final_path}")
            
        try:
            output_path = Path(output_path)
            temp_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
            
            # Execute with rollback
            self.atomic_ops.execute_with_rollback(_generate_to_temp, template_name, temp_path)
            self.atomic_ops.execute_with_rollback(_move_to_final, temp_path, output_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Atomic file generation failed: {e}")
            return False
            
    def copy_template_directory_atomic(self, template_dir: str, output_dir: str) -> bool:
        """
        Copy an entire template directory structure using atomic operations.
        
        Args:
            template_dir: Name of the template directory
            output_dir: Path where the directory should be copied
            
        Returns:
            bool: True if successful
        """
        def _copy_directory_structure(template_path: Path, output_path: Path):
            """Copy directory structure to temporary location."""
            if output_path.exists():
                shutil.rmtree(output_path)
            shutil.copytree(template_path, output_path)
            
            # Record operation for potential rollback
            self.atomic_ops.operations.append({
                'type': 'create_directory',
                'dir_path': output_path
            })
            
            logger.debug(f"Copied directory structure: {template_path} -> {output_path}")
            
        def _process_directory_files(directory_path: Path):
            """Process all files in the directory for parameter substitution."""
            file_count = 0
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
                            
                        file_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_path}: {e}")
                        
            return file_count
            
        try:
            template_path = self.templates_path / template_dir
            output_path = Path(output_dir)
            
            if not template_path.exists():
                logger.error(f"Template directory not found: {template_path}")
                return False
                
            # Calculate total operations for progress tracking
            total_files = sum(len(files) for _, _, files in os.walk(template_path))
            self.progress_tracker.set_total_operations(total_files + 1)  # +1 for directory copy
            
            # Start operation
            self.progress_tracker.start_operation(f"Copying template {template_dir}")
            
            # Copy directory structure
            self.atomic_ops.execute_with_rollback(_copy_directory_structure, template_path, output_path)
            
            # Process files
            file_count = self.atomic_ops.execute_with_rollback(_process_directory_files, output_path)
            
            # Complete operation
            self.progress_tracker.complete_operation(True)
            self.atomic_ops.clear_operations()  # Clear operations since everything succeeded
            
            logger.debug(f"Copied template directory: {template_dir} -> {output_dir} ({file_count} files processed)")
            return True
            
        except Exception as e:
            logger.error(f"Atomic directory copy failed: {e}")
            self.progress_tracker.fail_operation(str(e))
            return False
            
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped during processing."""
        # Skip binary files and certain extensions
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.exe', '.bin'}
        skip_files = {'Make', 'Allwmake', 'Allclean'}
        
        if file_path.suffix.lower() in skip_extensions:
            return True
            
        if file_path.name in skip_files:
            return True
            
        return False
        
    def validate_template_completeness(self, template_path: Path) -> Dict[str, Any]:
        """
        Validate template completeness and structure.
        
        Args:
            template_path: Path to the template directory
            
        Returns:
            Dict containing validation results
        """
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'critical_files': [],
            'openfoam_structure': False,
            'template_type': 'unknown'
        }
        
        try:
            # Check critical OpenFOAM directories
            critical_dirs = ['system', 'constant']
            for critical_dir in critical_dirs:
                if (template_path / critical_dir).exists():
                    validation_result['critical_files'].append(critical_dir)
                else:
                    validation_result['warnings'].append(f"Missing critical directory: {critical_dir}")
            
            # Check for OpenFOAM files
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
                
            # Check for required files based on template type
            if validation_result['template_type'] != 'unknown':
                validation_result['valid'] = True
            else:
                validation_result['issues'].append("Unknown template type")
                validation_result['valid'] = False
                
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            validation_result['issues'].append(f"Validation error: {str(e)}")
            validation_result['valid'] = False
            
        return validation_result
        
    def list_templates(self) -> List[str]:
        """List all available templates."""
        templates = []
        
        if self.templates_path.exists():
            for item in self.templates_path.iterdir():
                if item.is_file():
                    templates.append(item.name)
                    
        return sorted(templates)
        
    def list_template_directories(self) -> List[str]:
        """List all available template directories."""
        directories = []
        
        if self.templates_path.exists():
            for item in self.templates_path.iterdir():
                if item.is_dir():
                    directories.append(item.name)
                    
        return sorted(directories)
        
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dict containing template information
        """
        template_path = self.templates_path / template_name
        
        info = {
            'name': template_name,
            'path': str(template_path),
            'exists': template_path.exists(),
            'type': 'unknown',
            'size': 0,
            'file_count': 0,
            'validation': {}
        }
        
        if template_path.exists():
            # Calculate size and file count
            total_size = 0
            file_count = 0
            for item in template_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
                    
            info['size'] = total_size
            info['file_count'] = file_count
            
            # Validate template
            info['validation'] = self.validate_template_completeness(template_path)
            info['type'] = info['validation'].get('template_type', 'unknown')
            
        return info