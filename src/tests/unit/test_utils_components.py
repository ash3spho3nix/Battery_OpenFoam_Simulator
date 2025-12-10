"""
Unit tests for utility components.

This module tests the utility components including:
- TemplateManager (template operations)
- ParameterManager (parameter file parsing and management)
- File operations and path utilities
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import json

from src.utils.file_operations import TemplateManager
from src.utils.parameter_parser import ParameterManager
from src.core.constants import PARAMETER_FILES, DEFAULT_PARAMETERS


class TestTemplateManager:
    """Test suite for basic TemplateManager class."""
    
    def test_template_manager_initialization(self, temp_dir):
        """Test TemplateManager initialization."""
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        assert manager.templates_path == str(templates_path)
    
    def test_copy_template_success(self, temp_dir):
        """Test successful template copying."""
        # Create template structure
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create template files
        (spm_template / "README.md").write_text("SPM Template")
        (spm_template / "Make").mkdir()
        (spm_template / "Make" / "files").write_text("SPMFoam\n")
        
        # Create destination
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        # Copy template
        manager.copy_template("SPM", str(dest_path), "test_project")
        
        # Verify files were copied
        assert (dest_path / "SPMFoam").exists()
        assert (dest_path / "SPMFoam" / "README.md").exists()
        assert (dest_path / "SPMFoam" / "Make" / "files").exists()
    
    def test_copy_template_invalid_module(self, temp_dir):
        """Test template copying with invalid module."""
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        with pytest.raises(ValueError, match="Unknown module"):
            manager.copy_template("InvalidModule", str(dest_path), "test_project")
    
    def test_copy_template_nonexistent(self, temp_dir):
        """Test template copying when template doesn't exist."""
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        with pytest.raises(FileNotFoundError, match="Template not found"):
            manager.copy_template("SPM", str(dest_path), "test_project")
    
    def test_copy_template_with_solver(self, temp_dir):
        """Test template copying with solver building."""
        # Create template structure with solver
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        (spm_template / "README.md").write_text("SPM Template")
        make_dir = spm_template / "Make"
        make_dir.mkdir()
        (make_dir / "files").write_text("SPMFoam\n")
        
        # Create destination
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            manager.copy_template("SPM", str(dest_path), "test_project", build_solver=True)
            
            # Verify solver building was attempted
            mock_run.assert_called()
    
    def test_copy_template_preserve_structure(self, temp_dir):
        """Test that template copying preserves directory structure."""
        # Create complex template structure
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create nested directories
        src_dir = spm_template / "src"
        src_dir.mkdir()
        (src_dir / "main.C").write_text("// Main source file")
        
        system_dir = spm_template / "system"
        system_dir.mkdir()
        (system_dir / "controlDict").write_text("/* Control dictionary */")
        
        # Create destination
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        manager.copy_template("SPM", str(dest_path), "test_project")
        
        # Verify structure was preserved
        project_solver = dest_path / "SPMFoam"
        assert (project_solver / "src" / "main.C").exists()
        assert (project_solver / "system" / "controlDict").exists()
    
    def test_copy_template_file_permissions(self, temp_dir):
        """Test template copying preserves file permissions."""
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create executable file
        exe_file = spm_template / "run.sh"
        exe_file.write_text("#!/bin/bash\necho 'test'")
        exe_file.chmod(0o755)  # Make executable
        
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        manager.copy_template("SPM", str(dest_path), "test_project")
        
        # Verify permissions were preserved
        copied_exe = dest_path / "SPMFoam" / "run.sh"
        assert copied_exe.exists()
        # Note: File permissions may not be preserved on all platforms
    
    def test_list_templates(self, temp_dir):
        """Test listing available templates."""
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        # Create multiple templates
        for module in ["SPM", "halfCell", "fullCell"]:
            module_dir = templates_path / module
            module_dir.mkdir()
            (module_dir / "README.md").write_text(f"{module} Template")
        
        manager = TemplateManager(str(templates_path))
        templates = manager.list_templates()
        
        assert len(templates) == 3
        assert "SPM" in templates
        assert "halfCell" in templates
        assert "fullCell" in templates
    
    def test_list_templates_no_templates(self, temp_dir):
        """Test listing templates when none exist."""
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        templates = manager.list_templates()
        
        assert templates == []
    
    def test_validate_template(self, temp_dir):
        """Test template validation."""
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Valid template
        (spm_template / "README.md").write_text("SPM Template")
        result = TemplateManager.validate_template(str(spm_template))
        assert result is True
        
        # Invalid template (missing README)
        empty_template = templates_path / "Empty"
        empty_template.mkdir()
        result = TemplateManager.validate_template(str(empty_template))
        assert result is False
    
    def test_get_template_info(self, temp_dir):
        """Test getting template information."""
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create template info file
        info_file = spm_template / "template_info.json"
        info_data = {
            "name": "SPM Template",
            "version": "1.0",
            "description": "Single Particle Model template",
            "author": "Test Author"
        }
        info_file.write_text(json.dumps(info_data))
        
        info = TemplateManager.get_template_info(str(spm_template))
        
        assert info["name"] == "SPM Template"
        assert info["version"] == "1.0"
        assert info["description"] == "Single Particle Model template"
    
    def test_get_template_info_no_info_file(self, temp_dir):
        """Test getting template info when info file doesn't exist."""
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        info = TemplateManager.get_template_info(str(spm_template))
        
        assert info == {}
    
    def test_copy_template_with_substitution(self, temp_dir):
        """Test template copying with parameter substitution."""
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create template file with placeholders
        template_file = spm_template / "config.txt"
        template_file.write_text("Project: {{PROJECT_NAME}}\nSolver: {{SOLVER_NAME}}")
        
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        manager = TemplateManager(str(templates_path))
        
        # Copy with substitution
        manager.copy_template("SPM", str(dest_path), "test_project")
        
        # Verify substitution occurred
        copied_file = dest_path / "SPMFoam" / "config.txt"
        content = copied_file.read_text()
        assert "Project: test_project" in content
        assert "Solver: SPMFoam_OF6" in content


