"""
Comprehensive unit tests for utility components.

This module tests the utility functions and components including:
- ParameterManager and ParameterParser
- TemplateManager and FileOperations
- Error handling and recovery utilities
- Validator factory and specific validators
- File operations and backup management
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import json

# Import test modules
from src.utils.parameter_parser import ParameterManager, ParameterParser
from src.utils.file_operations import TemplateManager, FileBackupManager
from src.utils.error_recovery import (
    ErrorRecoveryManager, handle_file_error, handle_permission_error,
    handle_parameter_error, handle_template_error
)
from src.utils.validator_factory import ValidatorFactory
from src.utils.validators.carbon_validator import CarbonValidator
from src.utils.validators.halfcell_validator import HalfCellValidator
from src.utils.validators.fullcell_validator import FullCellValidator
from src.utils.exception_handler import ExceptionHandler


class TestParameterManager:
    """Test suite for ParameterManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.param_dir = Path(self.test_dir) / "parameters"
        self.param_dir.mkdir()
        self.manager = ParameterManager(str(self.param_dir))
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test ParameterManager initialization."""
        assert self.manager.parameter_dir == str(self.param_dir)
        assert self.manager.parameters == {}
        
    def test_load_parameters(self):
        """Test loading parameters from files."""
        # Create test parameter files
        param_files = {
            'blockMeshDict': 'test content 1',
            'topoSetDict': 'test content 2',
            'LiProperties': 'test content 3'
        }
        
        for filename, content in param_files.items():
            param_file = self.param_dir / filename
            param_file.write_text(content)
        
        # Load parameters
        result = self.manager.load_parameters()
        assert result is True
        
        # Verify parameters were loaded
        assert len(self.manager.parameters) == len(param_files)
        for filename in param_files.keys():
            assert filename in self.manager.parameters
            
    def test_save_parameters(self):
        """Test saving parameters to files."""
        # Set some parameters
        test_params = {
            'blockMeshDict': 'new content 1',
            'topoSetDict': 'new content 2'
        }
        self.manager.parameters = test_params
        
        # Save parameters
        result = self.manager.save_parameters()
        assert result is True
        
        # Verify files were created
        for filename in test_params.keys():
            param_file = self.param_dir / filename
            assert param_file.exists()
            assert param_file.read_text() == test_params[filename]
            
    def test_get_parameter(self):
        """Test getting a specific parameter."""
        # Load some parameters
        self.manager.parameters = {
            'blockMeshDict': 'test content',
            'topoSetDict': 'another content'
        }
        
        # Get parameter
        content = self.manager.get_parameter('blockMeshDict')
        assert content == 'test content'
        
        # Get non-existent parameter
        content = self.manager.get_parameter('nonexistent')
        assert content is None
        
    def test_set_parameter(self):
        """Test setting a parameter."""
        # Set parameter
        result = self.manager.set_parameter('newParam', 'new content')
        assert result is True
        assert self.manager.parameters['newParam'] == 'new content'
        
        # Set parameter with empty content
        result = self.manager.set_parameter('emptyParam', '')
        assert result is True
        assert self.manager.parameters['emptyParam'] == ''
        
    def test_update_parameter(self):
        """Test updating a parameter."""
        # Set initial parameter
        self.manager.parameters = {'testParam': 'old content'}
        
        # Update parameter
        result = self.manager.update_parameter('testParam', 'new content')
        assert result is True
        assert self.manager.parameters['testParam'] == 'new content'
        
        # Try to update non-existent parameter
        result = self.manager.update_parameter('nonexistent', 'content')
        assert result is False
        
    def test_delete_parameter(self):
        """Test deleting a parameter."""
        # Set up parameters
        self.manager.parameters = {
            'param1': 'content1',
            'param2': 'content2'
        }
        
        # Delete parameter
        result = self.manager.delete_parameter('param1')
        assert result is True
        assert 'param1' not in self.manager.parameters
        
        # Try to delete non-existent parameter
        result = self.manager.delete_parameter('nonexistent')
        assert result is False
        
    def test_get_all_parameters(self):
        """Test getting all parameters."""
        # Set up parameters
        test_params = {
            'param1': 'content1',
            'param2': 'content2',
            'param3': 'content3'
        }
        self.manager.parameters = test_params
        
        # Get all parameters
        all_params = self.manager.get_all_parameters()
        assert all_params == test_params
        
    def test_validate_parameters(self):
        """Test parameter validation."""
        # Set up valid parameters
        self.manager.parameters = {
            'blockMeshDict': 'valid content',
            'topoSetDict': 'valid content'
        }
        
        # Validate parameters
        is_valid, errors = self.manager.validate_parameters()
        assert is_valid is True
        assert len(errors) == 0
        
        # Test with missing required parameters
        self.manager.parameters = {}
        is_valid, errors = self.manager.validate_parameters()
        assert is_valid is False
        assert len(errors) > 0
        
    def test_export_parameters(self):
        """Test exporting parameters to different formats."""
        # Set up parameters
        self.manager.parameters = {
            'param1': 'content1',
            'param2': 'content2'
        }
        
        # Export to JSON
        export_path = Path(self.test_dir) / "export.json"
        result = self.manager.export_parameters(str(export_path), 'json')
        assert result is True
        assert export_path.exists()
        
        # Verify exported content
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
            assert exported_data == self.manager.parameters
            
    def test_import_parameters(self):
        """Test importing parameters from different formats."""
        # Create export file
        export_data = {
            'imported_param1': 'imported_content1',
            'imported_param2': 'imported_content2'
        }
        export_path = Path(self.test_dir) / "import.json"
        with open(export_path, 'w') as f:
            json.dump(export_data, f)
        
        # Import parameters
        result = self.manager.import_parameters(str(export_path), 'json')
        assert result is True
        
        # Verify parameters were imported
        for key, value in export_data.items():
            assert key in self.manager.parameters
            assert self.manager.parameters[key] == value


class TestParameterParser:
    """Test suite for ParameterParser class."""
    
    def test_parse_blockmesh_dict(self):
        """Test parsing blockMeshDict file."""
        blockmesh_content = """
