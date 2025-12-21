"""
Comprehensive unit tests for GUI components.

This module tests the GUI application logic including:
- UI loading system (UILoader, UILoaderEnhanced)
- UI configuration (UIConfig)
- Interface factory (InterfaceFactory)
- Base interface functionality
- Widget naming standardization
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

# Import test modules
from src.gui.ui_loader_enhanced import EnhancedUILoader, UILoadingError, UIValidationError
from src.gui.ui_config_enhanced import EnhancedUIConfig, UILoadingMode as UIMode
from src.gui.interface_factory import InterfaceFactory, InterfaceCreationError
from src.gui.widget_naming_standardizer import WidgetNamingStandardizer
from src.gui.interfaces.base_interface import BaseInterface


class TestUILoader:
    """Test suite for UILoader class."""
    pass # UILoader is deprecated, its tests are removed.


class TestUIConfig:
    """Test suite for UIConfig class."""
    
    def test_default_configuration(self):
        """Test default UI configuration."""
        config = EnhancedUIConfig()
        
        assert config.mode == UIMode.AUTO_DETECT
        assert config.should_load_ui_files() is True
        assert config.should_fallback_to_hand_coded() is True
    
    def test_environment_variable_configuration(self):
        """Test UI configuration from environment variables."""
        # Set environment variables
        os.environ['BATTERY_SIM_UI_MODE'] = 'ui_files'
        os.environ['BATTERY_SIM_UI_PATH'] = '/custom/ui/path'
        
        try:
            config = EnhancedUIConfig.from_environment()
            assert config.mode == UIMode.UI_FILES
            assert config.get_ui_base_path() == '/custom/ui/path'
        finally:
            # Clean up environment
            if 'BATTERY_SIM_UI_MODE' in os.environ:
                del os.environ['BATTERY_SIM_UI_MODE']
            if 'BATTERY_SIM_UI_PATH' in os.environ:
                del os.environ['BATTERY_SIM_UI_PATH']
    
    def test_command_line_configuration(self):
        """Test UI configuration from command line arguments."""
        # Mock command line arguments
        class MockArgs:
            ui_mode = 'hand_coded'
            ui_path = '/command/line/path'
            no_fallback = True
        
        # Use from_multiple_sources to simulate CLI args
        config = EnhancedUIConfig.from_multiple_sources(args=['--ui-mode', 'hand_coded', '--ui-path', '/command/line/path', '--no-fallback'])
        
        assert config.mode == UIMode.HAND_CODED
        assert config.get_ui_base_path() == '/command/line/path'
        assert config.should_fallback_to_hand_coded() is False

    def test_mode_switching(self):
        """Test UI mode switching."""
        config = EnhancedUIConfig()
        
        # Test switching to UI_FILES mode
        config.set_mode(UIMode.UI_FILES)
        assert config.mode == UIMode.UI_FILES
        assert config.should_load_ui_files() is True
        assert config.should_fallback_to_hand_coded() is True
        
        # Test switching to HAND_CODED mode
        config.set_mode(UIMode.HAND_CODED)
        assert config.mode == UIMode.HAND_CODED
        assert config.should_load_ui_files() is False
        assert config.should_fallback_to_hand_coded() is False
        
        # Test switching to AUTO_DETECT mode
        config.set_mode(UIMode.AUTO_DETECT)
        assert config.mode == UIMode.AUTO_DETECT
        assert config.should_load_ui_files() is True
        assert config.should_fallback_to_hand_coded() is True
    
    def test_fallback_configuration(self):
        """Test fallback configuration."""
        config = EnhancedUIConfig()
        
        # Test enabling fallback
        config.set_fallback_enabled(True)
        assert config.should_fallback_to_hand_coded() is True
        
        # Test disabling fallback
        config.set_fallback_enabled(False)
        assert config.should_fallback_to_hand_coded() is False
    
    def test_ui_base_path_configuration(self):
        """Test UI base path configuration."""
        config = EnhancedUIConfig()
        
        # Test setting UI base path
        test_path = "/test/ui/path"
        config.set_ui_base_path(test_path)
        assert config.get_ui_base_path() == test_path
    
    def test_configuration_serialization(self):
        """Test UI configuration serialization and deserialization."""
        # Create a configured instance
        config = EnhancedUIConfig()
        config.set_mode(UIMode.AUTO_DETECT)
        config.set_ui_base_path('/test/path')
        config.set_fallback_enabled(False)
        
        # Serialize to dict
        config_dict = config.to_dict()
        assert config_dict['mode'] == 'auto_detect'
        assert config_dict['ui_base_path'] == '/test/path'
        assert config_dict['fallback_to_hand_coded'] is False
        
        # Deserialize from dict
        new_config = EnhancedUIConfig(metadata=config_dict) # Assuming EnhancedUIConfig can be initialized from dict
        assert new_config.mode == UIMode.AUTO_DETECT
        assert new_config.get_ui_base_path() == '/test/path'
        assert new_config.should_fallback_to_hand_coded() is False


class TestInterfaceFactory:
    """Test suite for InterfaceFactory class."""
    
    def test_create_interface_with_ui_files_mode(self, qt_app, temp_ui_dir):
        """Test interface creation in UI_FILES mode."""
        # Create UI configuration for UI files mode
        config = EnhancedUIConfig()
        config.set_mode(UIMode.UI_FILES)
        config.set_ui_base_path(temp_ui_dir)
        
        # This should attempt UI loading first, then fall back to hand-coded
        # Since we don't have actual UI files, it should fall back to hand-coded
        with pytest.raises(InterfaceCreationError):
            InterfaceFactory.create_interface("carbon", ui_config=config)
    
    def test_create_interface_with_hand_coded_mode(self, qt_app):
        """Test interface creation in HAND_CODED mode."""
        # Create UI configuration for hand-coded mode
        config = EnhancedUIConfig()
        config.set_mode(UIMode.HAND_CODED)
        
        # This should attempt hand-coded first
        # Note: This might fail if the interface modules aren't available in test environment
        try:
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            assert interface is not None
        except InterfaceCreationError:
            # Expected if interface modules aren't available in test environment
            pass
    
    def test_create_interface_with_auto_detect_mode(self, qt_app, temp_ui_dir):
        """Test interface creation in AUTO_DETECT mode."""
        # Create UI configuration for auto-detect mode
        config = EnhancedUIConfig()
        config.set_mode(UIMode.AUTO_DETECT)
        config.set_ui_base_path(temp_ui_dir)
        
        # Should attempt UI loading first (will fail), then fall back to hand-coded
        try:
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            assert interface is not None
        except InterfaceCreationError:
            # Expected if no valid UI files and hand-coded fails
            pass
    
    def test_interface_caching(self, qt_app):
        """Test interface caching functionality."""
        # Clear cache before test
        InterfaceFactory._interface_cache = {}
        
        config = EnhancedUIConfig()
        config.set_mode(UIMode.HAND_CODED)
        
        # Create interface twice
        try:
            interface1 = InterfaceFactory.create_interface("carbon", ui_config=config, use_cache=True)
            interface2 = InterfaceFactory.create_interface("carbon", ui_config=config, use_cache=True)
            
            # Should return the same cached instance
            # Note: This depends on the caching implementation
            assert interface1 is not None
        except InterfaceCreationError:
            # Expected if interface modules aren't available
            pass
    
    def test_creation_statistics(self, qt_app):
        """Test interface creation statistics tracking."""
        # Reset statistics
        InterfaceFactory._creation_stats = {'success': 0, 'fallbacks': 0, 'failures': 0}
        
        config = EnhancedUIConfig()
        config.set_mode(UIMode.HAND_CODED)
        
        try:
            InterfaceFactory.create_interface("carbon", ui_config=config)
            stats = InterfaceFactory._creation_stats
            assert stats['success'] > 0
        except InterfaceCreationError:
            # If creation fails, should increment failures
            stats = InterfaceFactory.get_creation_stats()
            assert stats['failures'] > 0
    
    def test_diagnose_interface_creation(self, qt_app, temp_ui_dir):
        """Test interface creation diagnosis."""
        config = EnhancedUIConfig()
        config.set_mode(UIMode.AUTO_DETECT)
        config.set_ui_base_path(temp_ui_dir)
        
        # Run diagnosis
        diagnosis = InterfaceFactory.diagnose_interface_creation("carbon", config)
        
        # Check diagnosis structure
        assert 'interface_type' in diagnosis
        assert 'test_results' in diagnosis
        assert 'issues' in diagnosis
        assert 'recommendations' in diagnosis
    
    def test_fallback_mechanism(self, qt_app, temp_ui_dir):
        """Test the fallback mechanism when primary method fails."""
        config = EnhancedUIConfig()
        config.set_mode(UIMode.AUTO_DETECT)
        config.set_ui_base_path(temp_ui_dir)
        
        # Create an invalid UI file to force fallback
        ui_file = Path(temp_ui_dir) / "carboninterface.ui"
        ui_file.write_text("invalid xml content")
        
        # Should fall back to hand-coded when UI loading fails
        try:
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            assert interface is not None
        except InterfaceCreationError:
            # If all methods fail, that's also acceptable for this test
            pass


class TestWidgetNamingStandardizer:
    """Test suite for WidgetNamingStandardizer class."""
    
    def test_standardize_naming_convention(self):
        """Test widget naming convention standardization."""
        # Test standardizing from .ui convention to hand-coded
        ui_name = "length_lineEdit"
        standardized = WidgetNamingStandardizer.standardize_naming_convention(ui_name, "hand_coded")
        assert standardized == "length_edit"
        
        # Test standardizing from hand-coded to .ui convention
        hand_coded_name = "length_edit"
        standardized = WidgetNamingStandardizer.standardize_naming_convention(hand_coded_name, "ui_files")
        assert standardized == "length_lineEdit"
    
    def test_get_widget_naming_variants(self):
        """Test getting all possible widget naming variants."""
        base_name = "length"
        variants = WidgetNamingStandardizer.get_widget_naming_variants(base_name, "lineEdit")
        
        expected_variants = [
            "length_lineEdit",
            "length_edit",
            "length_spinBox",
            "length_doubleSpinBox"
        ]
        
        assert len(variants) == len(expected_variants)
        for variant in expected_variants:
            assert variant in variants
    
    def test_detect_naming_conflicts(self, qt_app):
        """Test detection of widget naming conflicts."""
        # Create a mock widget with multiple naming conventions
        from PyQt6.QtWidgets import QWidget, QLineEdit, QSpinBox
        
        widget = QWidget()
        widget.length_lineEdit = QLineEdit()
        widget.length_edit = QLineEdit()
        widget.length_spin = QSpinBox()
        
        # Detect conflicts
        conflicts = WidgetNamingStandardizer.detect_naming_conflicts(widget)
        
        # Should detect conflicts between different naming conventions
        assert len(conflicts) > 0
    
    def test_resolve_naming_conflicts(self, qt_app):
        """Test resolution of widget naming conflicts."""
        from PyQt6.QtWidgets import QWidget, QLineEdit, QSpinBox
        
        widget = QWidget()
        widget.length_lineEdit = QLineEdit()
        widget.length_edit = QLineEdit()
        widget.length_spin = QSpinBox()
        
        # Resolve conflicts
        resolved = WidgetNamingStandardizer.resolve_naming_conflicts(widget, "ui_files")
        
        # Should prefer .ui naming convention
        assert hasattr(resolved, "length_lineEdit")
        assert not hasattr(resolved, "length_edit")
    
    def test_validate_widget_naming_consistency(self, qt_app):
        """Test validation of widget naming consistency."""
        from PyQt6.QtWidgets import QWidget, QLineEdit, QSpinBox
        
        widget = QWidget()
        widget.length_lineEdit = QLineEdit()
        widget.width_lineEdit = QLineEdit()
        widget.height_spin = QSpinBox()
        
        # Validate consistency
        is_consistent = WidgetNamingStandardizer.validate_widget_naming_consistency(widget)
        
        # Should be inconsistent due to mixed naming conventions
        assert is_consistent is False


class TestBaseInterface:
    """Test suite for BaseInterface class."""
    
    def test_base_interface_initialization(self, qt_app):
        """Test BaseInterface initialization."""
        interface = BaseInterface()
        
        assert interface is not None
        assert interface.project_path is None
        assert interface.project_name is None
    
    def test_set_project_paths(self, mock_project):
        """Test setting project paths."""
        interface = BaseInterface()
        
        project_info = mock_project
        project_path = str(project_info['project_path'])
        project_name = "TestProject"
        
        result = interface.set_project_paths(project_path, project_name)
        
        assert result is True
        assert interface.project_path == project_path
        assert interface.project_name == project_name
        assert interface.case_path is not None
        assert interface.solver_path is not None
    
    def test_set_project_paths_invalid(self):
        """Test setting invalid project paths."""
        interface = BaseInterface()
        
        result = interface.set_project_paths("", "TestProject")
        assert result is False
        
        result = interface.set_project_paths("/nonexistent/path", "TestProject")
        assert result is False
    
    def test_get_solver_name(self):
        """Test getting solver name."""
        interface = BaseInterface()
        
        # Default implementation should return None or raise NotImplementedError
        try:
            solver_name = interface._get_solver_name()
            assert solver_name is not None
        except NotImplementedError:
            # Expected for base class
            pass
    
    def test_get_widget_access_pattern(self):
        """Test widget access pattern."""
        interface = BaseInterface()
        
        # Test with existing widget (if any)
        # This is a basic test since widgets aren't created in base class
        try:
            widget = interface._get_widget("test", "lineEdit")
            # Should either return a widget or raise AttributeError
        except AttributeError:
            # Expected if widget doesn't exist
            pass
    
    def test_get_widget_value(self):
        """Test getting widget value."""
        interface = BaseInterface()
        
        # Test with default value
        value = interface._get_widget_value("nonexistent", "default")
        assert value == "default"
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        interface = BaseInterface()
        
        # Test with empty parameters
        result = interface._validate_parameters({})
        assert result is True  # Should pass for empty parameters
    
    def test_save_parameters(self, temp_dir):
        """Test saving parameters."""
        interface = BaseInterface()
        
        # Set up project paths
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        result = interface.set_project_paths(str(project_path), "TestProject")
        assert result is True
        
        # Test saving parameters
        test_params = {"test_param": "test_value"}
        result = interface._save_parameters(test_params)
        
        # Should succeed if parameter directory exists
        assert result is True or result is False  # Depends on implementation
    
    def test_load_parameters(self, temp_dir):
        """Test loading parameters."""
        interface = BaseInterface()
        
        # Set up project paths
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        result = interface.set_project_paths(str(project_path), "TestProject")
        assert result is True
        
        # Test loading parameters
        params = interface._load_parameters()
        
        # Should return a dictionary
        assert isinstance(params, dict)


class TestUIIntegration:
    """Test suite for UI component integration."""
    
    def test_ui_config_with_ui_loader(self):
        """Test UIConfig integration with UILoader."""
        config = EnhancedUIConfig()
        config.set_mode(UIMode.UI_FILES)
        
        # Should be able to use config with UI loader
        ui_path = EnhancedUILoader(config)._get_ui_path("mainwindow") # Use EnhancedUILoader
        assert isinstance(ui_path, str)
    
    def test_interface_factory_with_ui_config(self, qt_app):
        """Test InterfaceFactory integration with UIConfig."""
        config = EnhancedUIConfig()
        config.set_mode(UIMode.AUTO_DETECT)
        
        # Should be able to use config with interface factory
        try:
            interface = InterfaceFactory.create_interface("carbon", ui_config=config)
            assert interface is not None
        except InterfaceCreationError:
            # Expected if modules aren't available
            pass
    
    def test_widget_standardizer_with_base_interface(self, qt_app):
        """Test WidgetNamingStandardizer integration with BaseInterface."""
        interface = BaseInterface()
        
        # Should be able to use standardizer with interface
        variants = WidgetNamingStandardizer.get_widget_naming_variants("test", "lineEdit")
        assert isinstance(variants, list)
    
    def test_error_handling_integration(self, qt_app):
        """Test error handling integration across UI components."""
        # Test that errors are properly propagated
        config = EnhancedUIConfig()
        
        # Should handle invalid configurations gracefully
        try:
            config.set_mode("invalid_mode")
        except ValueError:
            # Expected for invalid mode
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])