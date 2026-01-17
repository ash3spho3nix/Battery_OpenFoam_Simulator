#!/usr/bin/env python3
"""
Unit tests for the main application (MainWindow).

This module tests the MainWindow class functionality including
project creation, opening, and UI setup.
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

class TestMainWindow:
    """Test cases for MainWindow class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_name = "test_project"
        self.project_path = os.path.join(self.temp_dir, self.project_name)
        
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_main_window_initialization(self, qtbot):
        """Test MainWindow initialization."""
        # Create UI config
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Verify initialization
        assert main_window is not None
        assert main_window.project_path is None
        assert main_window.project_name is None
        assert main_window.carbon_interface is None
        assert main_window.halfcell_interface is None
        assert main_window.fullcell_interface is None
        assert main_window.current_interface is None
        
    def test_main_window_title(self, qtbot):
        """Test MainWindow title setting."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Verify window title
        assert main_window.windowTitle() == "Battery Simulator"
        
    def test_main_window_size(self, qtbot):
        """Test MainWindow size constraints."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Verify size constraints
        assert main_window.minimumSize().width() == 800
        assert main_window.minimumSize().height() == 640
        assert main_window.maximumSize().width() == 800
        assert main_window.maximumSize().height() == 640
        
    def test_ui_setup(self, qtbot):
        """Test UI setup."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Verify tab widget exists
        assert hasattr(main_window, 'tab_widget')
        assert main_window.tab_widget is not None
        
        # Verify tabs
        assert main_window.tab_widget.count() == 2
        assert main_window.tab_widget.tabText(0) == "New"
        assert main_window.tab_widget.tabText(1) == "Open"
        
    def test_path_selection(self, qtbot):
        """Test path selection functionality."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Mock the file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Trigger path selection
            main_window.on_main_path_button_clicked()
            
            # Verify path was set
            assert main_window.project_path == self.temp_dir
            assert main_window.main_path_label.text() == self.temp_dir
            
    def test_project_name_validation(self, qtbot):
        """Test project name validation."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Test empty name
        main_window.pro_name_editline.setText("")
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "invalid" in args[1].lower()
            
    def test_project_path_validation(self, qtbot):
        """Test project path validation."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set name but no path
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = None
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "invalid" in args[1].lower()
            
    @patch('src.gui.main_window.ProjectManager')
    def test_project_creation_success(self, mock_project_manager, qtbot):
        """Test successful project creation."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set up test data
        main_window.pro_name_editline.setText(self.project_name)
        main_window.project_path = self.temp_dir
        main_window.carbon_button.setChecked(True)
        
        # Mock file dialog to return valid path
        with patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = self.temp_dir
            
            # Mock QMessageBox for success case
            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                # Mock interface factory
                with patch('src.gui.main_window.InterfaceFactory') as mock_factory:
                    mock_interface = Mock()
                    mock_factory.create_interface.return_value = mock_interface
                    
                    # Trigger project creation
                    main_window.on_main_next_button_clicked()
                    
                    # Verify project manager was called
                    mock_pm_instance.create_project.assert_called_once_with(
                        self.temp_dir, self.project_name, "SPM"
                    )
                    
                    # Verify interface was created
                    mock_factory.create_interface.assert_called_once()
                    
    @patch('src.gui.main_window.ProjectManager')
    def test_project_creation_failure(self, mock_project_manager, qtbot):
        """Test project creation failure."""
        # Mock project manager to raise exception
        mock_pm_instance = Mock()
        mock_pm_instance.create_project.side_effect = Exception("Creation failed")
        mock_project_manager.return_value = mock_pm_instance
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
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
                
    def test_module_selection(self, qtbot):
        """Test module selection functionality."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Test SPM selection
        main_window.carbon_button.setChecked(True)
        assert main_window.carbon_button.isChecked()
        assert not main_window.halfcell_button.isChecked()
        assert not main_window.fullcell_button.isChecked()
        
        # Test half-cell selection
        main_window.halfcell_button.setChecked(True)
        assert not main_window.carbon_button.isChecked()
        assert main_window.halfcell_button.isChecked()
        assert not main_window.fullcell_button.isChecked()
        
        # Test full-cell selection
        main_window.fullcell_button.setChecked(True)
        assert not main_window.carbon_button.isChecked()
        assert not main_window.halfcell_button.isChecked()
        assert main_window.fullcell_button.isChecked()
        
    def test_name_hint_dialog(self, qtbot):
        """Test project name hint dialog."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msgbox:
            main_window.on_main_name_hint_clicked()
            
            # Verify hint message was shown
            mock_msgbox.assert_called_once()
            args = mock_msgbox.call_args[0]
            assert "supports" in args[1].lower()
            assert "underscore" in args[1].lower()
            
    def test_recent_project_opening(self, qtbot):
        """Test opening recent projects."""
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Create recent file
        recent_file_path = Path(self.temp_dir) / "most_recent_file"
        with open(recent_file_path, 'w') as f:
            f.write(self.project_path)
            
        # Mock the recent file path
        with patch('src.gui.main_window.Path') as mock_path:
            mock_path.return_value.parent.parent.__truediv__.return_value = Path(self.temp_dir)
            
            # Trigger recent project opening
            main_window.on_recent_path_button_clicked()
            
            # Verify recent path was set
            assert main_window.recent_path_label.text() == self.project_path
            
    @patch('src.gui.main_window.ProjectManager')
    def test_existing_project_opening(self, mock_project_manager, qtbot):
        """Test opening existing projects."""
        # Mock project manager
        mock_pm_instance = Mock()
        mock_project_manager.return_value = mock_pm_instance
        
        ui_config = UIConfig()
        main_window = MainWindow(ui_config=ui_config)
        qtbot.addWidget(main_window)
        
        # Set up test data
        main_window.project_path = self.temp_dir
        main_window.project_name = self.project_name
        
        # Create project directory structure
        os.makedirs(os.path.join(self.project_path, "SPMFoam"), exist_ok=True)
        
        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            # Mock interface factory
            with patch('src.gui.main_window.InterfaceFactory') as mock_factory:
                mock_interface = Mock()
                mock_factory.create_interface.return_value = mock_interface
                
                # Trigger existing project opening
                main_window.on_main_next_button_2_clicked()
                
                # Verify interface was created
                mock_factory.create_interface.assert_called_once()
