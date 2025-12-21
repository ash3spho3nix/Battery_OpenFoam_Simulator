#!/usr/bin/env python3
"""
Unit tests for utility components.

This module tests the utility components including file operations,
parameter parser, and error recovery.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import test fixtures
from conftest import TestError


class TestFileOperations:
    """Test the file operations utilities."""
    
    def test_template_manager_creation(self, temp_test_dir: Path):
        """Test TemplateManager can be created."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        assert template_manager is not None
        assert template_manager.template_dir == temp_test_dir
    
    def test_template_creation(self, temp_test_dir: Path):
        """Test template creation."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Create a simple template
        template_content = {
            "test_file.txt": "Hello {{name}}!",
            "test_dir/nested_file.txt": "Nested content"
        }
        
        # Create template files
        for file_path, content in template_content.items():
            full_path = temp_test_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Test template creation
        result = template_manager.create_template("test_template", temp_test_dir)
        assert result is True
    
    def test_project_creation_from_template(self, temp_test_dir: Path):
        """Test project creation from template."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Create a template
        template_dir = temp_test_dir / "templates" / "test_template"
        template_dir.mkdir(parents=True)
        
        # Create template files
        template_file = template_dir / "test_file.txt"
        template_file.write_text("Hello {{name}}!")
        
        # Create project from template
        project_dir = temp_test_dir / "projects" / "test_project"
        
        template_vars = {"name": "World"}
        result = template_manager.create_project_from_template("test_template", project_dir, template_vars)
        
        assert result is True
        assert project_dir.exists()
        
        # Check template variables were replaced
        created_file = project_dir / "test_file.txt"
        assert created_file.exists()
        content = created_file.read_text()
        assert content == "Hello World!"
    
    def test_file_backup_manager(self, temp_test_dir: Path):
        """Test FileBackupManager functionality."""
        from src.utils.file_operations import FileBackupManager
        
        backup_manager = FileBackupManager(temp_test_dir)
        
        # Create test files
        test_file = temp_test_dir / "test.txt"
        test_file.write_text("Original content")
        
        # Create backup
        backup_path = backup_manager.create_backup(test_file)
        assert backup_path.exists()
        
        # Modify original file
        test_file.write_text("Modified content")
        
        # Restore from backup
        backup_manager.restore_backup(backup_path, test_file)
        content = test_file.read_text()
        assert content == "Original content"
    
    def test_file_validation(self, temp_test_dir: Path):
        """Test file validation."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Create test file
        test_file = temp_test_dir / "test.txt"
        test_file.write_text("Test content")
        
        # Test file exists
        assert template_manager.validate_file_exists(test_file) is True
        
        # Test file checksum
        checksum = template_manager.calculate_file_checksum(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) > 0
        
        # Test file integrity
        assert template_manager.validate_file_integrity(test_file, checksum) is True
        
        # Test with modified file
        test_file.write_text("Modified content")
        assert template_manager.validate_file_integrity(test_file, checksum) is False


class TestParameterParser:
    """Test the parameter parser utilities."""
    
    def test_parameter_manager_creation(self, temp_test_dir: Path):
        """Test ParameterManager can be created."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        assert parameter_manager is not None
        assert parameter_manager.case_path == temp_test_dir
    
    def test_load_parameters(self, temp_test_dir: Path):
        """Test parameter loading."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Create test parameter file
        param_file = temp_test_dir / "test_params.txt"
        param_file.write_text("""
        // Test parameter file
        testParameter 100;
        anotherParameter 200;
        stringParameter "test";
        """)
        
        # Load parameters
        params = parameter_manager.load_parameters(param_file)
        assert isinstance(params, dict)
    
    def test_save_parameters(self, temp_test_dir: Path):
        """Test parameter saving."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Test parameters
        test_params = {
            "testParameter": 100,
            "anotherParameter": 200,
            "stringParameter": "test"
        }
        
        # Save parameters
        param_file = temp_test_dir / "saved_params.txt"
        result = parameter_manager.save_parameters(test_params, param_file)
        
        assert result is True
        assert param_file.exists()
    
    def test_validate_parameters(self, temp_test_dir: Path):
        """Test parameter validation."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Test valid parameters
        valid_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0,
            "radius": 10.0
        }
        
        result = parameter_manager.validate_parameters(valid_params)
        assert result is True
        
        # Test invalid parameters
        invalid_params = {
            "length": -10.0,  # Negative value
            "width": 0.0,     # Zero value
            "height": "invalid"  # Invalid type
        }
        
        result = parameter_manager.validate_parameters(invalid_params)
        assert result is False
    
    def test_parameter_interpolation(self, temp_test_dir: Path):
        """Test parameter interpolation."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Test interpolation
        template = "Value is {{testParameter}}"
        params = {"testParameter": 100}
        
        result = parameter_manager.interpolate_parameters(template, params)
        assert result == "Value is 100"
    
    def test_parse_openfoam_dictionary(self, temp_test_dir: Path):
        """Test OpenFOAM dictionary parsing."""
        from src.utils.parameter_parser import ParameterManager
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Create test OpenFOAM dictionary
        dict_content = """
        testDict
        {
            testParameter 100;
            nestedDict
            {
                nestedParameter 200;
            }
            arrayParameter (1 2 3 4);
        }
        """
        
        dict_file = temp_test_dir / "testDict"
        dict_file.write_text(dict_content)
        
        # Parse dictionary
        result = parameter_manager.parse_openfoam_dictionary(dict_file)
        assert isinstance(result, dict)


