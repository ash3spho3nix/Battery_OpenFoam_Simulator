#!/usr/bin/env python3
"""
Integration tests for complete workflows.
This module tests end-to-end workflows including project creation,
interface navigation, and simulation execution.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from src.core.project_manager import ProjectManager
from src.gui.main_window import MainWindow
from src.gui.ui_config import UIConfig
from src.gui.interfaces.base_interface import BaseInterface

class TestIntegrationWorkflows:
    """Integration test cases for complete workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_name = "integration_test_project"
        self.project_path = os.path.join(self.temp_dir, self.project_name)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_project_lifecycle(self, qtbot):
        """Test complete project lifecycle from creation to cleanup."""
        # 1. Create project
        pm = ProjectManager(self.temp_dir)
        result = pm.create_project_safe(
            self.temp_dir,
            self.project_name,
            "SPM",
            validate_template=False,
            create_backup=False
        )
        assert result is True, "Project creation failed"
        assert os.path.exists(self.project_path), "Project directory not created"
        
        # 2. Verify project structure
        required_dirs = ['SPMFoam', 'Case', 'Case/system', 'Case/constant', 'Case/0']
        for dir_path in required_dirs:
            full_path = os.path.join(self.project_path, dir_path)
            assert os.path.exists(full_path), f"Required directory missing: {dir_path}"
        
        # 3. Verify project metadata
        metadata_file = os.path.join(self.project_path, "project_metadata.json")
        assert os.path.exists(metadata_file), "Project metadata not created"
        
        import json
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        assert metadata['project_name'] == self.project_name
        assert metadata['template_name'] == 'SPM'
        assert 'creation_date' in metadata
        
        # 4. Test project info retrieval
        project_info = pm.get_project_info(self.project_name)
        assert project_info is not None
        assert project_info['project_name'] == self.project_name
        
        # 5. Test project listing
        projects = pm.list_projects()
        assert self.project_name in projects
        
        print("✓ Complete project lifecycle test passed")
    
    def test_main_window_workflow(self, qtbot):
        """Test MainWindow workflow integration."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Test UI setup
        assert main_window.tab_widget.count() == 2
        assert main_window.tab_widget.tabText(0) == "New"
        assert main_window.tab_widget.tabText(1) == "Open"
        
        # Test path selection
        main_window.project_path = self.temp_dir
        main_window.main_path_label.setText(self.temp_dir)
        assert main_window.project_path == self.temp_dir
        
        # Test project name setting
        main_window.pro_name_editline.setText(self.project_name)
        assert main_window.pro_name_editline.text() == self.project_name
        
        # Test module selection
        main_window.carbon_button.setChecked(True)
        assert main_window.carbon_button.isChecked()
        assert not main_window.halfcell_button.isChecked()
        assert not main_window.fullcell_button.isChecked()
        
        print("✓ MainWindow workflow test passed")
    
    @patch('src.gui.main_window.ProjectManager')
    @patch('src.gui.main_window.InterfaceFactory')
    def test_project_creation_workflow(self, mock_factory, mock_pm, qtbot):
        """Test complete project creation workflow."""
        # Setup mocks
        mock_pm_instance = Mock()
        mock_pm.return_value = mock_pm_instance
        mock_pm_instance.create_project_safe.return_value = True
        
        mock_interface = Mock()
        mock_factory.create_interface.return_value = mock_interface
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Mock QMessageBox
            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                # Trigger project creation
                main_window.on_main_next_button_clicked()
                
                # Verify project manager was called
                mock_pm_instance.create_project_safe.assert_called_once_with(
                    self.temp_dir,
                    self.project_name,
                    "SPM",
                    validate_template=True,
                    create_backup=True
                )
                
                # Verify interface was created
                mock_factory.create_interface.assert_called_once()
                
                # Verify interface was shown
                assert main_window.current_interface is not None
                assert main_window.isHidden() is True  # MainWindow should be hidden
        
        print("✓ Project creation workflow test passed")
    
    def test_interface_creation_and_navigation(self, qtbot):
        """Test interface creation and navigation."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Test interface factory
        from src.gui.interface_factory import InterfaceFactory
        
        # Test carbon interface creation
        carbon_interface = InterfaceFactory.create_interface("carbon", main_window, ui_config)
        assert carbon_interface is not None
        assert isinstance(carbon_interface, BaseInterface)
        qtbot.addWidget(carbon_interface)
        
        # Test half-cell interface creation
        halfcell_interface = InterfaceFactory.create_interface("halfcell", main_window, ui_config)
        assert halfcell_interface is not None
        assert isinstance(halfcell_interface, BaseInterface)
        qtbot.addWidget(halfcell_interface)
        
        # Test full-cell interface creation
        fullcell_interface = InterfaceFactory.create_interface("fullcell", main_window, ui_config)
        assert fullcell_interface is not None
        assert isinstance(fullcell_interface, BaseInterface)
        qtbot.addWidget(fullcell_interface)
        
        print("✓ Interface creation and navigation test passed")
    
    @patch('src.gui.main_window.ProjectManager')
    def test_existing_project_opening(self, mock_pm, qtbot):
        """Test opening existing projects."""
        # Setup project structure
        os.makedirs(os.path.join(self.project_path, "SPMFoam"), exist_ok=True)
        os.makedirs(os.path.join(self.project_path, "Case"), exist_ok=True)
        
        # Create metadata file
        import json
        metadata = {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "template_name": "SPM",
            "creation_date": "2023-01-01T00:00:00",
            "status": "active"
        }
        with open(os.path.join(self.project_path, "project_metadata.json"), 'w') as f:
            json.dump(metadata, f)
        
        # Setup mocks
        mock_pm_instance = Mock()
        mock_pm.return_value = mock_pm_instance
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set up test data
        main_window.project_path = self.project_path
        main_window.project_name = self.project_name
        
        # Mock interface factory
        with patch('src.gui.main_window.InterfaceFactory') as mock_factory:
            mock_interface = Mock()
            mock_factory.create_interface.return_value = mock_interface
            
            # Mock file operations
            with patch('builtins.open', mock_open(read_data=self.project_path)):
                # Trigger existing project opening
                main_window.on_main_next_button_2_clicked()
                
                # Verify interface was created
                mock_factory.create_interface.assert_called_once()
                assert main_window.current_interface is not None
        
        print("✓ Existing project opening test passed")
    
    def test_error_handling_workflow(self, qtbot):
        """Test error handling in workflows."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Test empty project name
        main_window.pro_name_editline.setText("")
        main_window.project_path = self.temp_dir
        
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            mock_msgbox.assert_called_once()
        
        # Test invalid project path
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = None
        
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            mock_msgbox.assert_called_once()
        
        print("✓ Error handling workflow test passed")
    
    @patch('src.gui.main_window.ProjectManager')
    def test_project_creation_failure_handling(self, mock_pm, qtbot):
        """Test handling of project creation failures."""
        # Setup mock to raise exception
        mock_pm_instance = Mock()
        mock_pm_instance.create_project_safe.side_effect = Exception("Creation failed")
        mock_pm.return_value = mock_pm_instance
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Mock QMessageBox for error case
            with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
                # Trigger project creation
                main_window.on_main_next_button_clicked()
                
                # Verify error message was shown
                mock_critical.assert_called_once()
                args = mock_critical.call_args[0]
                assert "Failed to create project" in args[1]
        
        print("✓ Project creation failure handling test passed")
    
    def test_ui_configuration_workflow(self, qtbot):
        """Test UI configuration workflow."""
        # Test different UI modes
        modes = ['auto_detect', 'ui_files', 'hand_coded']
        
        for mode in modes:
            ui_config = UIConfig()
            ui_config.set_mode_from_string(mode)
            
            main_window = MainWindow(ui_config=ui_config)
            qtbot.addWidget(main_window)
            
            # Verify window is created successfully
            assert main_window is not None
            assert main_window.windowTitle() == "Battery Simulator"
            
            # Clean up
            main_window.close()
        
        print("✓ UI configuration workflow test passed")
    
    def test_project_validation_workflow(self, qtbot):
        """Test project validation workflow."""
        pm = ProjectManager(self.temp_dir)
        
        # Test valid project
        result = pm.create_project_safe(
            self.temp_dir,
            self.project_name,
            "SPM",
            validate_template=False,
            create_backup=False
        )
        assert result is True
        
        # Test project validation
        is_valid = pm.validate_project(self.project_name)
        assert is_valid is True
        
        # Test invalid project (missing files)
        invalid_project_path = os.path.join(self.temp_dir, "invalid_project")
        os.makedirs(invalid_project_path, exist_ok=True)
        
        is_valid = pm.validate_project("invalid_project")
        assert is_valid is False
        
        print("✓ Project validation workflow test passed")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s"])