convertToMeters 1e-6;
vertices
(
    (0 0 0)
    (100 0 0)
    (100 100 0)
    (0 100 0)
    (0 0 100)
    (100 0 100)
    (100 100 100)
    (0 100 100)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1)
);
"""
        
        # Parse content
        result = ParameterParser.parse_blockmesh_dict(blockmesh_content)
        
        # Verify parsing results
        assert 'convertToMeters' in result
        assert 'vertices' in result
        assert 'blocks' in result
        assert result['convertToMeters'] == '1e-6'
        
    def test_parse_li_properties(self):
        """Test parsing LiProperties file."""
        li_properties_content = """
Li
{
    DS              [0 2 -1 0 0 0 0]     1e-14;
    CS_max          [0 0 -3 0 0 0 0]    30000;
    kReact          [0 3 1 -1 0 0 0]    1e-11;
}
"""
        
        # Parse content
        result = ParameterParser.parse_li_properties(li_properties_content)
        
        # Verify parsing results
        assert 'Li' in result
        assert 'DS' in result['Li']
        assert 'CS_max' in result['Li']
        assert 'kReact' in result['Li']
        
    def test_parse_control_dict(self):
        """Test parsing controlDict file."""
        control_dict_content = """
application testSolver;
startTime 0;
endTime 10;
deltaT 0.1;
writeInterval 1;
"""
        
        # Parse content
        result = ParameterParser.parse_control_dict(control_dict_content)
        
        # Verify parsing results
        assert 'application' in result
        assert 'startTime' in result
        assert 'endTime' in result
        assert 'deltaT' in result
        assert 'writeInterval' in result
        
    def test_parse_fv_schemes(self):
        """Test parsing fvSchemes file."""
        fv_schemes_content = """
ddtSchemes
{
    default Euler;
}
gradSchemes
{
    default Gauss linear;
}
"""
        
        # Parse content
        result = ParameterParser.parse_fv_schemes(fv_schemes_content)
        
        # Verify parsing results
        assert 'ddtSchemes' in result
        assert 'gradSchemes' in result
        assert result['ddtSchemes']['default'] == 'Euler'
        assert result['gradSchemes']['default'] == 'linear'
        
    def test_parse_fv_solution(self):
        """Test parsing fvSolution file."""
        fv_solution_content = """
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
    }
}
"""
        
        # Parse content
        result = ParameterParser.parse_fv_solution(fv_solution_content)
        
        # Verify parsing results
        assert 'solvers' in result
        assert 'p' in result['solvers']
        assert 'solver' in result['solvers']['p']
        assert 'preconditioner' in result['solvers']['p']
        
    def test_parse_topo_set_dict(self):
        """Test parsing topoSetDict file."""
        topo_set_content = """