class TestErrorRecovery:
    """Test the error recovery utilities."""
    
    def test_error_recovery_creation(self, temp_test_dir: Path):
        """Test ErrorRecovery can be created."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        assert error_recovery is not None
        assert error_recovery.recovery_dir == temp_test_dir
    
    def test_error_logging(self, temp_test_dir: Path):
        """Test error logging."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Log error
        error_recovery.log_error("Test error message", "test_component")
        
        # Check log file was created
        log_files = list(temp_test_dir.glob("*.log"))
        assert len(log_files) > 0
    
    def test_state_backup(self, temp_test_dir: Path):
        """Test state backup."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Create test state
        test_state = {
            "project_path": str(temp_test_dir),
            "parameters": {"test": 100},
            "status": "running"
        }
        
        # Backup state
        backup_path = error_recovery.backup_state(test_state)
        assert backup_path.exists()
    
    def test_state_restore(self, temp_test_dir: Path):
        """Test state restoration."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Create test state
        test_state = {
            "project_path": str(temp_test_dir),
            "parameters": {"test": 100},
            "status": "running"
        }
        
        # Backup state
        backup_path = error_recovery.backup_state(test_state)
        
        # Restore state
        restored_state = error_recovery.restore_state(backup_path)
        assert restored_state == test_state
    
    def test_recovery_point_creation(self, temp_test_dir: Path):
        """Test recovery point creation."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Create recovery point
        recovery_point = error_recovery.create_recovery_point("test_operation")
        assert recovery_point is not None
        assert "timestamp" in recovery_point
        assert "operation" in recovery_point
    
    def test_recovery_execution(self, temp_test_dir: Path):
        """Test recovery execution."""
        from src.utils.error_recovery import ErrorRecovery
        
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Create test recovery function
        recovery_executed = False
        
        def test_recovery():
            nonlocal recovery_executed
            recovery_executed = True
            return True
        
        # Execute recovery
        result = error_recovery.execute_recovery(test_recovery)
        
        assert result is True
        assert recovery_executed is True


class TestUtilsIntegration:
    """Test integration between utility components."""
    
    def test_template_and_parameter_integration(self, temp_test_dir: Path):
        """Test integration between template manager and parameter parser."""
        from src.utils.file_operations import TemplateManager
        from src.utils.parameter_parser import ParameterManager
        
        # Create template manager
        template_manager = TemplateManager(temp_test_dir)
        
        # Create parameter manager
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Create template with parameters
        template_dir = temp_test_dir / "templates" / "param_template"
        template_dir.mkdir(parents=True)
        
        template_file = template_dir / "config.txt"
        template_file.write_text("Parameter: {{testParam}}")
        
        # Create parameters
        params = {"testParam": 42}
        
        # Create project with parameters
        project_dir = temp_test_dir / "projects" / "param_project"
        result = template_manager.create_project_from_template("param_template", project_dir, params)
        
        assert result is True
        
        # Verify parameter substitution
        config_file = project_dir / "config.txt"
        assert config_file.exists()
        content = config_file.read_text()
        assert content == "Parameter: 42"
    
    def test_backup_and_recovery_integration(self, temp_test_dir: Path):
        """Test integration between backup manager and error recovery."""
        from src.utils.file_operations import FileBackupManager
        from src.utils.error_recovery import ErrorRecovery
        
        # Create backup manager
        backup_manager = FileBackupManager(temp_test_dir)
        
        # Create error recovery
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Create test file
        test_file = temp_test_dir / "test.txt"
        test_file.write_text("Original content")
        
        # Create backup
        backup_path = backup_manager.create_backup(test_file)
        
        # Create recovery point
        recovery_point = error_recovery.create_recovery_point("backup_operation")
        
        # Modify file
        test_file.write_text("Modified content")
        
        # Restore from backup
        backup_manager.restore_backup(backup_path, test_file)
        
        # Verify restoration
        content = test_file.read_text()
        assert content == "Original content"
    
    def test_error_handling_integration(self, temp_test_dir: Path):
        """Test error handling integration."""
        from src.utils.file_operations import TemplateManager
        from src.utils.error_recovery import ErrorRecovery
        
        # Create components
        template_manager = TemplateManager(temp_test_dir)
        error_recovery = ErrorRecovery(temp_test_dir)
        
        # Test error scenario
        try:
            # This should fail gracefully
            result = template_manager.create_project_from_template("nonexistent", temp_test_dir, {})
            assert result is False
        except Exception as e:
            # Log error
            error_recovery.log_error(str(e), "template_manager")
            
            # Verify error was logged
            log_files = list(temp_test_dir.glob("*.log"))
            assert len(log_files) > 0


class TestUtilsPerformance:
    """Test performance aspects of utility components."""
    
    def test_template_performance(self, temp_test_dir: Path):
        """Test template performance."""
        from src.utils.file_operations import TemplateManager
        import time
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Create large template
        template_dir = temp_test_dir / "templates" / "large_template"
        template_dir.mkdir(parents=True)
        
        # Create multiple files
        for i in range(10):
            file_path = template_dir / f"file_{i}.txt"
            file_path.write_text(f"Content for file {i}" * 100)
        
        # Measure creation time
        project_dir = temp_test_dir / "projects" / "large_project"
        
        start_time = time.time()
        result = template_manager.create_project_from_template("large_template", project_dir, {})
        end_time = time.time()
        
        duration = end_time - start_time
        assert result is True
        assert duration < 5.0  # Should complete in reasonable time
    
    def test_parameter_parsing_performance(self, temp_test_dir: Path):
        """Test parameter parsing performance."""
        from src.utils.parameter_parser import ParameterManager
        import time
        
        parameter_manager = ParameterManager(temp_test_dir)
        
        # Create large parameter file
        param_file = temp_test_dir / "large_params.txt"
        param_content = ""
        for i in range(1000):
            param_content += f"param_{i} {i};\n"
        param_file.write_text(param_content)
        
        # Measure parsing time
        start_time = time.time()
        params = parameter_manager.load_parameters(param_file)
        end_time = time.time()
        
        duration = end_time - start_time
        assert isinstance(params, dict)
        assert duration < 2.0  # Should parse quickly
    
    def test_backup_performance(self, temp_test_dir: Path):
        """Test backup performance."""
        from src.utils.file_operations import FileBackupManager
        import time
        
        backup_manager = FileBackupManager(temp_test_dir)
        
        # Create large file
        large_file = temp_test_dir / "large_file.txt"
        large_content = "Large content" * 10000
        large_file.write_text(large_content)
        
        # Measure backup time
        start_time = time.time()
        backup_path = backup_manager.create_backup(large_file)
        end_time = time.time()
        
        duration = end_time - start_time
        assert backup_path.exists()
        assert duration < 10.0  # Should backup quickly


class TestUtilsCrossPlatform:
    """Test cross-platform compatibility of utility components."""
    
    def test_path_handling(self, temp_test_dir: Path):
        """Test path handling across platforms."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Test different path formats
        test_paths = [
            temp_test_dir / "test1",
            temp_test_dir / "test2" / "nested",
            temp_test_dir / "test3" / "deeply" / "nested" / "path"
        ]
        
        for path in test_paths:
            # Test path creation
            path.mkdir(parents=True, exist_ok=True)
            assert path.exists()
            
            # Test path validation
            assert template_manager.validate_file_exists(path) is True
    
    def test_file_encoding(self, temp_test_dir: Path):
        """Test file encoding compatibility."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Test different encodings
        test_contents = [
            "ASCII content",
            "Unicode content: 你好世界",
            "Special chars: éèêë",
            "Emoji: 🚀⚡💻"
        ]
        
        for i, content in enumerate(test_contents):
            file_path = temp_test_dir / f"test_{i}.txt"
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            
            # Read file
            read_content = file_path.read_text(encoding='utf-8')
            assert read_content == content
    
    def test_file_permissions(self, temp_test_dir: Path):
        """Test file permission handling."""
        from src.utils.file_operations import TemplateManager
        
        template_manager = TemplateManager(temp_test_dir)
        
        # Create test file
        test_file = temp_test_dir / "test_permissions.txt"
        test_file.write_text("Test content")
        
        # Test file exists
        assert template_manager.validate_file_exists(test_file) is True
        
        # Test file operations work with different permissions
        # (This is more relevant on Unix systems)
        if os.name != 'nt':  # Not Windows
            import stat
            # Make file read-only
            os.chmod(test_file, stat.S_IRUSR)
            
            # Should still be readable
            assert template_manager.validate_file_exists(test_file) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])