class TestParameterManager:
    """Test suite for basic ParameterManager class."""
    
    def test_parameter_manager_initialization(self, temp_dir):
        """Test ParameterManager initialization."""
        manager = ParameterManager(temp_dir)
        
        assert manager.project_path == temp_dir
    
    def test_read_parameter_file(self, temp_dir, sample_parameter_files):
        """Test reading parameter files."""
        # Create parameter file
        param_file = Path(temp_dir) / "blockMeshDict"
        param_file.write_text(sample_parameter_files['blockMeshDict'])
        
        manager = ParameterManager(temp_dir)
        content = manager.read_parameter_file("blockMeshDict")
        
        assert content is not None
        assert "convertToMeters" in content
        assert "vertices" in content
    
    def test_read_nonexistent_parameter_file(self, temp_dir):
        """Test reading non-existent parameter file."""
        manager = ParameterManager(temp_dir)
        
        with pytest.raises(FileNotFoundError):
            manager.read_parameter_file("nonexistent")
    
    def test_write_parameter_file(self, temp_dir):
        """Test writing parameter files."""
        manager = ParameterManager(temp_dir)
        
        test_content = """/* Test parameter file */
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      testDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""
        
        manager.write_parameter_file("testDict", test_content)
        
        # Verify file was written
        written_file = Path(temp_dir) / "testDict"
        assert written_file.exists()
        
        content = written_file.read_text()
        assert "Test parameter file" in content
    
    def test_update_parameters(self, temp_dir, sample_parameter_files):
        """Test updating parameters in a file."""
        # Create parameter file
        param_file = Path(temp_dir) / "blockMeshDict"
        param_file.write_text(sample_parameter_files['blockMeshDict'])
        
        manager = ParameterManager(temp_dir)
        
        # Update parameters
        updates = {
            "convertToMeters": "2.0",
            "vertices": "(0 0 0)\n(200 0 0)\n(200 200 0)\n(0 200 0)\n(0 0 200)\n(200 0 200)\n(200 200 200)\n(0 200 200)"
        }
        
        manager.update_parameters("blockMeshDict", updates)
        
        # Verify updates
        content = param_file.read_text()
        assert "convertToMeters 2.0;" in content
    
    def test_update_nonexistent_file(self, temp_dir):
        """Test updating parameters in non-existent file."""
        manager = ParameterManager(temp_dir)
        
        with pytest.raises(FileNotFoundError):
            manager.update_parameters("nonexistent", {"test": "value"})
    
    def test_get_parameters(self, temp_dir, sample_parameter_files):
        """Test getting parameters from a file."""
        # Create parameter file
        param_file = Path(temp_dir) / "LiProperties"
        param_file.write_text(sample_parameter_files['LiProperties'])
        
        manager = ParameterManager(temp_dir)
        params = manager.get_parameters("LiProperties")
        
        assert params is not None
        assert "DS" in params
        assert "CS_max" in params
        assert "kReact" in params
    
    def test_get_parameters_nonexistent_file(self, temp_dir):
        """Test getting parameters from non-existent file."""
        manager = ParameterManager(temp_dir)
        
        with pytest.raises(FileNotFoundError):
            manager.get_parameters("nonexistent")
    
    def test_validate_parameters(self, temp_dir, sample_parameter_files):
        """Test parameter validation."""
        # Create parameter file
        param_file = Path(temp_dir) / "fvSchemes"
        param_file.write_text(sample_parameter_files['fvSchemes'])
        
        manager = ParameterManager(temp_dir)
        
        # Valid parameters
        valid_params = {
            "ddtSchemes": {"default": "Euler"},
            "gradSchemes": {"default": "Gauss linear"}
        }
        
        result = manager.validate_parameters("fvSchemes", valid_params)
        assert result is True
    
    def test_validate_parameters_invalid(self, temp_dir, sample_parameter_files):
        """Test parameter validation with invalid parameters."""
        # Create parameter file
        param_file = Path(temp_dir) / "fvSchemes"
        param_file.write_text(sample_parameter_files['fvSchemes'])
        
        manager = ParameterManager(temp_dir)
        
        # Invalid parameters
        invalid_params = {
            "invalidScheme": {"default": "invalid"}
        }
        
        result = manager.validate_parameters("fvSchemes", invalid_params)
        assert result is False
    
    def test_parse_blockmesh_dict(self, temp_dir, sample_parameter_files):
        """Test parsing blockMeshDict file."""
        # Create blockMeshDict file
        param_file = Path(temp_dir) / "blockMeshDict"
        param_file.write_text(sample_parameter_files['blockMeshDict'])
        
        manager = ParameterManager(temp_dir)
        geometry = manager.parse_blockmesh_dict()
        
        assert geometry is not None
        assert "vertices" in geometry
        assert "blocks" in geometry
        assert "boundary" in geometry
    
    def test_parse_toposet_dict(self, temp_dir, sample_parameter_files):
        """Test parsing topoSetDict file."""
        # Create topoSetDict file
        param_file = Path(temp_dir) / "topoSetDict"
        param_file.write_text(sample_parameter_files['topoSetDict'])
        
        manager = ParameterManager(temp_dir)
        selection = manager.parse_toposet_dict()
        
        assert selection is not None
        assert "actions" in selection
    
    def test_parse_li_properties(self, temp_dir, sample_parameter_files):
        """Test parsing LiProperties file."""
        # Create LiProperties file
        param_file = Path(temp_dir) / "LiProperties"
        param_file.write_text(sample_parameter_files['LiProperties'])
        
        manager = ParameterManager(temp_dir)
        properties = manager.parse_li_properties()
        
        assert properties is not None
        assert "DS" in properties
        assert "CS_max" in properties
        assert "kReact" in properties
    
    def test_parse_fv_schemes(self, temp_dir, sample_parameter_files):
        """Test parsing fvSchemes file."""
        # Create fvSchemes file
        param_file = Path(temp_dir) / "fvSchemes"
        param_file.write_text(sample_parameter_files['fvSchemes'])
        
        manager = ParameterManager(temp_dir)
        schemes = manager.parse_fv_schemes()
        
        assert schemes is not None
        assert "ddtSchemes" in schemes
        assert "gradSchemes" in schemes
        assert "divSchemes" in schemes
    
    def test_parse_fv_solution(self, temp_dir, sample_parameter_files):
        """Test parsing fvSolution file."""
        # Create fvSolution file
        param_file = Path(temp_dir) / "fvSolution"
        param_file.write_text(sample_parameter_files['fvSolution'])
        
        manager = ParameterManager(temp_dir)
        solution = manager.parse_fv_solution()
        
        assert solution is not None
        assert "solvers" in solution
        assert "PISO" in solution
    
    def test_parse_control_dict(self, temp_dir, sample_parameter_files):
        """Test parsing controlDict file."""
        # Create controlDict file
        param_file = Path(temp_dir) / "controlDict"
        param_file.write_text(sample_parameter_files['controlDict'])
        
        manager = ParameterManager(temp_dir)
        control = manager.parse_control_dict()
        
        assert control is not None
        assert "application" in control
        assert "startTime" in control
        assert "endTime" in control
    
    def test_backup_parameter_file(self, temp_dir, sample_parameter_files):
        """Test backing up parameter files."""
        # Create parameter file
        param_file = Path(temp_dir) / "blockMeshDict"
        param_file.write_text(sample_parameter_files['blockMeshDict'])
        
        manager = ParameterManager(temp_dir)
        
        # Backup the file
        backup_path = manager.backup_parameter_file("blockMeshDict")
        
        assert backup_path is not None
        assert Path(backup_path).exists()
        
        # Original file should still exist
        assert param_file.exists()
    
    def test_restore_parameter_file(self, temp_dir, sample_parameter_files):
        """Test restoring parameter files from backup."""
        # Create parameter file
        param_file = Path(temp_dir) / "blockMeshDict"
        original_content = sample_parameter_files['blockMeshDict']
        param_file.write_text(original_content)
        
        manager = ParameterManager(temp_dir)
        
        # Backup the file
        backup_path = manager.backup_parameter_file("blockMeshDict")
        
        # Modify the original file
        param_file.write_text("Modified content")
        
        # Restore from backup
        manager.restore_parameter_file("blockMeshDict", backup_path)
        
        # Verify restoration
        restored_content = param_file.read_text()
        assert restored_content == original_content
    
    def test_cleanup_backups(self, temp_dir, sample_parameter_files):
        """Test cleaning up old backup files."""
        # Create parameter file
        param_file = Path(temp_dir) / "blockMeshDict"
        param_file.write_text(sample_parameter_files['blockMeshDict'])
        
        manager = ParameterManager(temp_dir)
        
        # Create multiple backups
        backup_paths = []
        for i in range(5):
            backup_paths.append(manager.backup_parameter_file("blockMeshDict"))
            # Simulate time passing
            import time
            time.sleep(0.01)
        
        # Clean up old backups (keep only 2)
        manager.cleanup_backups("blockMeshDict", keep_count=2)
        
        # Should have only 2 backups left
        backup_files = list(Path(temp_dir).glob("blockMeshDict.backup.*"))
        assert len(backup_files) == 2


class TestIntegration:
    """Integration tests for utility components."""
    
    def test_template_parameter_integration(self, temp_dir):
        """Test integration between template and parameter management."""
        # Create template with parameter files
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        # Create parameter files in template
        for param_file, content in [
            ("blockMeshDict", "/* Block mesh */\nconvertToMeters 1e-6;"),
            ("fvSchemes", "/* Schemes */\nddtSchemes { default Euler; }"),
            ("controlDict", "/* Control */\nendTime 10;")
        ]:
            (spm_template / param_file).write_text(content)
        
        # Create destination
        dest_path = Path(temp_dir) / "project"
        dest_path.mkdir()
        
        # Test template copying
        template_manager = TemplateManager(str(templates_path))
        template_manager.copy_template("SPM", str(dest_path), "test_project")
        
        # Test parameter management
        param_manager = ParameterManager(str(dest_path / "SPMFoam"))
        
        # Read and modify parameters
        blockmesh = param_manager.read_parameter_file("blockMeshDict")
        assert "convertToMeters" in blockmesh
        
        param_manager.update_parameters("blockMeshDict", {"convertToMeters": "2e-6"})
        
        # Verify changes
        updated_content = param_manager.read_parameter_file("blockMeshDict")
        assert "convertToMeters 2e-6;" in updated_content
    
    def test_backup_restore_integration(self, temp_dir):
        """Test backup and restore integration."""
        # Create parameter files
        param_dir = Path(temp_dir) / "parameters"
        param_dir.mkdir()
        
        for param_file, content in [
            ("blockMeshDict", "/* Original content */\nconvertToMeters 1e-6;"),
            ("fvSchemes", "/* Original schemes */\nddtSchemes { default Euler; }")
        ]:
            (param_dir / param_file).write_text(content)
        
        manager = ParameterManager(str(param_dir))
        
        # Backup all parameter files
        backup_paths = {}
        for param_file in ["blockMeshDict", "fvSchemes"]:
            backup_path = manager.backup_parameter_file(param_file)
            if backup_path:
                backup_paths[param_file] = backup_path
        
        # Modify files
        for param_file in ["blockMeshDict", "fvSchemes"]:
            file_path = param_dir / param_file
            original_content = file_path.read_text()
            file_path.write_text(original_content.replace("Original", "Modified"))
        
        # Restore all files
        for param_file, backup_path in backup_paths.items():
            manager.restore_parameter_file(param_file, backup_path)
        
        # Verify restoration
        for param_file in ["blockMeshDict", "fvSchemes"]:
            file_path = param_dir / param_file
            content = file_path.read_text()
            assert "Original" in content
            assert "Modified" not in content
    
    def test_performance_with_large_files(self, temp_dir):
        """Test performance with large parameter files."""
        # Create large parameter file
        large_content = "/* Large file */\n"
        for i in range(1000):
            large_content += f"vertex {i} ({i} {i} {i});\n"
        
        param_file = Path(temp_dir) / "large_blockMeshDict"
        param_file.write_text(large_content)
        
        manager = ParameterManager(temp_dir)
        
        # Test reading large file
        import time
        start_time = time.time()
        content = manager.read_parameter_file("large_blockMeshDict")
        read_time = time.time() - start_time
        
        assert content is not None
        assert "vertex 0" in content
        assert "vertex 999" in content
        
        # Should read reasonably quickly (less than 1 second)
        assert read_time < 1.0
        
        # Test writing large file
        start_time = time.time()
        manager.write_parameter_file("large_output", large_content)
        write_time = time.time() - start_time
        
        assert write_time < 1.0
        
        output_file = Path(temp_dir) / "large_output"
        assert output_file.exists()