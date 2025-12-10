"""
Unit tests for core application components.

This module tests the core application logic including:
- BatterySimulatorApp (main application window)
- ProjectManager (project creation and management)
- Constants (application configuration and parameters)
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

from src.core.application import BatterySimulatorApp
from src.core.project_manager import ProjectManager
from src.core.constants import (
    APP_NAME, APP_VERSION, SUPPORTED_MODULES, SOLVER_NAMES,
    PARAMETER_FILES, DEFAULT_PARAMETERS, ERROR_MESSAGES, SUCCESS_MESSAGES
)


class TestBatterySimulatorApp:
    """Test suite for BatterySimulatorApp class."""
    
    @pytest.fixture
    def app_instance(self, qt_app):
        """Create a BatterySimulatorApp instance for testing."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
            yield app
            app.close()
    
    def test_app_initialization(self, qt_app):
        """Test that the application initializes correctly."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
            
            assert app.windowTitle() == APP_NAME
            assert app.minimumSize().width() == 800
            assert app.minimumSize().height() == 640
            assert app.maximumSize().width() == 800
            assert app.maximumSize().height() == 640
            
            # Check that project state is initialized
            assert app.project_path is None
            assert app.project_name is None
            
            app.close()
    
    def test_app_with_ui_config(self, qt_app):
        """Test application initialization with UI configuration."""
        mock_ui_config = Mock()
        mock_ui_config.mode = 'auto_detect'
        
        with patch('src.gui.ui_config.UIConfig', return_value=mock_ui_config):
            app = BatterySimulatorApp(ui_config=mock_ui_config)
            
            assert app.ui_config == mock_ui_config
            app.close()
    
    def test_setup_ui(self, qt_app):
        """Test UI setup functionality."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
            
            # Check that tab widget was created
            assert hasattr(app, 'tab_widget')
            assert app.tab_widget is not None
            
            # Check that both tabs were created
            assert app.tab_widget.tabText(0) == "New"
            assert app.tab_widget.tabText(1) == "Open"
            
            app.close()
    
    def test_project_creation_success(self, qt_app, temp_dir):
        """Test successful project creation."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Mock the project manager
        mock_pm = Mock()
        app.project_manager = mock_pm
        
        # Set up UI components
        app.project_path = temp_dir
        app.project_name = "test_project"
        app.carbon_button.setChecked(True)
        
        # Mock interface factory
        with patch('src.gui.interface_factory.InterfaceFactory') as mock_factory:
            mock_interface = Mock()
            mock_factory.create_interface.return_value = mock_interface
            
            # Mock the hide method
            app.hide = Mock()
            
            # Trigger project creation
            app.on_main_next_button_clicked()
            
            # Verify project manager was called
            mock_pm.create_project.assert_called_once_with(
                temp_dir, "test_project", "SPM"
            )
            
            # Verify interface factory was called
            mock_factory.create_interface.assert_called_once()
            
            app.close()
    
    def test_project_creation_invalid_name(self, qt_app):
        """Test project creation with invalid name."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up invalid project name
        app.project_path = "/valid/path"
        app.project_name = ""
        
        # Mock QMessageBox to avoid GUI interaction
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert args[1] == "Hint"
            assert ERROR_MESSAGES["invalid_name"] in args[2]
        
        app.close()
    
    def test_project_creation_invalid_path(self, qt_app):
        """Test project creation with invalid path."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up invalid project path
        app.project_path = None
        app.project_name = "test_project"
        
        # Mock QMessageBox to avoid GUI interaction
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert args[1] == "Hint"
            assert ERROR_MESSAGES["invalid_path"] in args[2]
        
        app.close()
    
    def test_project_creation_existing_project(self, qt_app, temp_dir):
        """Test project creation when project already exists."""
        # Create existing project directory
        project_dir = Path(temp_dir) / "test_project"
        project_dir.mkdir()
        
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project details
        app.project_path = temp_dir
        app.project_name = "test_project"
        app.carbon_button.setChecked(True)
        
        # Mock QMessageBox to avoid GUI interaction
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert args[1] == "BatteryFOAM"
            assert ERROR_MESSAGES["name_exists"] in args[2]
        
        app.close()
    
    def test_project_creation_error_handling(self, qt_app, temp_dir):
        """Test project creation error handling."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project details
        app.project_path = temp_dir
        app.project_name = "test_project"
        app.carbon_button.setChecked(True)
        
        # Mock project manager to raise exception
        mock_pm = Mock()
        mock_pm.create_project.side_effect = Exception("Test error")
        app.project_manager = mock_pm
        
        # Mock QMessageBox to avoid GUI interaction
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert args[1] == "Error"
            assert "Test error" in args[2]
        
        app.close()
    
    def test_path_selection(self, qt_app):
        """Test project path selection."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Mock QFileDialog
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = "/selected/path"
            
            app.on_main_path_button_clicked()
            
            # Verify path was set
            assert app.project_path == "/selected/path"
            assert app.main_path_label.text() == "/selected/path"
            assert app.main_next_button.isEnabled()
        
        app.close()
    
    def test_path_selection_cancelled(self, qt_app):
        """Test project path selection when cancelled."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Mock QFileDialog returning empty string (cancelled)
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = ""
            
            app.on_main_path_button_clicked()
            
            # Verify path was not set
            assert app.project_path is None
            assert not app.main_next_button.isEnabled()
        
        app.close()


