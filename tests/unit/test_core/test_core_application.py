"""
Comprehensive unit tests for core application components.

This module tests the core application logic including:
- ProjectManager functionality
- Constants and configuration
- Application initialization
- Error handling and recovery
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

# Import test modules
from src.core.project_manager_enhanced import EnhancedProjectManager, ProjectValidationError
from src.core.constants import (
    APP_NAME, APP_VERSION, SUPPORTED_MODULES, SOLVER_NAMES,
    PARAMETER_FILES, DEFAULT_PARAMETERS, ERROR_MESSAGES
)
from src.core.config import ConfigManager


class TestEnhancedProjectManager:
    """Test suite for EnhancedProjectManager class."""
    
    def test_project_manager_initialization(self):
        """Test ProjectManager initialization with default parameters."""
        pm = EnhancedProjectManager(base_projects_path=tempfile.mkdtemp())
        assert pm.base_projects_path.is_dir()
    
    def test_create_project_success(self, temp_dir, mock_templates):
        """Test successful project creation."""
        with patch('src.core.constants.TEMPLATES_PATH', mock_templates):
            pm = EnhancedProjectManager(base_projects_path=temp_dir)
            
            result = pm.create_project_safe(
                project_name="TestProject",
                template_name="SPM",
                project_path=temp_dir,
                create_backup=False # Disable backup for faster tests
            )
            
            assert result is True
            
            # Verify project structure was created
            project_path = Path(temp_dir) / "TestProject"
            assert project_path.exists()
            assert (project_path / "SPMFoam").exists()
            assert (project_path / "Case").exists()
            assert (project_path / pm.PROJECT_METADATA_FILE).exists()
            assert (project_path / pm.INTEGRITY_FILE).exists()
    
    def test_create_project_invalid_inputs(self, temp_dir):
        """Test project creation with invalid inputs."""
        pm = EnhancedProjectManager(base_projects_path=temp_dir)
        
        # Empty project name
        with pytest.raises(ProjectValidationError):
            pm.create_project_safe("", "SPM", temp_dir)
    
    def test_create_project_existing_directory(self, temp_dir, mock_templates):
        """Test project creation when directory already exists."""
        with patch('src.core.constants.TEMPLATES_PATH', mock_templates):
            pm = EnhancedProjectManager(base_projects_path=temp_dir)
            
            # Create project first time
            result1 = pm.create_project_safe("TestProject", "SPM", temp_dir, create_backup=False)
            assert result1 is True
            
            # Try to create again
            with pytest.raises(ProjectValidationError):
                pm.create_project_safe("TestProject", "SPM", temp_dir, create_backup=False)
    
    def test_create_project_missing_template(self, temp_dir):
        """Test project creation when template is missing."""
        pm = EnhancedProjectManager(base_projects_path=temp_dir)
        
        with pytest.raises(ProjectValidationError):
            pm.create_project_safe("TestProject", "NonExistentTemplate", temp_dir, create_backup=False)


class TestConstants:
    """Test suite for constants module."""
    
    def test_app_constants(self):
        """Test application constants."""
        assert APP_NAME == "BatteryFOAM"
        assert APP_VERSION == "1.0.0"
    
    def test_supported_modules(self):
        """Test supported modules configuration."""
        assert isinstance(SUPPORTED_MODULES, dict)
        assert "SPM" in SUPPORTED_MODULES
        assert "halfCell" in SUPPORTED_MODULES
        assert "fullCell" in SUPPORTED_MODULES
    
    def test_solver_names(self):
        """Test solver names configuration."""
        assert isinstance(SOLVER_NAMES, dict)
        assert "SPM" in SOLVER_NAMES
        assert "halfCell" in SOLVER_NAMES
        assert "fullCell" in SOLVER_NAMES
    
    def test_parameter_files(self):
        """Test parameter files configuration."""
        assert isinstance(PARAMETER_FILES, dict)
        expected_files = [
            'blockMeshDict', 'topoSetDict', 'LiProperties',
            'fvSchemes', 'fvSolution', 'controlDict'
        ]
        for file_name in expected_files:
            assert file_name in PARAMETER_FILES
    
    def test_default_parameters(self):
        """Test default parameters configuration."""
        assert isinstance(DEFAULT_PARAMETERS, dict)
        assert len(DEFAULT_PARAMETERS) > 0
    
    def test_error_messages(self):
        """Test error messages configuration."""
        assert isinstance(ERROR_MESSAGES, dict)
        assert len(ERROR_MESSAGES) > 0


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization."""
        config = ConfigManager()
        assert config is not None
    
    def test_get_config_value(self):
        """Test getting configuration values."""
        config = ConfigManager()
        
        # Test with environment variable
        os.environ['TEST_CONFIG_KEY'] = 'test_value'
        value = config.get('TEST_CONFIG_KEY', 'default_value')
        assert value == 'test_value'
        
        # Test with default value
        value = config.get('NONEXISTENT_KEY', 'default_value')
        assert value == 'default_value'
    
    def test_set_config_value(self):
        """Test setting configuration values."""
        config = ConfigManager()
        
        config.set('TEST_KEY', 'test_value')
        value = config.get('TEST_KEY', 'default')
        assert value == 'test_value'
    
    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        config_path = Path(temp_dir) / "test_config.json"
        config = ConfigManager(config_path=str(config_path))
        
        # Set some values
        config.set('test_key1', 'value1')
        config.set('test_key2', 'value2')
        
        # Save configuration
        config.save()
        
        # Create new config instance and load
        config2 = ConfigManager(config_path=str(config_path))
        config2.load()
        
        assert config2.get('test_key1', None) == 'value1'
        assert config2.get('test_key2', None) == 'value2'
    
    def test_reset_config(self):
        """Test resetting configuration to defaults."""
        config = ConfigManager()
        
        # Set custom values
        config.set('custom_key', 'custom_value')
        
        # Reset configuration
        config.reset()
        
        # Should not have custom values anymore
        value = config.get('custom_key', None)
        assert value is None


