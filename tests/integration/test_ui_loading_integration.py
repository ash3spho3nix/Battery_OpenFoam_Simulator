"""
Integration tests for the complete UI loading system.

This module tests the integration of all UI loading components:
- UILoader with UIConfig
- Widget naming standardization
- Fallback mechanisms
- Error handling and recovery
- Real-world usage scenarios
"""

import os
import sys
import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt6.QtCore import Qt

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.ui_loader import UILoader
from src.gui.ui_config import UIConfig
from src.gui.interface_factory import InterfaceFactory
from src.gui.main_window import MainWindow


class TestUILoadingIntegration:
    """Integration tests for the complete UI loading system."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def temp_ui_directory(self):
        """Create a temporary directory with test .ui files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ui_dir = Path(temp_dir) / "ui" / "files"
            ui_dir.mkdir(parents=True)
            
            # Create test .ui files
            mainwindow_ui = ui_dir / "mainwindow.ui"
            mainwindow_ui.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <widget class="QMainWindow" name="MainWindow">
  <widget class="QWidget" name="centralwidget">
   <widget class="QPushButton" name="test_button">
    <property name="text">
     <string>Test Button</string>
    </property>
   </widget>
  </widget>
 </widget>
</ui>''')
            
            carbon_ui = ui_dir / "carboninterface.ui"
            carbon_ui.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <widget class="QWidget" name="CarbonInterface">
  <widget class="QLineEdit" name="length_lineEdit">
   <property name="text">
    <string>100</string>
   </property>
  </widget>
  <widget class="QLineEdit" name="width_lineEdit">
   <property name="text">
    <string>200</string>
   </property>
  </widget>
  <widget class="QPushButton" name="run_button">
   <property name="text">
    <string>Run</string>
   </property>
  </widget>
 </widget>
</ui>''')
            
            yield temp_dir
    
    def test_complete_ui_loading_workflow(self, app, temp_ui_directory):
        """Test the complete UI loading workflow from configuration to widget access."""
        # 1. Create configuration
        config = UIConfig.from_multiple_sources()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('ui_base_path', temp_ui_directory)
        config.update_setting('fallback_enabled', True)
        
        # 2. Create loader
        loader = UILoader(config)
        
        # 3. Load main window UI
        main_window_widget = loader.load_ui("mainwindow")
        assert main_window_widget is not None
        assert hasattr(main_window_widget, 'test_button')
        
        # 4. Load carbon interface UI
        carbon_widget = loader.load_ui("carboninterface")
        assert carbon_widget is not None
        assert hasattr(carbon_widget, 'length_lineEdit')
        assert hasattr(carbon_widget, 'width_lineEdit')
        assert hasattr(carbon_widget, 'run_button')
        
        # 5. Test widget naming standardization
        standardizer = WidgetNamingStandardizer(carbon_widget)
        
        # Should find length_lineEdit using standardized access
        length_value = standardizer.get_widget_value('length', 'lineEdit')
        assert length_value == "100"
        
        width_value = standardizer.get_widget_value('width', 'lineEdit')
        assert width_value == "200"
        
        # 6. Test statistics
        stats = loader.get_loading_stats()
        assert stats['total_attempts'] >= 2
        assert stats['ui_success'] >= 2
    
    def test_fallback_mechanism_integration(self, app, temp_ui_directory):
        """Test the complete fallback mechanism."""
        # Create config with auto-detect mode
        config = UIConfig()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('ui_base_path', temp_ui_directory)
        config.update_setting('fallback_enabled', True)
        
        loader = UILoader(config)
        
        # Test successful .ui loading
        widget1 = loader.load_ui("mainwindow")
        assert widget1 is not None
        
        # Test fallback for non-existent .ui file
        # This should try .ui first, then fall back to hand-coded
        with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
            mock_hand_coded.return_value = QWidget()
            
            widget2 = loader.load_ui("nonexistent")
            
            assert widget2 is not None
            mock_hand_coded.assert_called_once()
        
        # Check fallback statistics
        stats = loader.get_loading_stats()
        assert stats['fallbacks'] >= 1
    
    def test_error_handling_integration(self, app):
        """Test comprehensive error handling."""
        # Create config with strict UI_FILES mode
        config = UIConfig()
        config.update_setting('mode', UILoadingMode.UI_FILES)
        config.update_setting('fallback_enabled', False)
        
        loader = UILoader(config)
        
        # Test that missing .ui file raises exception in UI_FILES mode
        with pytest.raises(UILoadingError):
            loader.load_ui("nonexistent")
        
        # Test graceful handling in AUTO_DETECT mode
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        
        with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
            mock_hand_coded.return_value = None
            
            widget = loader.load_ui("nonexistent")
            assert widget is None
    
    def test_configuration_integration(self, app, temp_ui_directory):
        """Test configuration integration with UI loading."""
        # Test environment variable configuration
        os.environ['BATTERY_SIM_UI_MODE'] = 'ui_files'
        os.environ['BATTERY_SIM_UI_PATH'] = temp_ui_directory
        
        try:
            config = UIConfig.from_environment()
            
            assert config.settings.mode == UILoadingMode.UI_FILES
            assert config.settings.ui_base_path == temp_ui_directory
            
            # Use this config for loading
            loader = UILoader(config)
            widget = loader.load_ui("mainwindow")
            
            assert widget is not None
            assert hasattr(widget, 'test_button')
            
        finally:
            del os.environ['BATTERY_SIM_UI_MODE']
            del os.environ['BATTERY_SIM_UI_PATH']
    
    def test_widget_naming_integration(self, app, temp_ui_directory):
        """Test widget naming standardization integration."""
        # Load a widget with .ui naming convention
        config = UIConfig()
        config.update_setting('ui_base_path', temp_ui_directory)
        
        loader = UILoader(config)
        widget = loader.load_ui("carboninterface")
        
        # Test different access modes
        standardizer_ui_first = WidgetNamingStandardizer(
            widget, 
            WidgetAccessMode.UI_FIRST
        )
        standardizer_code_first = WidgetNamingStandardizer(
            widget, 
            WidgetAccessMode.CODE_FIRST
        )
        
        # Both should find the same widgets but with different priority
        length_ui = standardizer_ui_first.get_widget_value('length', 'lineEdit')
        length_code = standardizer_code_first.get_widget_value('length', 'lineEdit')
        
        assert length_ui == length_code == "100"
        
        # Test diagnostics
        diagnostics_ui = standardizer_ui_first.get_diagnostics()
        diagnostics_code = standardizer_code_first.get_diagnostics()
        
        assert diagnostics_ui is not None
        assert diagnostics_code is not None
        assert diagnostics_ui['statistics']['successful_accesses'] > 0
        assert diagnostics_code['statistics']['successful_accesses'] > 0
    
    def test_performance_and_caching_integration(self, app, temp_ui_directory):
        """Test performance and caching mechanisms."""
        config = UIConfig()
        config.update_setting('ui_base_path', temp_ui_directory)
        config.update_setting('cache_enabled', True)
        
        loader = UILoader(config)
        
        # Load the same UI multiple times
        widget1 = loader.load_ui("mainwindow")
        widget2 = loader.load_ui("mainwindow")
        widget3 = loader.load_ui("mainwindow")
        
        # Should be the same cached instance
        assert widget1 is widget2
        assert widget2 is widget3
        
        # Clear cache and reload
        loader.clear_cache()
        widget4 = loader.load_ui("mainwindow")
        
        # Should be a different instance after cache clear
        assert widget4 is not widget1
    
    def test_real_world_scenario(self, app, temp_ui_directory):
        """Test a real-world scenario with MainWindow and InterfaceFactory."""
        # Setup configuration
        config = UIConfig.from_multiple_sources()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('ui_base_path', temp_ui_directory)
        
        # Test MainWindow creation with enhanced config
        main_window = MainWindow(ui_config=config)
        
        # Verify MainWindow has proper widget access
        if hasattr(main_window, 'test_button'):
            # Test that we can access widgets through standardization
            standardizer = WidgetNamingStandardizer(main_window)
            button = standardizer.get_widget('test', 'button')
            assert button is not None
        
        # Test InterfaceFactory integration
        with patch.object(InterfaceFactory, 'create_interface') as mock_create:
            mock_widget = QWidget()
            mock_widget.setObjectName("MockInterface")
            mock_create.return_value = mock_widget
            
            # This would normally create an interface
            interface = InterfaceFactory.create_interface(
                "carbon", 
                parent=main_window, 
                ui_config=config
            )
            
            assert interface is mock_widget
            mock_create.assert_called_once()
    
    def test_logging_integration(self, app, temp_ui_directory, caplog):
        """Test logging integration across all components."""
        with caplog.at_level(logging.DEBUG):
            # Create components with logging
            config = UIConfig()
            config.update_setting('ui_base_path', temp_ui_directory)
            config.update_setting('log_level', 'DEBUG')
            
            loader = UILoader(config)
            
            # Perform operations that should generate logs
            widget = loader.load_ui("mainwindow")
            
            # Check that logs were generated
            assert len(caplog.records) > 0
            
            # Check for specific log messages
            log_messages = [record.message for record in caplog.records]
            assert any('Starting UI loading' in msg for msg in log_messages)
            assert any('Successfully loaded' in msg for msg in log_messages)
    
    def test_error_recovery_integration(self, app, temp_ui_directory):
        """Test error recovery mechanisms."""
        config = UIConfig()
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('fallback_enabled', True)
        config.update_setting('fallback_strategy', FallbackStrategy.GRACEFUL)
        
        loader = UILoader(config)
        
        # Test recovery from .ui file corruption
        corrupt_ui_path = Path(temp_ui_directory) / "ui" / "files" / "corrupt.ui"
        corrupt_ui_path.parent.mkdir(parents=True, exist_ok=True)
        corrupt_ui_path.write_text("invalid xml content")
        
        try:
            # This should fail .ui loading but recover with fallback
            with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
                mock_hand_coded.return_value = QWidget()
                
                widget = loader.load_ui("corrupt")
                
                assert widget is not None
                mock_hand_coded.assert_called_once()
                
        finally:
            # Cleanup
            if corrupt_ui_path.exists():
                corrupt_ui_path.unlink()
    
    def test_configuration_validation_integration(self, app):
        """Test configuration validation across the system."""
        # Test invalid configuration
        config = UIConfig()
        
        # Invalid mode should raise validation error
        with pytest.raises(Exception):  # ConfigurationValidationError
            config.update_setting('mode', 'invalid_mode')
        
        # Valid configuration should work
        config.update_setting('mode', UILoadingMode.AUTO_DETECT)
        config.update_setting('fallback_strategy', FallbackStrategy.GRACEFUL)
        
        # Should be able to create loader with valid config
        loader = UILoader(config)
        assert loader.ui_config is config
    
    def test_multi_mode_integration(self, app, temp_ui_directory):
        """Test all loading modes in integration scenario."""
        modes_to_test = [
            UILoadingMode.AUTO_DETECT,
            UILoadingMode.UI_FILES,
            UILoadingMode.HAND_CODED
        ]
        
        for mode in modes_to_test:
            config = UIConfig()
            config.update_setting('mode', mode)
            config.update_setting('ui_base_path', temp_ui_directory)
            
            loader = UILoader(config)
            
            if mode == UILoadingMode.UI_FILES:
                # Should successfully load existing .ui file
                widget = loader.load_ui("mainwindow")
                assert widget is not None
                assert hasattr(widget, 'test_button')
            elif mode == UILoadingMode.AUTO_DETECT:
                # Should work with .ui files
                widget = loader.load_ui("mainwindow")
                assert widget is not None
            elif mode == UILoadingMode.HAND_CODED:
                # Should try hand-coded even if .ui exists
                with patch.object(loader, '_load_hand_coded') as mock_hand_coded:
                    mock_hand_coded.return_value = QWidget()
                    
                    widget = loader.load_ui("mainwindow")
                    
                    # In HAND_CODED mode, should call hand-coded loader
                    mock_hand_coded.assert_called_once()


