"""
Unit tests for GUI components.

This module tests the GUI components including:
- UILoader (basic and enhanced)
- UIConfig (configuration management)
- InterfaceFactory (interface creation and fallback)
- BaseInterface (base interface functionality)
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

from src.gui.ui_loader import UILoader
from src.gui.ui_loader_enhanced import UILoader, UIValidationError
from src.gui.ui_config import UIConfig, UILoadingMode

from src.gui.interface_factory import InterfaceFactory, InterfaceCreationError
from src.gui.interfaces.base_interface import BaseInterface


class TestUILoader:
    """Test suite for basic UILoader class."""
    
    def test_load_ui_file_success(self, qt_app, temp_dir, sample_ui_content):
        """Test successful .ui file loading."""
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        
        widget = UILoader.load_ui_file(str(ui_file))
        
        assert widget is not None
        assert widget.objectName() == "TestWidget"
        assert widget.windowTitle() == "Test Widget"
    
    def test_load_ui_file_not_found(self, qt_app):
        """Test loading non-existent .ui file."""
        nonexistent_file = "/path/that/does/not/exist.ui"
        
        with pytest.raises(FileNotFoundError):
            UILoader.load_ui_file(nonexistent_file)
    
    def test_get_ui_path(self):
        """Test UI path generation."""
        ui_path = UILoader.get_ui_path("test")
        
        # Should be in resources/ui directory
        assert "resources" in ui_path
        assert "ui" in ui_path
        assert "test.ui" in ui_path
    
    def test_ui_file_exists(self, temp_dir, sample_ui_content):
        """Test UI file existence checking."""
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        
        assert UILoader.ui_file_exists("test", temp_dir) is True
        assert UILoader.ui_file_exists("nonexistent", temp_dir) is False
    
    def test_get_available_ui_files(self, temp_dir, sample_ui_content):
        """Test getting available UI files."""
        # Create multiple UI files
        ui_files = ["test1.ui", "test2.ui", "invalid.txt"]
        for filename in ui_files:
            ui_file = Path(temp_dir) / filename
            if filename.endswith(".ui"):
                ui_file.write_text(sample_ui_content)
            else:
                ui_file.write_text("invalid content")
        
        available_files = UILoader.get_available_ui_files(temp_dir)
        
        assert "test1" in available_files
        assert "test2" in available_files
        assert "invalid" not in available_files
    
    def test_load_main_window(self, qt_app, temp_dir, sample_ui_content):
        """Test loading main window .ui file."""
        # Create mainwindow.ui file
        ui_file = Path(temp_dir) / "mainwindow.ui"
        ui_file.write_text(sample_ui_content)
        
        with patch('src.gui.ui_loader.UI_LOADER_PATH', temp_dir):
            widget = UILoader.load_main_window()
            
            assert widget is not None
            assert widget.objectName() == "TestWidget"
    
    def test_load_interface_files(self, qt_app, temp_dir, sample_ui_content):
        """Test loading various interface .ui files."""
        interface_files = [
            "carboninterface.ui",
            "halfcellinterface.ui", 
            "fullcellfoam.ui",
            "resultinterface.ui"
        ]
        
        for filename in interface_files:
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(sample_ui_content)
        
        with patch('src.gui.ui_loader.UI_LOADER_PATH', temp_dir):
            # Test carbon interface
            widget = UILoader.load_carbon_interface()
            assert widget is not None
            
            # Test half-cell interface
            widget = UILoader.load_halfcell_interface()
            assert widget is not None
            
            # Test full-cell interface
            widget = UILoader.load_fullcell_interface()
            assert widget is not None
            
            # Test result interface
            widget = UILoader.load_result_interface()
            assert widget is not None


class TestUILoaderEnhanced:
    """Test suite for enhanced UILoader class."""
    
    def test_load_ui_file_with_validation(self, qt_app, temp_dir, sample_ui_content):
        """Test enhanced .ui file loading with validation."""
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        
        widget = UILoader.load_ui_file(str(ui_file))
        
        assert widget is not None
        assert widget.objectName() == "TestWidget"
        assert widget.windowTitle() == "Test Widget"
    
    def test_load_invalid_ui_file(self, qt_app, temp_dir):
        """Test loading invalid .ui file."""
        invalid_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestWidget</class>
 <widget class="QWidget" name="TestWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <!-- Missing closing tags -->
'''
        ui_file = Path(temp_dir) / "invalid.ui"
        ui_file.write_text(invalid_content)
        
        # Should raise exception for invalid XML
        with pytest.raises(Exception):
            UILoader.load_ui_file(str(ui_file))
    
    def test_ui_integrity_validation(self, temp_dir, sample_ui_content):
        """Test UI file integrity validation."""
        # Valid UI file
        valid_ui = Path(temp_dir) / "valid.ui"
        valid_ui.write_text(sample_ui_content)
        assert UILoader.validate_ui_integrity(str(valid_ui)) is True
        
        # Invalid UI file
        invalid_ui = Path(temp_dir) / "invalid.ui"
        invalid_ui.write_text("invalid xml content")
        assert UILoader.validate_ui_integrity(str(invalid_ui)) is False
        
        # Non-existent file
        nonexistent = "/path/that/does/not/exist.ui"
        assert UILoader.validate_ui_integrity(nonexistent) is False
    
    def test_ui_structure_validation(self, temp_dir, sample_ui_content):
        """Test UI structure validation."""
        # Valid structure
        valid_ui = Path(temp_dir) / "valid.ui"
        valid_ui.write_text(sample_ui_content)
        assert UILoader._validate_ui_structure(str(valid_ui)) is True
        
        # Invalid structure
        invalid_ui = Path(temp_dir) / "invalid.ui"
        invalid_ui.write_text("invalid content")
        assert UILoader._validate_ui_structure(str(invalid_ui)) is False
    
    def test_ui_metadata_caching(self, qt_app, temp_dir, sample_ui_content):
        """Test UI metadata caching."""
        # Clear cache
        UILoader.clear_ui_cache()
        
        # Create and load UI file
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        widget = UILoader.load_ui_file(str(ui_file))
        
        # Check that metadata was cached
        metadata = UILoader.get_ui_metadata(str(ui_file))
        assert metadata is not None
        assert 'checksum' in metadata
        assert 'object_name' in metadata
        assert 'widget_count' in metadata
    
    def test_diagnose_ui_loading_issue(self, temp_dir, sample_ui_content):
        """Test UI loading issue diagnosis."""
        # Create valid UI file
        ui_file = Path(temp_dir) / "diagnose_test.ui"
        ui_file.write_text(sample_ui_content)
        
        # Run diagnosis
        diagnosis = UILoader.diagnose_ui_loading_issue("diagnose_test", temp_dir)
        
        # Check diagnosis results
        assert diagnosis['ui_name'] == 'diagnose_test'
        assert diagnosis['success'] is True
        assert len(diagnosis['issues']) == 0
    
    def test_get_available_ui_files_with_validation(self, temp_dir, sample_ui_content):
        """Test getting available UI files with integrity validation."""
        # Create multiple UI files
        ui_files = ["test1.ui", "test2.ui", "invalid.ui"]
        for i, filename in enumerate(ui_files[:2]):
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(sample_ui_content)
        
        # Create invalid UI file
        invalid_file = Path(temp_dir) / "invalid.ui"
        invalid_file.write_text("invalid content")
        
        # Get available files
        available_files = UILoader.get_available_ui_files(temp_dir)
        
        # Should only return valid UI files
        assert "test1" in available_files
        assert "test2" in available_files
        assert "invalid" not in available_files
    
    def test_ui_file_exists_with_validation(self, temp_dir, sample_ui_content):
        """Test ui_file_exists with integrity validation."""
        # Create valid UI file
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        
        # Should return True for valid file
        assert UILoader.ui_file_exists("test", temp_dir) is True
        
        # Should return False for invalid file
        invalid_file = Path(temp_dir) / "invalid.ui"
        invalid_file.write_text("invalid content")
        assert UILoader.ui_file_exists("invalid", temp_dir) is False


class TestUIConfig:
    """Test suite for UIConfig class."""
    
    def test_default_configuration(self):
        """Test default UI configuration."""
        config = UIConfig()
        
        assert config.mode == UILoadingMode.AUTO_DETECT
        assert config.prefer_ui_files is True
        assert config.fallback_to_hand_coded is True
        assert config.ui_base_path is None
    
    def test_environment_variable_configuration(self):
        """Test configuration from environment variables."""
        # Set environment variables
        os.environ['BATTERY_SIM_UI_MODE'] = 'ui_files'
        os.environ['BATTERY_SIM_UI_PATH'] = '/custom/ui/path'
        
        try:
            config = UIConfig.from_environment()
            
            assert config.mode == UILoadingMode.UI_FILES
            assert config.ui_base_path == '/custom/ui/path'
        finally:
            # Clean up environment
            if 'BATTERY_SIM_UI_MODE' in os.environ:
                del os.environ['BATTERY_SIM_UI_MODE']
            if 'BATTERY_SIM_UI_PATH' in os.environ:
                del os.environ['BATTERY_SIM_UI_PATH']
    
    def test_command_line_configuration(self):
        """Test configuration from command line arguments."""
        # Mock command line arguments
        class MockArgs:
            ui_mode = 'hand_coded'
            ui_path = '/command/line/path'
            no_fallback = True
        
        args = MockArgs()
        config = UIConfig.from_command_line(args)
        
        assert config.mode == UILoadingMode.HAND_CODED
        assert config.ui_base_path == '/command/line/path'
        assert config.fallback_to_hand_coded is False
    
    def test_mode_setting(self):
        """Test mode setting."""
        config = UIConfig()
        
        config.set_mode(UILoadingMode.UI_FILES)
        assert config.mode == UILoadingMode.UI_FILES
        
        config.set_mode(UILoadingMode.HAND_CODED)
        assert config.mode == UILoadingMode.HAND_CODED
        
        config.set_mode(UILoadingMode.AUTO_DETECT)
        assert config.mode == UILoadingMode.AUTO_DETECT
    
    def test_prefer_ui_files_setting(self):
        """Test prefer_ui_files setting."""
        config = UIConfig()
        
        config.set_prefer_ui_files(False)
        assert config.prefer_ui_files is False
        
        config.set_prefer_ui_files(True)
        assert config.prefer_ui_files is True
    
    def test_fallback_setting(self):
        """Test fallback setting."""
        config = UIConfig()
        
        config.set_fallback_enabled(False)
        assert config.fallback_to_hand_coded is False
        
        config.set_fallback_enabled(True)
        assert config.fallback_to_hand_coded is True
    
    def test_ui_base_path_setting(self):
        """Test UI base path setting."""
        config = UIConfig()
        
        config.set_ui_base_path('/custom/path')
        assert config.ui_base_path == '/custom/path'
        
        config.set_ui_base_path(None)
        assert config.ui_base_path is None
    
    def test_should_load_ui_files(self):
        """Test should_load_ui_files logic."""
        config = UIConfig()
        
        # Auto-detect with prefer_ui_files=True
        config.mode = UILoadingMode.AUTO_DETECT
        config.prefer_ui_files = True
        assert config.should_load_ui_files() is True
        
        # Auto-detect with prefer_ui_files=False
        config.prefer_ui_files = False
        assert config.should_load_ui_files() is False
        
        # UI_FILES mode
        config.mode = UILoadingMode.UI_FILES
        assert config.should_load_ui_files() is True
        
        # HAND_CODED mode
        config.mode = UILoadingMode.HAND_CODED
        assert config.should_load_ui_files() is False
    
    def test_should_fallback_to_hand_coded(self):
        """Test should_fallback_to_hand_coded logic."""
        config = UIConfig()
        
        config.fallback_to_hand_coded = True
        assert config.should_fallback_to_hand_coded() is True
        
        config.fallback_to_hand_coded = False
        assert config.should_fallback_to_hand_coded() is False
    
    def test_configuration_serialization(self):
        """Test configuration serialization and deserialization."""
        # Create a configured instance
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path('/test/path')
        config.set_fallback_enabled(False)
        
        # Serialize to dict
        config_dict = config.to_dict()
        assert config_dict['mode'] == 'auto_detect'
        assert config_dict['ui_base_path'] == '/test/path'
        assert config_dict['fallback_to_hand_coded'] is False
        
        # Deserialize from dict
        new_config = UIConfig.from_dict(config_dict)
        assert new_config.mode == UILoadingMode.AUTO_DETECT
        assert new_config.ui_base_path == '/test/path'
        assert new_config.fallback_to_hand_coded is False
    
    def test_invalid_mode_handling(self):
        """Test handling of invalid mode values."""
        config = UIConfig()
        
        # Test invalid mode in from_dict
        invalid_dict = {'mode': 'invalid_mode'}
        config_from_dict = UIConfig.from_dict(invalid_dict)
        assert config_from_dict.mode == UILoadingMode.AUTO_DETECT  # Should default to AUTO_DETECT


class TestInterfaceFactory:
    """Test suite for basic InterfaceFactory class."""
    
    def test_create_interface_success(self, qt_app):
        """Test successful interface creation."""
        config = UIConfig()
        config.set_mode(UILoadingMode.HAND_CODED)
        
        # Mock the hand-coded interface creation
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            
            assert interface == mock_instance
            mock_carbon.assert_called_once()
    
    def test_create_interface_invalid_type(self):
        """Test interface creation with invalid type."""
        config = UIConfig()
        
        with pytest.raises(ValueError, match="Unknown interface type"):
            InterfaceFactory.create_interface("invalid_type", ui_config=config)
    
    def test_create_main_window(self, qt_app):
        """Test main window creation."""
        with patch('src.gui.ui_loader.UILoader.load_main_window') as mock_load:
            mock_widget = Mock()
            mock_load.return_value = mock_widget
            
            window = InterfaceFactory.create_main_window()
            
            assert window == mock_widget
            mock_load.assert_called_once()
    
    def test_get_available_interfaces(self):
        """Test getting available interfaces."""
        interfaces = InterfaceFactory.get_available_interfaces()
        
        assert "carbon" in interfaces
        assert "halfcell" in interfaces
        assert "fullcell" in interfaces
        assert "result" in interfaces
    
    def test_interface_exists(self):
        """Test interface existence checking."""
        assert InterfaceFactory.interface_exists("carbon") is True
        assert InterfaceFactory.interface_exists("nonexistent") is False


class TestInterfaceFactoryEnhanced:
    """Test suite for enhanced InterfaceFactory class."""
    
    def test_create_interface_with_fallback_success(self, qt_app):
        """Test interface creation with successful fallback."""
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        
        # Mock successful hand-coded creation
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            
            assert interface == mock_instance
    
    def test_create_interface_all_methods_fail(self):
        """Test interface creation when all methods fail."""
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        
        # Mock all creation methods to fail
        with patch('src.gui.ui_loader_enhanced.UILoader.validate_ui_integrity', return_value=False):
            with patch('src.gui.ui_loader.UILoader.ui_file_exists', return_value=False):
                with patch('src.gui.interfaces.carbon_interface.CarbonInterface', side_effect=ImportError("Module not found")):
                    with pytest.raises(InterfaceCreationError):
                        InterfaceFactory.create_interface("carbon", ui_config=config)
    
    def test_create_interface_ui_enhanced_success(self, qt_app, temp_dir, sample_ui_content):
        """Test interface creation using enhanced UI loading."""
        # Create valid UI file
        ui_file = Path(temp_dir) / "carboninterface.ui"
        ui_file.write_text(sample_ui_content)
        
        config = UIConfig()
        config.set_mode(UILoadingMode.UI_FILES)
        config.set_ui_base_path(temp_dir)
        
        interface = InterfaceFactory.create_interface("carbon", ui_config=config)
        
        assert interface is not None
    
    def test_create_interface_hand_coded_success(self, qt_app):
        """Test interface creation using hand-coded widgets."""
        config = UIConfig()
        config.set_mode(UILoadingMode.HAND_CODED)
        
        # Mock the hand-coded interface
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            
            assert interface == mock_instance
    
    def test_interface_caching(self, qt_app):
        """Test interface caching functionality."""
        # Clear cache
        InterfaceFactory.clear_cache()
        
        config = UIConfig()
        config.set_mode(UILoadingMode.HAND_CODED)
        
        # Mock the hand-coded interface
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            # Create interface twice
            interface1 = InterfaceFactory.create_interface("carbon", ui_config=config, use_cache=True)
            interface2 = InterfaceFactory.create_interface("carbon", ui_config=config, use_cache=True)
            
            # Should only create once due to caching
            assert mock_carbon.call_count == 1
            assert interface1 == interface2
    
    def test_creation_statistics(self, qt_app):
        """Test creation statistics tracking."""
        # Reset statistics
        InterfaceFactory._creation_stats = {'success': 0, 'fallbacks': 0, 'failures': 0}
        
        config = UIConfig()
        config.set_mode(UILoadingMode.HAND_CODED)
        
        # Mock successful creation
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            InterfaceFactory.create_interface("carbon", ui_config=config)
            
            stats = InterfaceFactory.get_creation_stats()
            assert stats['success'] > 0
    
    def test_diagnose_interface_creation(self, qt_app, temp_dir):
        """Test interface creation diagnosis."""
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path(temp_dir)
        
        # Run diagnosis
        diagnosis = InterfaceFactory.diagnose_interface_creation("carbon", config)
        
        # Check diagnosis structure
        assert 'interface_type' in diagnosis
        assert 'test_results' in diagnosis
        assert 'issues' in diagnosis
        assert 'recommendations' in diagnosis
    
    def test_fallback_mechanism(self, qt_app, temp_dir):
        """Test the fallback mechanism when primary method fails."""
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path(temp_dir)
        
        # Create an invalid UI file to force fallback
        ui_file = Path(temp_dir) / "carboninterface.ui"
        ui_file.write_text("invalid xml content")
        
        # Mock hand-coded interface
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            # Should fall back to hand-coded when UI loading fails
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            
            assert interface == mock_instance


class TestBaseInterface:
    """Test suite for BaseInterface class."""
    
    def test_base_interface_initialization(self, qt_app):
        """Test BaseInterface initialization."""
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        assert interface.interface_type == "baseinterface"
        assert interface.tab_widget is not None
        assert interface.terminal_output is not None
        assert interface.command_input is not None
        
        interface.close()
    
    def test_base_interface_with_ui_config(self, qt_app):
        """Test BaseInterface initialization with UI configuration."""
        mock_ui_config = Mock()
        mock_ui_config.mode = 'auto_detect'
        
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface(ui_config=mock_ui_config)
        
        assert interface.ui_config == mock_ui_config
        interface.close()
    
    def test_setup_ui(self, qt_app):
        """Test UI setup."""
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        # Check that tabs were created
        assert interface.tab_widget.count() >= 5  # Should have multiple tabs
        
        interface.close()
    
    def test_process_controller_connection(self, qt_app):
        """Test process controller signal connection."""
        mock_process_controller = Mock()
        mock_process_controller.output_received = Mock()
        mock_process_controller.error_received = Mock()
        mock_process_controller.process_started = Mock()
        mock_process_controller.process_finished = Mock()
        
        with patch('src.openfoam.process_controller.ProcessController', return_value=mock_process_controller):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        # Check that signals were connected
        assert mock_process_controller.output_received.connect.called
        assert mock_process_controller.error_received.connect.called
        assert mock_process_controller.process_started.connect.called
        assert mock_process_controller.process_finished.connect.called
        
        interface.close()
    
    def test_set_project_paths(self, qt_app):
        """Test setting project paths."""
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        test_project_path = "/test/project/path"
        test_project_name = "test_project"
        
        interface.set_project_paths(test_project_path, test_project_name)
        
        assert interface.project_path == test_project_path
        assert interface.project_name == test_project_name
        assert interface.case_path == Path(test_project_path) / test_project_name / "Case"
        assert interface.solver_path == Path(test_project_path) / test_project_name
        
        interface.close()
    
    def test_signal_emission(self, qt_app):
        """Test signal emission."""
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        # Mock signal emission
        with patch.object(interface, 'simulation_started') as mock_started:
            with patch.object(interface, 'simulation_stopped') as mock_stopped:
                with patch.object(interface, 'simulation_paused') as mock_paused:
                    with patch.object(interface, 'output_received') as mock_output:
                        with patch.object(interface, 'error_received') as mock_error:
                            # Test simulation started
                            interface._on_process_started()
                            mock_started.emit.assert_called_once()
                            
                            # Test simulation stopped
                            interface._on_process_finished(0)
                            mock_stopped.emit.assert_called_once()
                            
                            # Test simulation paused
                            interface._resume_simulation()  # This should trigger paused signal
                            # Note: This is a simplified test - actual pause/resume logic would be more complex
        
        interface.close()
    
    def test_terminal_output_limiting(self, qt_app):
        """Test terminal output limiting to prevent memory issues."""
        with patch('src.openfoam.process_controller.ProcessController'):
            with patch('src.utils.file_operations.TemplateManager'):
                interface = BaseInterface()
        
        # Simulate adding many lines to terminal output
        for i in range(1500):  # More than the 1000 line limit
            interface._on_process_output(f"Line {i}")
        
        # The terminal should handle this gracefully without crashing
        assert interface.terminal_output is not None
        
        interface.close()


class TestIntegration:
    """Integration tests for GUI components."""
    
    def test_ui_config_with_interface_factory(self, qt_app):
        """Test integration between UIConfig and InterfaceFactory."""
        # Test auto-detect mode
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        
        # Should attempt UI loading first, then fall back
        with patch('src.gui.ui_loader_enhanced.UILoader.validate_ui_integrity', return_value=False):
            with patch('src.gui.ui_loader.UILoader.ui_file_exists', return_value=False):
                with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
                    mock_instance = Mock()
                    mock_carbon.return_value = mock_instance
                    
                    interface = InterfaceFactory.create_interface("carbon", ui_config=config)
                    
                    assert interface == mock_instance
    
    def test_ui_loader_with_ui_config(self, temp_dir, sample_ui_content):
        """Test integration between UILoader and UIConfig."""
        # Create UI file
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(sample_ui_content)
        
        config = UIConfig()
        config.set_mode(UILoadingMode.UI_FILES)
        config.set_ui_base_path(temp_dir)
        
        # Test that UIConfig settings are respected
        assert UILoader.ui_file_exists("test", temp_dir) is True
        
        # Test with different mode
        config.set_mode(UILoadingMode.HAND_CODED)
        assert not config.should_load_ui_files()
    
    def test_complete_ui_loading_workflow(self, qt_app, temp_dir, sample_ui_content):
        """Test complete UI loading workflow."""
        # Create UI files
        ui_files = ["mainwindow.ui", "carboninterface.ui"]
        for filename in ui_files:
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(sample_ui_content)
        
        # Test enhanced UI loading
        config = UIConfig()
        config.set_mode(UILoadingMode.UI_FILES)
        config.set_ui_base_path(temp_dir)
        
        # Should successfully load UI files
        with patch('src.gui.ui_loader_enhanced.UILoader.validate_ui_integrity', return_value=True):
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            assert interface is not None
            
            window = InterfaceFactory.create_main_window(ui_config=config)
            assert window is not None
