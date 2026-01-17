"""
Comprehensive tests for the enhanced UI loading system.

This module tests all aspects of the enhanced UI loading system including:
- Multi-mode loading (AUTO_DETECT, UI_FILES, HAND_CODED)
- Fallback mechanisms
- Configuration management
- Widget naming standardization
- Error handling and recovery
- Performance and caching
"""

import os
import sys
import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget, QApplication, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.ui_loader import (
    UILoader, UILoadingError, UIValidationError,
    UIProgressTracker
)
from src.gui.ui_config import (
    EnhancedUIConfig, UILoadingMode, FallbackStrategy,
    ConfigurationError, ConfigurationValidationError
)
from src.gui.widget_naming_standardizer import (
    WidgetNamingStandardizer, WidgetAccessMode,
    create_standardized_interface_mixin
)


class TestUILoader:
    """Test suite for UILoader."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def temp_ui_file(self):
        """Create a temporary valid .ui file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ui', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <widget class="QWidget" name="TestWidget">
  <widget class="QLineEdit" name="test_lineEdit">
   <property name="text">
    <string>Test Value</string>
   </property>
  </widget>
 </widget>
</ui>''')
            temp_path = f.name
        
        yield Path(temp_path)
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    
    @pytest.fixture
    def temp_invalid_ui_file(self):
        """Create a temporary invalid .ui file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ui', delete=False) as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <widget class="QWidget" name="TestWidget">
  <invalid_tag>
   <property name="text">
    <string>Test Value</string>
   </property>
  </invalid_tag>
 </widget>
</ui>''')
            temp_path = f.name
        
        yield Path(temp_path)
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    
    @pytest.fixture
    def loader(self):
        """Create a UILoader instance."""
        config = UIConfig()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        return UILoader(config)
    
    def test_initialization(self):
        """Test UILoader initialization."""
        config = UIConfig()
        loader = UILoader(config)
        
        assert loader.ui_config is not None
        assert loader.progress_tracker is not None
        assert loader.logger is not None
    
    def test_load_ui_files_only_success(self, loader, temp_ui_file):
        """Test successful UI file loading in UI_FILES mode."""
        # Setup config for UI_FILES mode
        loader.ui_config.update_setting('mode', UILoadingMode.UI_FILES)
        
        # Mock the path resolution
        with patch.object(loader, '_get_ui_path') as mock_get_path:
            mock_get_path.return_value = temp_ui_file
            
            widget = loader.load_ui("test")
            
            assert widget is not None
            assert hasattr(widget, 'test_lineEdit')
    
    def test_load_ui_files_only_failure(self, loader):
        """Test UI file loading failure in UI_FILES mode."""
        loader.ui_config.update_setting('mode', UILoadingMode.UI_FILES)
        
        with patch.object(loader, '_get_ui_path') as mock_get_path:
            mock_get_path.return_value = None
            
            with pytest.raises(UILoadingError):
                loader.load_ui("nonexistent")
    
    def test_load_hand_coded_only_success(self, loader):
        """Test successful hand-coded loading in HAND_CODED mode."""
        loader.ui_config.update_setting('mode', UILoadingMode.HAND_CODED)
        
        # This should fail since we don't have actual hand-coded interfaces
        # in the test environment, but we can test the logic
        with patch.object(loader, '_load_hand_coded') as mock_load:
            mock_load.return_value = QWidget()
            
            widget = loader.load_ui("test")
            
            assert widget is not None
            mock_load.assert_called_once()
    
    def test_auto_detect_ui_success(self, loader, temp_ui_file):
        """Test AUTO_DETECT mode with successful .ui file loading."""
        loader.ui_config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        
        with patch.object(loader, '_get_ui_path') as mock_get_path:
            mock_get_path.return_value = temp_ui_file
            
            widget = loader.load_ui("test")
            
            assert widget is not None
            assert hasattr(widget, 'test_lineEdit')
    
    def test_auto_detect_ui_failure_fallback(self, loader):
        """Test AUTO_DETECT mode with .ui failure and hand-coded fallback."""
        loader.ui_config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        
        with patch.object(loader, '_get_ui_path') as mock_get_path:
            mock_get_path.return_value = None  # No .ui file
            
            with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
                mock_hand_coded.return_value = QWidget()
                
                widget = loader.load_ui("test")
                
                assert widget is not None
                mock_hand_coded.assert_called_once()
    
    def test_auto_detect_both_fail(self, loader):
        """Test AUTO_DETECT mode when both .ui and hand-coded fail."""
        loader.ui_config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        
        with patch.object(loader, '_get_ui_path') as mock_get_path:
            mock_get_path.return_value = None
            
            with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
                mock_hand_coded.return_value = None
                
                widget = loader.load_ui("test")
                
                assert widget is None
    
    def test_ui_file_validation(self, loader, temp_ui_file, temp_invalid_ui_file):
        """Test UI file validation."""
        # Valid file should pass
        assert loader._validate_ui_file(temp_ui_file) is True
        
        # Invalid file should fail
        assert loader._validate_ui_file(temp_invalid_ui_file) is False
        
        # Non-existent file should fail
        assert loader._validate_ui_file(Path("nonexistent.ui")) is False
    
    def test_widget_validation(self, loader, app):
        """Test widget integrity validation."""
        # Create a test widget
        widget = QWidget()
        widget.setObjectName("TestWidget")
        
        # Valid widget should pass
        loader._validate_widget_integrity(widget, "test")
        
        # None widget should fail
        with pytest.raises(UIValidationError):
            loader._validate_widget_integrity(None, "test")
    
    def test_fallback_notification(self, loader):
        """Test fallback notification mechanism."""
        with patch('PyQt6.QtWidgets.QMessageBox') as mock_msgbox:
            loader._notify_fallback("test_ui")
            
            # Verify message box was created
            mock_msgbox.assert_called_once()
    
    def test_loading_stats(self, loader):
        """Test loading statistics tracking."""
        initial_stats = loader.get_loading_stats()
        
        # Simulate some loading attempts
        loader._update_stats('ui_success')
        loader._update_stats('hand_coded_success')
        loader._update_stats('fallbacks')
        
        final_stats = loader.get_loading_stats()
        
        assert final_stats['ui_success'] == initial_stats['ui_success'] + 1
        assert final_stats['hand_coded_success'] == initial_stats['hand_coded_success'] + 1
        assert final_stats['fallbacks'] == initial_stats['fallbacks'] + 1
    
    def test_cache_management(self, loader):
        """Test interface caching."""
        widget = QWidget()
        
        # Cache a widget
        loader._cache_interface("test", widget)
        
        # Retrieve from cache
        cached = loader._get_cached_interface("test")
        assert cached is widget
        
        # Clear cache
        loader.clear_cache()
        cached_after_clear = loader._get_cached_interface("test")
        assert cached_after_clear is None
    
    def test_progress_tracking(self, loader):
        """Test progress tracking functionality."""
        progress_events = []
        
        def on_progress(current, total):
            progress_events.append((current, total))
        
        loader.progress_tracker.loading_progress.connect(on_progress)
        
        # Simulate loading
        loader.progress_tracker.start_loading("test")
        loader.progress_tracker.update_progress(1, 5)
        loader.progress_tracker.update_progress(3, 5)
        loader.progress_tracker.complete_loading(True, "Success")
        
        assert len(progress_events) == 2
        assert progress_events[0] == (1, 5)
        assert progress_events[1] == (3, 5)