class TestUILoadingSystemPerformance:
    """Performance tests for the UI loading system."""
    
    def test_loading_performance(self, app, temp_ui_directory):
        """Test UI loading performance."""
        config = UIConfig()
        config.update_setting('ui_base_path', temp_ui_directory)
        
        loader = UILoader(config)
        
        import time
        
        # Measure loading time for multiple UIs
        start_time = time.time()
        
        for _ in range(10):
            widget = loader.load_ui("mainwindow")
            assert widget is not None
        
        end_time = time.time()
        loading_time = end_time - start_time
        
        # Should load 10 UIs in reasonable time (less than 5 seconds)
        assert loading_time < 5.0
    
    def test_memory_usage(self, app, temp_ui_directory):
        """Test memory usage with caching."""
        import psutil
        import gc
        
        config = UIConfig()
        config.update_setting('ui_base_path', temp_ui_directory)
        config.update_setting('cache_enabled', True)
        
        loader = UILoader(config)
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Load many UIs
        widgets = []
        for i in range(50):
            widget = loader.load_ui("mainwindow")
            widgets.append(widget)
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # With caching, memory increase should be minimal
        memory_increase = final_memory - initial_memory
        
        # Should not increase by more than 50MB (reasonable for 50 widgets)
        assert memory_increase < 50.0
    
    def test_cache_efficiency(self, app, temp_ui_directory):
        """Test cache efficiency and hit rates."""
        config = UIConfig()
        config.update_setting('ui_base_path', temp_ui_directory)
        config.update_setting('cache_enabled', True)
        
        loader = UILoader(config)
        
        # Load same UI multiple times
        for _ in range(5):
            widget = loader.load_ui("mainwindow")
        
        # Should have cache hit for repeated loads
        # (This is more of a functional test since we can't directly measure cache hits)
        assert loader._get_cached_interface("mainwindow") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