actions
(
    {
        name    cellSet;
        type    cellSet;
        action  new;
        source  boxToCell;
        sourceInfo
        {
            box (0 0 0) (100 100 100);
        }
    }
);
"""
        
        # Parse content
        result = ParameterParser.parse_topo_set_dict(topo_set_content)
        
        # Verify parsing results
        assert 'actions' in result
        assert len(result['actions']) == 1
        assert result['actions'][0]['name'] == 'cellSet'
        assert result['actions'][0]['type'] == 'cellSet'


class TestTemplateManager:
    """Test suite for TemplateManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.test_dir) / "templates"
        self.templates_dir.mkdir()
        self.manager = TemplateManager(str(self.templates_dir))
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test TemplateManager initialization."""
        assert self.manager.templates_dir == str(self.templates_dir)
        
    def test_create_template_structure(self):
        """Test creating template directory structure."""
        template_name = "testTemplate"
        
        # Create template structure
        result = self.manager.create_template_structure(template_name)
        assert result is True
        
        # Verify directories were created
        template_path = self.templates_dir / template_name
        assert template_path.exists()
        assert (template_path / "README.md").exists()
        
    def test_copy_template_files(self):
        """Test copying template files."""
        # Create source template
        source_template = self.templates_dir / "source_template"
        source_template.mkdir()
        (source_template / "README.md").write_text("Source template")
        (source_template / "test_file.txt").write_text("Test content")
        
        # Create destination
        dest_template = self.templates_dir / "dest_template"
        
        # Copy template files
        result = self.manager.copy_template_files(str(source_template), str(dest_template))
        assert result is True
        
        # Verify files were copied
        assert dest_template.exists()
        assert (dest_template / "README.md").exists()
        assert (dest_template / "test_file.txt").exists()
        
    def test_validate_template(self):
        """Test template validation."""
        # Create valid template
        template_path = self.templates_dir / "valid_template"
        template_path.mkdir()
        (template_path / "README.md").write_text("Valid template")
        
        # Validate template
        is_valid, errors = self.manager.validate_template(str(template_path))
        assert is_valid is True
        assert len(errors) == 0
        
        # Create invalid template
        invalid_template = self.templates_dir / "invalid_template"
        invalid_template.mkdir()
        
        # Validate invalid template
        is_valid, errors = self.manager.validate_template(str(invalid_template))
        assert is_valid is False
        assert len(errors) > 0
        
    def test_get_template_info(self):
        """Test getting template information."""
        # Create template with README
        template_path = self.templates_dir / "test_template"
        template_path.mkdir()
        readme_content = """
