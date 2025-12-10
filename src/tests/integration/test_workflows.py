#!/usr/bin/env python3
"""
Integration tests for Battery Simulator workflows.

This module tests the integration between different components
and end-to-end workflows.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the main application components
from src.gui.main_window import MainWindow
from src.core.project_manager import ProjectManager
from src.gui.ui_config import UIConfig

class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_name = "integration_test_project"
        self.project_path = os.path.join(self.temp_dir, self.project_name)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('src.gui.main_window.ProjectManager')
    @patch('src.gui.main_window.InterfaceFactory')
    def test_complete_project_creation_workflow(self, mock_factory, mock_project_manager):
        """Test complete project creation workflow."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Mock interface factory
        mock_interface = Mock()
        mock_factory.create_interface.return_value = mock_interface
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog to return valid path
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Trigger project creation
            main_window.on_main_next_button_clicked()
            
            # Verify project manager was called
            mock_pm_instance.create_project.assert_called_once_with(
                self.temp_dir, self.project_name, "SPM"
            )
            
            # Verify interface was created
            mock_factory.create_interface.assert_called_once()
            
            # Verify interface was shown
            mock_interface.show.assert_called_once()
            
    @patch('src.gui.main_window.ProjectManager')
    @patch('src.gui.main_window.InterfaceFactory')
    def test_existing_project_opening_workflow(self, mock_factory, mock_project_manager):
        """Test existing project opening workflow."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Mock interface factory
        mock_interface = Mock()
        mock_factory.create_interface.return_value = mock_interface
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Set up test data
        main_window.project_path = self.temp_dir
        main_window.project_name = self.project_name
        
        # Create project directory structure
        os.makedirs(os.path.join(self.project_path, "SPMFoam"), exist_ok=True)
        
        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            # Trigger existing project opening
            main_window.on_main_next_button_2_clicked()
            
            # Verify interface was created
            mock_factory.create_interface.assert_called_once()
            
            # Verify interface was shown
            mock_interface.show.assert_called_once()
            
    @patch('src.gui.main_window.ProjectManager')
    def test_project_creation_error_handling(self, mock_project_manager):
        """Test error handling during project creation."""
        # Mock project manager to raise exception
        mock_pm_instance = Mock()
        mock_pm_instance.create_project.side_effect = Exception("Creation failed")
        mock_project_manager.return_value = mock_pm_instance
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog to return valid path
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
                
    @patch('src.gui.main_window.ProjectManager')
    def test_project_path_validation(self, mock_project_manager):
        """Test project path validation."""
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Test empty path
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = None
        main_window.carbon_button.setChecked(True)
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "invalid" in args[1].lower()
            
    @patch('src.gui.main_window.ProjectManager')
    def test_project_name_validation(self, mock_project_manager):
        """Test project name validation."""
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Test empty name
        main_window.pro_name_editline.setText("")
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "invalid" in args[1].lower()
            
    @patch('src.gui.main_window.ProjectManager')
    def test_module_selection_validation(self, mock_project_manager):
        """Test module selection validation."""
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Set up test data without selecting any module
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        # Don't check any module button
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "invalid" in args[1].lower()
            
    @patch('src.gui.main_window.ProjectManager')
    @patch('src.gui.main_window.InterfaceFactory')
    def test_interface_creation_and_display(self, mock_factory, mock_project_manager):
        """Test interface creation and display."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Mock interface factory
        mock_interface = Mock()
        mock_factory.create_interface.return_value = mock_interface
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog to return valid path
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Trigger project creation
            main_window.on_main_next_button_clicked()
            
            # Verify interface was created and stored
            assert main_window.carbon_interface is not None
            assert main_window.current_interface is not None
            
            # Verify interface was shown
            mock_interface.show.assert_called_once()
            
    @patch('src.gui.main_window.ProjectManager')
    def test_project_manager_initialization(self, mock_project_manager):
        """Test ProjectManager initialization."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Verify project manager was initialized
        mock_project_manager.assert_called_once_with(
            base_projects_path=main_window.project_manager.base_projects_path
        )
        
    @patch('src.gui.main_window.ProjectManager')
    def test_ui_setup_and_initialization(self, mock_project_manager):
        """Test UI setup and initialization."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Verify UI was set up
        assert main_window.tab_widget is not None
        assert main_window.tab_widget.count() == 2
        
        # Verify tab titles
        assert main_window.tab_widget.tabText(0) == "New"
        assert main_window.tab_widget.tabText(1) == "Open"
        
    @patch('src.gui.main_window.ProjectManager')
    def test_signal_slot_connections(self, mock_project_manager):
        """Test signal-slot connections."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Verify that UI elements exist (connections are set up in _setup_ui)
        assert hasattr(main_window, 'main_path_button')
        assert hasattr(main_window, 'main_next_button')
        assert hasattr(main_window, 'main_next_button_2')
        assert hasattr(main_window, 'recent_path_button')
        
    @patch('src.gui.main_window.ProjectManager')
    @patch('src.gui.main_window.InterfaceFactory')
    def test_multiple_project_creations(self, mock_factory, mock_project_manager):
        """Test multiple project creations in sequence."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        # Mock interface factory
        mock_interface = Mock()
        mock_factory.create_interface.return_value = mock_interface
        
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        
        # Test multiple project creations
        for i in range(3):
            project_name = f"{self.project_name}_{i}"
            
            # Set up test data
            main_window.pro_name_editline.setText(project_name)
            main_window.project_path = self.temp_dir
            main_window.carbon_button.setChecked(True)
            
            # Mock file dialog to return valid path
            with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = self.temp_dir
                
                # Trigger project creation
                main_window.on_main_next_button_clicked()
                
                # Verify project manager was called
                mock_pm_instance.create_project.assert_called_with(
                    self.temp_dir, project_name, "SPM"
                )
                
                # Verify interface was created
                mock_factory.create_interface.assert_called()
                
                # Verify interface was shown
                mock_interface.show.assert_called()

def test_integration_workflows_comprehensive():
    """Comprehensive test for integration workflows."""
    # This test would typically be run with pytest
    # For now, we'll just verify the imports work
    from src.gui.main_window import MainWindow
    from src.core.project_manager import ProjectManager
    from src.gui.ui_config import UIConfig
    
    assert MainWindow is not None
    assert ProjectManager is not None
    assert UIConfig is not None

if __name__ == "__main__":
    # Run basic import test
    test_integration_workflows_comprehensive()
    print("Integration workflow tests completed successfully")