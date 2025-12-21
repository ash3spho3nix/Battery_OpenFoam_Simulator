"""
Template Integration Example - Complete Implementation.

This module demonstrates how all the enhanced template components work together
in a real-world scenario with comprehensive error handling and progress tracking.
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import enhanced components
from src.utils.file_operations_enhanced import (
    EnhancedTemplateManager, 
    TemplateProgressTracker,
    FileOperationError
)
from src.core.project_manager_enhanced import EnhancedProjectManager
from src.utils.error_recovery import (
    ErrorRecoveryManager, 
    ErrorSeverity, 
    RecoveryStrategy,
    get_error_recovery_manager
)


class TemplateIntegrationExample:
    """
    Complete example of enhanced template system integration.
    
    Demonstrates how to use all enhanced components together for robust
    template operations with comprehensive error handling and recovery.
    """
    
    def __init__(self, base_projects_path: str, templates_path: Optional[str] = None):
        """
        Initialize the integration example.
        
        Args:
            base_projects_path: Base path for projects
            templates_path: Path to templates (optional, uses default if not provided)
        """
        self.base_projects_path = Path(base_projects_path)
        self.templates_path = Path(templates_path) if templates_path else None
        
        # Initialize progress tracker with custom callbacks
        self.progress_tracker = TemplateProgressTracker()
        self._setup_progress_callbacks()
        
        # Initialize enhanced components
        self.template_manager = EnhancedTemplateManager(
            str(self.templates_path) if self.templates_path else str(self._get_default_templates_path()),
            self.progress_tracker
        )
        self.project_manager = EnhancedProjectManager(
            self.base_projects_path,
            self.templates_path,
            self.progress_tracker
        )
        self.error_recovery = get_error_recovery_manager()
        
        # Setup logging
        self._setup_logging()
        
    def _setup_progress_callbacks(self):
        """Setup progress tracking callbacks."""
        self.progress_tracker.progress_updated.connect(self._on_progress_updated)
        self.progress_tracker.operation_started.connect(self._on_operation_started)
        self.progress_tracker.operation_completed.connect(self._on_operation_completed)
        self.progress_tracker.operation_failed.connect(self._on_operation_failed)
        
    def _setup_logging(self):
        """Setup comprehensive logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('template_integration.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _get_default_templates_path(self) -> Path:
        """Get default templates path."""
        return Path(__file__).parent.parent / "resources" / "templates"
        
    def _on_progress_updated(self, current: int, total: int):
        """Handle progress updates."""
        percentage = (current / total) * 100 if total > 0 else 0
        self.logger.info(f"Progress: {current}/{total} ({percentage:.1f}%)")
        
    def _on_operation_started(self, operation_name: str):
        """Handle operation start."""
        self.logger.info(f"Started operation: {operation_name}")
        
    def _on_operation_completed(self, success: bool):
        """Handle operation completion."""
        status = "completed successfully" if success else "failed"
        self.logger.info(f"Operation {status}")
        
    def _on_operation_failed(self, error_message: str):
        """Handle operation failure."""
        self.logger.error(f"Operation failed: {error_message}")
        
    def create_project_with_enhanced_safety(
        self,
        project_name: str,
        template_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a project using all enhanced safety features.
        
        This method demonstrates the complete integration of:
        - Atomic file operations
        - File locking
        - Progress tracking
        - Advanced validation
        - Error recovery
        - Comprehensive logging
        
        Args:
            project_name: Name of the project to create
            template_name: Name of the template to use
            parameters: Optional parameters for substitution
            
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        self.logger.info(f"Starting enhanced project creation: {project_name}")
        
        try:
            # Step 1: Validate inputs with enhanced validation
            self.logger.info("Step 1: Validating inputs...")
            if not self._validate_project_creation_inputs(project_name, template_name):
                return False
                
            # Step 2: Check template availability and validate
            self.logger.info("Step 2: Validating template...")
            template_info = self._validate_template_with_details(template_name)
            if not template_info['validation']['valid']:
                self.logger.error(f"Template validation failed: {template_info['validation']['issues']}")
                return False
                
            # Step 3: Check disk space and system resources
            self.logger.info("Step 3: Checking system resources...")
            if not self._check_system_resources(template_info):
                self.logger.error("Insufficient system resources")
                return False
                
            # Step 4: Create project with enhanced safety features
            self.logger.info("Step 4: Creating project with enhanced safety features...")
            success = self.project_manager.create_project_safe(
                project_path=self.base_projects_path,
                project_name=project_name,
                template_name=template_name,
                parameters=parameters or {},
                validate_template=True,
                create_backup=True
            )
            
            if not success:
                self.logger.error("Project creation failed")
                return False
                
            # Step 5: Verify project integrity
            self.logger.info("Step 5: Verifying project integrity...")
            if not self._verify_project_integrity(project_name):
                self.logger.error("Project integrity check failed")
                return False
                
            # Step 6: Generate health report
            self.logger.info("Step 6: Generating health report...")
            health_report = self.project_manager.get_project_health_report_enhanced(project_name)
            self._log_health_report(health_report)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Project creation completed successfully in {elapsed_time:.2f}s")
            return True
            
        except Exception as e:
            # Handle errors with advanced error recovery
            self.logger.error(f"Enhanced project creation failed: {e}", exc_info=True)
            
            # Use error recovery manager
            recovered = self.error_recovery.handle_error(
                e, 
                operation=f"Create project {project_name}",
                file_path=str(self.base_projects_path / project_name)
            )
            
            if recovered:
                self.logger.info("Error recovered successfully, retrying...")
                # Retry once after recovery
                return self.create_project_with_enhanced_safety(project_name, template_name, parameters)
            else:
                self.logger.error("Error recovery failed")
                return False
    
    def _validate_project_creation_inputs(self, project_name: str, template_name: str) -> bool:
        """Validate project creation inputs with enhanced checks."""
        try:
            # Check project name format
            if not project_name or len(project_name.strip()) < 3:
                self.logger.error("Project name must be at least 3 characters long")
                return False
                
            # Check for invalid characters
            invalid_chars = set('<>:"/\\|?*')
            if any(char in project_name for char in invalid_chars):
                self.logger.error("Project name contains invalid characters")
                return False
                
            # Check if project already exists
            project_path = self.base_projects_path / project_name
            if project_path.exists():
                self.logger.error(f"Project already exists: {project_path}")
                return False
                
            # Check template availability
            available_templates = self.template_manager.list_template_directories()
            if template_name not in available_templates:
                self.logger.error(f"Template not found: {template_name}")
                self.logger.info(f"Available templates: {available_templates}")
                return False
                
            # Check disk space (minimum 100MB required)
            import shutil
            total, used, free = shutil.disk_usage(self.base_projects_path)
            free_mb = free // (1024 * 1024)
            if free_mb < 100:
                self.logger.error(f"Insufficient disk space: {free_mb}MB available, 100MB required")
                return False
                
            self.logger.info("Input validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {e}")
            return False
    
    def _validate_template_with_details(self, template_name: str) -> Dict[str, Any]:
        """Get detailed template validation information."""
        template_path = self.template_manager.templates_path / template_name
        return self.template_manager.get_template_info(template_name)
    
    def _check_system_resources(self, template_info: Dict[str, Any]) -> bool:
        """Check if system has sufficient resources for template creation."""
        try:
            import shutil
            
            # Check disk space based on template size
            template_size = template_info.get('size', 0)
            required_space = template_size * 3  # Template + project + backup
            required_space_mb = required_space // (1024 * 1024)
            
            total, used, free = shutil.disk_usage(self.base_projects_path)
            free_mb = free // (1024 * 1024)
            
            if free_mb < required_space_mb:
                self.logger.error(f"Insufficient disk space: {free_mb}MB available, {required_space_mb}MB required")
                return False
                
            # Check memory (minimum 512MB free RAM recommended)
            import psutil
            memory = psutil.virtual_memory()
            free_gb = memory.available / (1024**3)
            if free_gb < 0.5:
                self.logger.warning(f"Low memory: {free_gb:.2f}GB available, 0.5GB recommended")
                # Continue but log warning
                
            self.logger.info(f"System resources sufficient: {free_mb}MB disk, {free_gb:.2f}GB RAM")
            return True
            
        except Exception as e:
            self.logger.error(f"System resource check failed: {e}")
            return False
    
    def _verify_project_integrity(self, project_name: str) -> bool:
        """Verify project integrity after creation."""
        try:
            project_path = self.base_projects_path / project_name
            
            # Check if project directory exists
            if not project_path.exists():
                self.logger.error("Project directory was not created")
                return False
                
            # Check for critical files
            critical_files = [
                'system/controlDict',
                'system/fvSchemes',
                'system/fvSolution',
                'constant/transportProperties'
            ]
            
            missing_files = []
            for critical_file in critical_files:
                file_path = project_path / critical_file
                if not file_path.exists():
                    missing_files.append(critical_file)
                    
            if missing_files:
                self.logger.error(f"Missing critical files: {missing_files}")
                return False
                
            # Check metadata file
            metadata_path = project_path / "project_metadata.json"
            if not metadata_path.exists():
                self.logger.error("Project metadata file not found")
                return False
                
            # Check integrity file
            integrity_path = project_path / "file_integrity.json"
            if not integrity_path.exists():
                self.logger.error("File integrity file not found")
                return False
                
            self.logger.info("Project integrity verification passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Project integrity verification failed: {e}")
            return False
    
    def _log_health_report(self, health_report: Dict[str, Any]):
        """Log detailed health report."""
        self.logger.info("=== Project Health Report ===")
        self.logger.info(f"Project Status: {health_report.get('status', 'unknown')}")
        self.logger.info(f"File Count: {health_report.get('statistics', {}).get('file_count', 0)}")
        self.logger.info(f"Total Size: {health_report.get('statistics', {}).get('total_size_mb', 0):.2f}MB")
        self.logger.info(f"Integrity Check: {'Passed' if health_report.get('integrity_check', False) else 'Failed'}")
        
        issues = health_report.get('issues', [])
        warnings = health_report.get('warnings', [])
        recommendations = health_report.get('recommendations', [])
        
        if issues:
            self.logger.warning(f"Issues found: {issues}")
        if warnings:
            self.logger.warning(f"Warnings: {warnings}")
        if recommendations:
            self.logger.info(f"Recommendations: {recommendations}")
            
        self.logger.info("===========================")
    
    def demonstrate_error_recovery(self):
        """Demonstrate error recovery capabilities."""
        self.logger.info("=== Demonstrating Error Recovery ===")
        
        # Simulate different types of errors and show recovery
        test_scenarios = [
            ("PermissionError", "Simulated permission error"),
            ("FileOperationError", "Simulated file operation error"),
            ("ConnectionError", "Simulated connection error"),
            ("DiskFullError", "Simulated disk full error")
        ]
        
        for error_type, error_message in test_scenarios:
            self.logger.info(f"Testing recovery for {error_type}...")
            
            # Create a mock exception
            error = Exception(error_message)
            error.__class__.__name__ = error_type  # Simulate different error types
            
            # Test recovery
            context = {
                'error_type': error_type,
                'error_message': error_message,
                'operation': 'test_operation',
                'file_path': '/test/path',
                'timestamp': '2025-01-01T00:00:00',
                'severity': ErrorSeverity.MEDIUM
            }
            
            recovered = self.error_recovery.handle_error(error, context)
            self.logger.info(f"Recovery for {error_type}: {'Success' if recovered else 'Failed'}")
            
        # Show recovery statistics
        stats = self.error_recovery.get_recovery_statistics()
        self.logger.info(f"Recovery Statistics: {stats}")
        
        # Export recovery report
        report_path = self.base_projects_path / "recovery_report.json"
        self.error_recovery.export_recovery_report(report_path)
        self.logger.info(f"Recovery report exported to: {report_path}")
        
        self.logger.info("=============================")
    
    def demonstrate_progress_tracking(self, project_name: str, template_name: str):
        """Demonstrate progress tracking capabilities."""
        self.logger.info("=== Demonstrating Progress Tracking ===")
        
        # Create a project and watch progress
        self.create_project_with_enhanced_safety(project_name, template_name)
        
        self.logger.info("==============================")
    
    def cleanup_test_projects(self, prefix: str = "test_"):
        """Clean up test projects created during demonstration."""
        self.logger.info(f"Cleaning up test projects with prefix: {prefix}")
        
        try:
            removed_count = 0
            for item in self.base_projects_path.iterdir():
                if item.is_dir() and item.name.startswith(prefix):
                    import shutil
                    shutil.rmtree(item)
                    removed_count += 1
                    self.logger.info(f"Removed: {item.name}")
                    
            self.logger.info(f"Cleaned up {removed_count} test projects")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


def main():
    """Main demonstration function."""
    # Setup paths
    base_projects_path = Path("test_projects")
    templates_path = Path("src/resources/templates")
    
    # Create integration example
    integration = TemplateIntegrationExample(str(base_projects_path), str(templates_path))
    
    # Demonstrate error recovery
    integration.demonstrate_error_recovery()
    
    # Get available templates
    templates = integration.template_manager.list_template_directories()
    if not templates:
        print("No templates found. Please ensure templates are available.")
        return
    
    # Create test project
    test_project_name = "test_enhanced_project"
    template_name = templates[0]  # Use first available template
    
    print(f"Creating test project: {test_project_name} using template: {template_name}")
    
    # Demonstrate progress tracking and enhanced safety
    success = integration.create_project_with_enhanced_safety(
        test_project_name, 
        template_name,
        parameters={
            'PROJECT_NAME': test_project_name,
            'CREATION_DATE': '2025-01-01',
            'TEMPLATE_NAME': template_name
        }
    )
    
    if success:
        print("✅ Project created successfully with enhanced safety features!")
    else:
        print("❌ Project creation failed")
    
    # Cleanup
    integration.cleanup_test_projects("test_")
    print("🧹 Cleanup completed")


if __name__ == "__main__":
    main()