# Test Template
Description: This is a test template
Version: 1.0.0
Author: Test Author
"""
        (template_path / "README.md").write_text(readme_content)
        
        # Get template info
        info = self.manager.get_template_info(str(template_path))
        
        # Verify info extraction
        assert 'name' in info
        assert 'description' in info
        assert 'version' in info
        assert 'author' in info
        
    def test_list_available_templates(self):
        """Test listing available templates."""
        # Create multiple templates
        templates = ["template1", "template2", "template3"]
        for template_name in templates:
            template_path = self.templates_dir / template_name
            template_path.mkdir()
            (template_path / "README.md").write_text(f"{template_name} template")
        
        # List templates
        available_templates = self.manager.list_available_templates()
        
        # Verify all templates are listed
        assert len(available_templates) == len(templates)
        for template_name in templates:
            assert template_name in available_templates


class TestFileBackupManager:
    """Test suite for FileBackupManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / "backups"
        self.backup_dir.mkdir()
        self.manager = FileBackupManager(str(self.backup_dir))
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test FileBackupManager initialization."""
        assert self.manager.backup_dir == str(self.backup_dir)
        
    def test_create_backup(self):
        """Test creating file backup."""
        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Original content")
        
        # Create backup
        backup_path = self.manager.create_backup(str(test_file))
        
        # Verify backup was created
        assert backup_path is not None
        assert Path(backup_path).exists()
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
            assert backup_content == "Original content"
            
    def test_restore_backup(self):
        """Test restoring from backup."""
        # Create test file and backup
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Original content")
        
        backup_path = self.manager.create_backup(str(test_file))
        
        # Modify original file
        test_file.write_text("Modified content")
        
        # Restore from backup
        result = self.manager.restore_backup(str(test_file), backup_path)
        assert result is True
        
        # Verify file was restored
        with open(test_file, 'r') as f:
            restored_content = f.read()
            assert restored_content == "Original content"
            
    def test_list_backups(self):
        """Test listing available backups."""
        # Create test file and multiple backups
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Content")
        
        backup1 = self.manager.create_backup(str(test_file))
        backup2 = self.manager.create_backup(str(test_file))
        
        # List backups
        backups = self.manager.list_backups(str(test_file))
        
        # Verify backups are listed
        assert len(backups) == 2
        assert backup1 in backups
        assert backup2 in backups
        
    def test_cleanup_old_backups(self):
        """Test cleaning up old backups."""
        # Create test file and multiple backups
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("Content")
        
        # Create multiple backups
        for i in range(5):
            self.manager.create_backup(str(test_file))
        
        # Cleanup old backups (keep only 2)
        result = self.manager.cleanup_old_backups(str(test_file), keep_count=2)
        assert result is True
        
        # Verify only 2 backups remain
        backups = self.manager.list_backups(str(test_file))
        assert len(backups) == 2


class TestErrorRecovery:
    """Test suite for error handling and recovery utilities."""
    
    def test_handle_file_error(self):
        """Test handling file errors."""
        error_msg = handle_file_error("test_file.txt")
        assert "file" in error_msg.lower()
        assert "error" in error_msg.lower()
        
    def test_handle_permission_error(self):
        """Test handling permission errors."""
        error_msg = handle_permission_error("test_file.txt")
        assert "permission" in error_msg.lower()
        assert "error" in error_msg.lower()
        
    def test_handle_parameter_error(self):
        """Test handling parameter errors."""
        error_msg = handle_parameter_error("Invalid parameter value")
        assert "parameter" in error_msg.lower()
        assert "invalid" in error_msg.lower()
        
    def test_handle_template_error(self):
        """Test handling template errors."""
        error_msg = handle_template_error("Template not found")
        assert "template" in error_msg.lower()
        assert "not found" in error_msg.lower()
        
    def test_error_recovery_manager(self):
        """Test ErrorRecoveryManager functionality."""
        manager = ErrorRecoveryManager()
        
        # Test error logging
        manager.log_error("Test error message")
        
        # Test error recovery
        result = manager.recover_from_error("Test error")
        assert result is True
        
        # Test error statistics
        stats = manager.get_error_statistics()
        assert isinstance(stats, dict)


class TestValidatorFactory:
    """Test suite for ValidatorFactory class."""
    
    def test_create_validator(self):
        """Test creating validators."""
        # Test creating carbon validator
        carbon_validator = ValidatorFactory.create_validator("carbon")
        assert isinstance(carbon_validator, CarbonValidator)
        
        # Test creating half-cell validator
        halfcell_validator = ValidatorFactory.create_validator("halfCell")
        assert isinstance(halfcell_validator, HalfCellValidator)
        
        # Test creating full-cell validator
        fullcell_validator = ValidatorFactory.create_validator("fullCell")
        assert isinstance(fullcell_validator, FullCellValidator)
        
        # Test creating invalid validator
        with pytest.raises(ValueError):
            ValidatorFactory.create_validator("invalid_type")


class TestCarbonValidator:
    """Test suite for CarbonValidator class."""
    
    def test_validate_geometry_parameters(self):
        """Test validating geometry parameters."""
        validator = CarbonValidator()
        
        # Test valid parameters
        valid_params = {
            'length': 100.0,
            'width': 50.0,
            'height': 25.0,
            'x_division': 20,
            'y_division': 10,
            'z_division': 5
        }
        
        is_valid, errors = validator.validate_geometry_parameters(valid_params)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = {
            'length': -10.0,  # Negative value
            'width': 0.0,     # Zero value
            'height': 'invalid'  # Invalid type
        }
        
        is_valid, errors = validator.validate_geometry_parameters(invalid_params)
        assert is_valid is False
        assert len(errors) > 0
        
    def test_validate_material_parameters(self):
        """Test validating material parameters."""
        validator = CarbonValidator()
        
        # Test valid parameters
        valid_params = {
            'Ds_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11
        }
        
        is_valid, errors = validator.validate_material_parameters(valid_params)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = {
            'Ds_value': -1e-14,  # Negative value
            'CS_max': 'invalid',  # Invalid type
            'kReact': 0  # Zero value
        }
        
        is_valid, errors = validator.validate_material_parameters(invalid_params)
        assert is_valid is False
        assert len(errors) > 0


class TestHalfCellValidator:
    """Test suite for HalfCellValidator class."""
    
    def test_validate_geometry_parameters(self):
        """Test validating half-cell geometry parameters."""
        validator = HalfCellValidator()
        
        # Test valid parameters
        valid_params = {
            'length': 150.0,
            'width': 75.0,
            'height': 30.0,
            'x_division': 30,
            'y_division': 15,
            'z_division': 6
        }
        
        is_valid, errors = validator.validate_geometry_parameters(valid_params)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = {
            'length': 0.0,
            'width': -50.0,
            'height': 'invalid'
        }
        
        is_valid, errors = validator.validate_geometry_parameters(invalid_params)
        assert is_valid is False
        assert len(errors) > 0


class TestFullCellValidator:
    """Test suite for FullCellValidator class."""
    
    def test_validate_geometry_parameters(self):
        """Test validating full-cell geometry parameters."""
        validator = FullCellValidator()
        
        # Test valid parameters
        valid_params = {
            'length': 200.0,
            'width': 100.0,
            'height': 50.0,
            'x_division': 40,
            'y_division': 20,
            'z_division': 10
        }
        
        is_valid, errors = validator.validate_geometry_parameters(valid_params)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = {
            'length': 'invalid',
            'width': 0.0,
            'height': -25.0
        }
        
        is_valid, errors = validator.validate_geometry_parameters(invalid_params)
        assert is_valid is False
        assert len(errors) > 0


class TestExceptionHandler:
    """Test suite for ExceptionHandler class."""
    
    def test_handle_exception(self):
        """Test exception handling."""
        handler = ExceptionHandler()
        
        # Test handling a generic exception
        try:
            raise ValueError("Test exception")
        except Exception as e:
            result = handler.handle_exception(e, "Test context")
            assert result is True
            
    def test_get_error_context(self):
        """Test getting error context information."""
        handler = ExceptionHandler()
        
        # Test getting context
        context = handler.get_error_context()
        assert isinstance(context, dict)
        assert 'timestamp' in context
        assert 'platform' in context
        assert 'python_version' in context


class TestUtilityIntegration:
    """Integration tests for utility components."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_parameter_manager_with_file_operations(self):
        """Test ParameterManager integration with file operations."""
        # Create parameter manager
        param_dir = Path(self.test_dir) / "parameters"
        param_dir.mkdir()
        param_manager = ParameterManager(str(param_dir))
        
        # Create template manager
        template_dir = Path(self.test_dir) / "templates"
        template_dir.mkdir()
        template_manager = TemplateManager(str(template_dir))
        
        # Test creating template with parameters
        template_name = "test_template"
        result = template_manager.create_template_structure(template_name)
        assert result is True
        
        # Set parameters and save
        param_manager.parameters = {
            'blockMeshDict': 'test content',
            'LiProperties': 'material content'
        }
        
        result = param_manager.save_parameters()
        assert result is True
        
        # Verify files were created
        assert (param_dir / 'blockMeshDict').exists()
        assert (param_dir / 'LiProperties').exists()
        
    def test_error_recovery_with_parameter_manager(self):
        """Test error recovery integration with ParameterManager."""
        # Create parameter manager
        param_dir = Path(self.test_dir) / "parameters"
        param_dir.mkdir()
        param_manager = ParameterManager(str(param_dir))
        
        # Create error recovery manager
        error_manager = ErrorRecoveryManager()
        
        # Test error recovery during parameter operations
        try:
            # Simulate an error
            raise FileNotFoundError("Parameter file not found")
        except Exception as e:
            # Log error
            error_manager.log_error(str(e))
            
            # Attempt recovery
            result = error_manager.recover_from_error(str(e))
            assert result is True
            
    def test_validator_factory_integration(self):
        """Test ValidatorFactory integration with different validators."""
        # Test creating different validators
        validators = {
            'carbon': CarbonValidator,
            'halfCell': HalfCellValidator,
            'fullCell': FullCellValidator
        }
        
        for validator_type, validator_class in validators.items():
            validator = ValidatorFactory.create_validator(validator_type)
            assert isinstance(validator, validator_class)
            
            # Test validation with sample parameters
            sample_params = {
                'length': 100.0,
                'width': 50.0,
                'height': 25.0
            }
            
            is_valid, errors = validator.validate_geometry_parameters(sample_params)
            # Should be valid for basic parameters
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])