class TestProjectManager:
    """Test suite for ProjectManager class."""
    
    def test_project_manager_initialization(self):
        """Test ProjectManager initialization."""
        pm = ProjectManager()
        assert pm is not None
    
    def test_list_available_templates(self, temp_dir):
        """Test listing available templates."""
        # Create mock template directory structure
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create mock template directories
        for module in SUPPORTED_MODULES.keys():
            module_dir = templates_dir / module
            module_dir.mkdir()
            # Create a README file to make it a valid template
            (module_dir / "README.md").write_text("Test template")
        
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            templates = pm.list_available_templates()
            
            assert len(templates) == len(SUPPORTED_MODULES)
            for module in SUPPORTED_MODULES.keys():
                assert module in templates
    
    def test_list_available_templates_no_templates(self):
        """Test listing templates when no templates exist."""
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', Path("/nonexistent/path")):
            templates = pm.list_available_templates()
            assert templates == {}
    
    def test_create_project_success(self, temp_dir):
        """Test successful project creation."""
        # Create mock template
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        spm_template = templates_dir / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create project
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            pm.create_project(temp_dir, "test_project", "SPM")
        
        # Verify project was created
        project_path = Path(temp_dir) / "test_project"
        assert project_path.exists()
        assert (project_path / "SPMFoam").exists()
    
    def test_create_project_invalid_module(self, temp_dir):
        """Test project creation with invalid module."""
        pm = ProjectManager()
        
        with pytest.raises(ValueError, match="Unknown module"):
            pm.create_project(temp_dir, "test_project", "InvalidModule")
    
    def test_create_project_template_not_found(self, temp_dir):
        """Test project creation when template is not found."""
        pm = ProjectManager()
        
        with pytest.raises(FileNotFoundError, match="Template not found"):
            pm.create_project(temp_dir, "test_project", "SPM")
    
    def test_create_project_name_exists(self, temp_dir):
        """Test project creation when project name already exists."""
        # Create existing project
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        pm = ProjectManager()
        
        with pytest.raises(FileExistsError, match="already exists"):
            pm.create_project(temp_dir, "test_project", "SPM")
    
    def test_create_project_with_solver(self, temp_dir):
        """Test project creation with solver building."""
        # Create mock template with solver
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        spm_template = templates_dir / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create solver directory
        solver_dir = spm_template / "SPMFoam"
        solver_dir.mkdir()
        (solver_dir / "Make").mkdir()
        make_files = solver_dir / "Make" / "files"
        make_files.write_text("SPMFoam\n")
        
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                pm.create_project(temp_dir, "test_project", "SPM", build_solver=True)
                
                # Verify solver building was attempted
                mock_run.assert_called()
    
    def test_create_project_solver_build_failure(self, temp_dir):
        """Test project creation when solver building fails."""
        # Create mock template with solver
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        spm_template = templates_dir / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create solver directory
        solver_dir = spm_template / "SPMFoam"
        solver_dir.mkdir()
        (solver_dir / "Make").mkdir()
        make_files = solver_dir / "Make" / "files"
        make_files.write_text("SPMFoam\n")
        
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 1
                
                # Should still create project but log solver build failure
                pm.create_project(temp_dir, "test_project", "SPM", build_solver=True)
                
                # Verify solver building was attempted
                mock_run.assert_called()