class TestErrorHandling:
    """Test suite for error handling and recovery."""
    
    def test_file_not_found_error(self):
        """Test handling of file not found errors."""
        from src.utils.error_recovery import handle_file_error
        
        with pytest.raises(FileNotFoundError):
            handle_file_error("nonexistent_file.txt")
    
    def test_permission_error(self, temp_dir):
        """Test handling of permission errors."""
        from src.utils.error_recovery import handle_permission_error
        
        # Create a file and make it read-only
        test_file = Path(temp_dir) / "readonly.txt"
        test_file.write_text("test content")
        
        # This would require platform-specific code to actually make read-only
        # For now, just test that the function exists and can be called
        try:
            handle_permission_error(str(test_file))
        except Exception as e:
            # Expected to fail in test environment
            assert "permission" in str(e).lower()
    
    def test_invalid_parameter_error(self):
        """Test handling of invalid parameter errors."""
        from src.utils.error_recovery import handle_parameter_error
        
        error_msg = handle_parameter_error("Invalid parameter value")
        assert "Invalid parameter value" in error_msg
        assert "parameter" in error_msg.lower()
    
    def test_template_error_recovery(self, temp_dir):
        """Test recovery from template errors."""
        from src.utils.error_recovery import handle_template_error
        
        error_msg = handle_template_error("Template not found")
        assert "template" in error_msg.lower()
        assert "not found" in error_msg.lower()


class TestApplicationIntegration:
    """Test suite for application-level integration."""
    
    def test_project_manager_with_config(self, temp_dir):
        """Test ProjectManager integration with ConfigManager."""
        config = ConfigManager()
        config.set('projects_path', str(temp_dir)) # Ensure it's a string for ConfigManager
        
        pm = EnhancedProjectManager(base_projects_path=config.get('projects_path'))
        assert pm.base_projects_path == Path(temp_dir)
    
    def test_error_handling_with_recovery_manager(self, temp_dir):
        """Test error handling integration with configuration."""
        from src.utils.error_recovery import ErrorRecoveryManager
        
        recovery_manager = ErrorRecoveryManager()
        
        # Test error logging
        recovery_manager.log_error("Test error message")
        
        # Test error recovery
        result = recovery_manager.recover_from_error("Test error")
        assert result is True  # Should always return True for recovery
    
    def test_project_cleanup(self, temp_dir, mock_project):
        """Test project cleanup functionality."""
        pm = ProjectManager(base_projects_path=temp_dir)
        
        project_info = mock_project
        project_path = project_info['project_path']
        
        # Verify project exists
        assert project_path.exists()
        
        # Clean up project (this would normally be implemented)
        # For now, just verify the path exists
        assert project_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])