class TestEnhancedUIConfig:
    """Test suite for EnhancedUIConfig."""
    
    def test_initialization(self):
        """Test EnhancedUIConfig initialization."""
        config = EnhancedUIConfig()
        
        assert config.settings.mode == UILoadingMode.AUTO_DETECT
        assert config.settings.fallback_enabled is True
        assert config.settings.ui_base_path is None
    
    def test_from_environment(self):
        """Test configuration from environment variables."""
        # Set environment variables
        os.environ['BATTERY_SIM_UI_MODE'] = 'ui_files'
        os.environ['BATTERY_SIM_UI_PATH'] = '/custom/path'
        
        try:
            config = EnhancedUIConfig.from_environment()
            
            assert config.settings.mode == UILoadingMode.UI_FILES
            assert config.settings.ui_base_path == '/custom/path'
            assert 'environment' in config.source_priority
            
        finally:
            # Clean up environment
            del os.environ['BATTERY_SIM_UI_MODE']
            del os.environ['BATTERY_SIM_UI_PATH']
    
    def test_from_command_line(self):
        """Test configuration from command line arguments."""
        test_args = [
            '--ui-mode', 'hand_coded',
            '--ui-path', '/cli/path',
            '--no-fallback',
            '--log-level', 'DEBUG'
        ]
        
        config = EnhancedUIConfig.from_command_line(test_args)
        
        assert config.settings.mode == UILoadingMode.HAND_CODED
        assert config.settings.ui_base_path == '/cli/path'
        assert config.settings.fallback_enabled is False
        assert config.settings.log_level == 'DEBUG'
    
    def test_from_file_json(self):
        """Test configuration from JSON file."""
        config_data = {
            'mode': 'auto_detect',
            'fallback_enabled': True,
            'ui_base_path': '/file/path',
            'cache_enabled': False
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = EnhancedUIConfig.from_file(temp_path)
            
            assert config.settings.mode == UILoadingMode.AUTO_DETECT
            assert config.settings.ui_base_path == '/file/path'
            assert config.settings.cache_enabled is False
            
        finally:
            os.unlink(temp_path)
    
    def test_from_file_yaml(self):
        """Test configuration from YAML file."""
        config_data = {
            'mode': 'ui_files',
            'fallback_enabled': False,
            'ui_base_path': '/yaml/path'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = EnhancedUIConfig.from_file(temp_path)
            
            assert config.settings.mode == UILoadingMode.UI_FILES
            assert config.settings.ui_base_path == '/yaml/path'
            assert config.settings.fallback_enabled is False
            
        finally:
            os.unlink(temp_path)
    
    def test_from_multiple_sources(self):
        """Test configuration from multiple sources."""
        # Create a config file
        config_data = {
            'mode': 'auto_detect',
            'ui_base_path': '/file/path'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            # Set environment variable
            os.environ['BATTERY_SIM_UI_MODE'] = 'hand_coded'
            
            # Command line argument
            cli_args = ['--ui-path', '/cli/path']
            
            config = EnhancedUIConfig.from_multiple_sources(
                config_file=temp_path,
                args=cli_args
            )
            
            # CLI should have highest priority, then environment, then file
            assert config.settings.mode == UILoadingMode.HAND_CODED  # From environment
            assert config.settings.ui_base_path == '/cli/path'  # From CLI
            
        finally:
            os.unlink(temp_path)
            if 'BATTERY_SIM_UI_MODE' in os.environ:
                del os.environ['BATTERY_SIM_UI_MODE']
    
    def test_validation(self):
        """Test configuration validation."""
        config = EnhancedUIConfig()
        
        # Valid configuration should pass
        config._validate_configuration()
        
        # Invalid mode should fail
        config.settings.mode = 'invalid_mode'
        with pytest.raises(ConfigurationValidationError):
            config._validate_configuration()
    
    def test_runtime_updates(self):
        """Test runtime configuration updates."""
        config = EnhancedUIConfig()
        
        # Update setting
        config.update_setting('log_level', 'DEBUG')
        assert config.settings.log_level == 'DEBUG'
        
        # Invalid setting should fail
        with pytest.raises(ConfigurationError):
            config.update_setting('invalid_setting', 'value')
    
    def test_to_dict_and_json(self):
        """Test configuration serialization."""
        config = EnhancedUIConfig()
        config.update_setting('mode', UILoadingMode.UI_FILES)
        
        # Test to_dict
        config_dict = config.to_dict()
        assert 'mode' in config_dict
        assert config_dict['mode'] == UILoadingMode.UI_FILES
        
        # Test to_json
        config_json = config.to_json()
        assert 'UI_FILES' in config_json
    
    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = EnhancedUIConfig()
        config.update_setting('mode', UILoadingMode.HAND_CODED)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / 'config.json'
            yaml_path = Path(temp_dir) / 'config.yaml'
            
            # Save as JSON
            config.save_to_file(str(json_path), 'json')
            assert json_path.exists()
            
            # Save as YAML
            config.save_to_file(str(yaml_path), 'yaml')
            assert yaml_path.exists()
    
    def test_get_summary(self):
        """Test configuration summary."""
        config = EnhancedUIConfig()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        
        summary = config.get_summary()
        
        assert 'mode' in summary
        assert 'fallback_enabled' in summary
        assert 'source_priority' in summary
        assert summary['mode'] == 'auto_detect'


class TestWidgetNamingStandardizer:
    """Test suite for WidgetNamingStandardizer."""
    
    @pytest.fixture
    def test_widget(self):
        """Create a test widget with various naming conventions."""
        widget = QWidget()
        widget.setObjectName("TestWidget")
        
        # Add widgets with different naming conventions
        widget.length_lineEdit = QLineEdit()
        widget.width_edit = QLineEdit()
        widget.height_spinBox = QPushButton()
        widget.radius_spin = QPushButton()
        
        return widget
    
    def test_initialization(self, test_widget):
        """Test WidgetNamingStandardizer initialization."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        assert standardizer.widget is test_widget
        assert standardizer.access_mode == WidgetAccessMode.UI_FIRST
    
    def test_get_widget_ui_first(self, test_widget):
        """Test widget access with UI-first mode."""
        standardizer = WidgetNamingStandardizer(
            test_widget, 
            WidgetAccessMode.UI_FIRST
        )
        
        # Should find length_lineEdit first
        widget = standardizer.get_widget('length', 'lineEdit')
        assert widget is test_widget.length_lineEdit
        
        # Should find width_edit as fallback
        widget = standardizer.get_widget('width', 'lineEdit')
        assert widget is test_widget.width_edit
    
    def test_get_widget_code_first(self, test_widget):
        """Test widget access with code-first mode."""
        standardizer = WidgetNamingStandardizer(
            test_widget, 
            WidgetAccessMode.CODE_FIRST
        )
        
        # Should find width_edit first
        widget = standardizer.get_widget('width', 'lineEdit')
        assert widget is test_widget.width_edit
        
        # Should find length_lineEdit as fallback
        widget = standardizer.get_widget('length', 'lineEdit')
        assert widget is test_widget.length_lineEdit
    
    def test_get_widget_value(self, test_widget):
        """Test getting widget values."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        # Set values
        test_widget.length_lineEdit.setText("100")
        test_widget.width_edit.setText("200")
        
        # Get values
        length_value = standardizer.get_widget_value('length', 'lineEdit')
        width_value = standardizer.get_widget_value('width', 'lineEdit')
        
        assert length_value == "100"
        assert width_value == "200"
    
    def test_set_widget_value(self, test_widget):
        """Test setting widget values."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        # Set values
        success1 = standardizer.set_widget_value('length', '300', 'lineEdit')
        success2 = standardizer.set_widget_value('width', '400', 'lineEdit')
        
        assert success1 is True
        assert success2 is True
        assert test_widget.length_lineEdit.text() == "300"
        assert test_widget.width_edit.text() == "400"
    
    def test_generate_naming_variants(self, test_widget):
        """Test naming variant generation."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        variants = standardizer._generate_naming_variants('length', 'lineEdit')
        
        assert 'length_lineEdit' in variants
        assert 'length_edit' in variants
        assert 'length_LineEdit' in variants
    
    def test_discover_widgets(self, test_widget):
        """Test widget discovery."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        discovery = standardizer.discover_widgets()
        
        assert 'QLineEdit' in discovery
        assert 'QPushButton' in discovery
        assert 'length_lineEdit' in discovery['QLineEdit']
        assert 'width_edit' in discovery['QLineEdit']
    
    def test_diagnostics(self, test_widget):
        """Test diagnostic functionality."""
        standardizer = WidgetNamingStandardizer(test_widget, enable_diagnostics=True)
        
        # Access some widgets
        standardizer.get_widget('length', 'lineEdit')
        standardizer.get_widget('nonexistent', 'lineEdit')
        
        diagnostics = standardizer.get_diagnostics()
        
        assert diagnostics is not None
        assert diagnostics['statistics']['total_attempts'] == 2
        assert diagnostics['statistics']['successful_accesses'] == 1
        assert diagnostics['statistics']['failed_accesses'] == 1
    
    def test_validate_naming_convention(self, test_widget):
        """Test naming convention validation."""
        standardizer = WidgetNamingStandardizer(test_widget)
        
        validation = standardizer.validate_naming_convention()
        
        assert 'total_widgets' in validation
        assert 'widget_types' in validation
        assert 'ui_convention_count' in validation
        assert 'code_convention_count' in validation
    
    def test_standardized_interface_mixin(self):
        """Test the standardized interface mixin."""
        StandardizedMixin = create_standardized_interface_mixin()
        
        class TestClass(StandardizedMixin, QWidget):
            def __init__(self):
                super().__init__()
        
        test_instance = TestClass()
        
        # Should have all the standardized methods
        assert hasattr(test_instance, 'get_widget')
        assert hasattr(test_instance, 'get_widget_value')
        assert hasattr(test_instance, 'set_widget_value')
        assert hasattr(test_instance, 'discover_widgets')
        assert hasattr(test_instance, 'get_diagnostics')
        assert hasattr(test_instance, 'validate_naming')


class TestIntegration:
    """Integration tests for the UI loading system."""
    
    def test_complete_ui_loading_workflow(self):
        """Test the complete UI loading workflow."""
        # Create enhanced config
        config = UIConfig()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('fallback_enabled', True)
        
        # Create loader
        loader = UILoader(config)
        
        # Test that all components work together
        assert loader.ui_config is config
        assert loader.progress_tracker is not None
        
        # Test statistics
        stats = loader.get_loading_stats()
        assert 'total_attempts' in stats
        assert 'ui_success' in stats
        assert 'hand_coded_success' in stats
        assert 'fallbacks' in stats
        assert 'failures' in stats
    
    def test_error_handling_chain(self):
        """Test the complete error handling chain."""
        config = UIConfig()
        loader = UILoader(config)
        
        # Test that errors are properly propagated
        with pytest.raises(UILoadingError):
            loader._load_ui_files_only("nonexistent", None)
        
        with pytest.raises(ConfigurationError):
            UIConfig.from_environment()  # Should handle missing env vars gracefully
    
    def test_performance_and_caching(self):
        """Test performance and caching mechanisms."""
        config = UIConfig()
        loader = UILoader(config)
        
        # Test that caches are properly managed
        assert hasattr(loader, '_ui_file_cache')
        assert hasattr(loader, '_widget_count_cache')
        assert hasattr(loader, '_interface_cache')
        
        # Test cache clearing
        loader.clear_cache()
        
        # Caches should be empty after clearing
        assert len(loader._ui_file_cache) == 0
        assert len(loader._widget_count_cache) == 0
        assert len(loader._interface_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])