class TestConstants:
    """Test suite for constants module."""
    
    def test_app_constants(self):
        """Test application constants."""
        assert APP_NAME == "BatteryFOAM"
        assert APP_VERSION == "1.0.0"
    
    def test_supported_modules(self):
        """Test supported modules configuration."""
        assert "SPM" in SUPPORTED_MODULES
        assert "halfCell" in SUPPORTED_MODULES
        assert "fullCell" in SUPPORTED_MODULES
        
        assert SUPPORTED_MODULES["SPM"] == "Single Particle Model"
        assert SUPPORTED_MODULES["halfCell"] == "Pseudo-2D Model (Half Cell)"
        assert SUPPORTED_MODULES["fullCell"] == "Pseudo-2D Model (Full Cell)"
    
    def test_solver_names(self):
        """Test solver name mappings."""
        assert SOLVER_NAMES["SPM"] == "SPMFoam_OF6"
        assert SOLVER_NAMES["halfCell"] == "halfCellFoam_OF6"
        assert SOLVER_NAMES["fullCell"] == "fullCellFoam_OF6"
    
    def test_parameter_files(self):
        """Test parameter file mappings."""
        assert "blockMeshDict" in PARAMETER_FILES
        assert "topoSetDict" in PARAMETER_FILES
        assert "LiProperties" in PARAMETER_FILES
        assert "fvSchemes" in PARAMETER_FILES
        assert "fvSolution" in PARAMETER_FILES
        assert "controlDict" in PARAMETER_FILES
    
    def test_default_parameters(self):
        """Test default parameter values."""
        assert "length" in DEFAULT_PARAMETERS
        assert "width" in DEFAULT_PARAMETERS
        assert "height" in DEFAULT_PARAMETERS
        assert "radius" in DEFAULT_PARAMETERS
        assert "unit" in DEFAULT_PARAMETERS
    
    def test_error_messages(self):
        """Test error message constants."""
        assert "invalid_path" in ERROR_MESSAGES
        assert "invalid_name" in ERROR_MESSAGES
        assert "name_exists" in ERROR_MESSAGES
    
    def test_success_messages(self):
        """Test success message constants."""
        assert "project_created" in SUCCESS_MESSAGES
        assert "parameters_modified" in SUCCESS_MESSAGES
        assert "solver_built" in SUCCESS_MESSAGES


class TestIntegration:
    """Integration tests for core components."""
    
    def test_app_project_manager_integration(self, qt_app, temp_dir):
        """Test integration between app and project manager."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project details
        app.project_path = temp_dir
        app.project_name = "integration_test"
        app.carbon_button.setChecked(True)
        
        # Mock interface creation to avoid GUI issues
        with patch('src.gui.interface_factory.InterfaceFactory.create_interface') as mock_create:
            mock_create.return_value = None
            
            # Mock hide to avoid GUI issues
            app.hide = Mock()
            
            # Trigger project creation
            app.on_main_next_button_clicked()
            
            # Verify project was created
            project_path = Path(temp_dir) / "integration_test"
            assert project_path.exists()
        
        app.close()
    
    def test_project_creation_workflow(self, temp_dir):
        """Test complete project creation workflow."""
        # Create mock templates
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        for module in SUPPORTED_MODULES.keys():
            module_dir = templates_dir / module
            module_dir.mkdir()
            (module_dir / "README.md").write_text(f"{module} Template")
        
        # Test project creation for each module
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            for module in SUPPORTED_MODULES.keys():
                project_name = f"test_{module}"
                pm.create_project(temp_dir, project_name, module)
                
                # Verify project structure
                project_path = Path(temp_dir) / project_name
                assert project_path.exists()
                
                solver_name = SOLVER_NAMES[module]
                solver_path = project_path / solver_name
                assert solver_path.exists()
    
    @pytest.mark.parametrize("module", SUPPORTED_MODULES.keys())
    def test_module_specific_project_creation(self, temp_dir, module):
        """Test project creation for each specific module."""
        # Create mock template
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        module_template = templates_dir / module
        module_template.mkdir()
        (module_template / "README.md").write_text(f"{module} Template")
        
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_dir):
            pm.create_project(temp_dir, f"test_{module}", module)
            
            # Verify project was created
            project_path = Path(temp_dir) / f"test_{module}"
            assert project_path.exists()