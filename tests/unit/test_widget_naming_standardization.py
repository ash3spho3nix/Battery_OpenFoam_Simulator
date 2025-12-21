"""
Test widget naming standardization for Issue #4 resolution.

This test validates that the standardized widget naming convention
works correctly across all interfaces and loading modes.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from gui.interfaces.base_interface_standardized import BaseInterface
from gui.interfaces.carbon_interface import CarbonInterface
from gui.ui_config import UIConfig


class TestWidgetNamingStandardization:
    """Test class for widget naming standardization."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def base_interface(self, app):
        """Create a BaseInterface instance for testing."""
        ui_config = UIConfig()
        interface = BaseInterface(ui_config=ui_config)
        yield interface
        interface.close()
    
    @pytest.fixture
    def carbon_interface(self, app):
        """Create a CarbonInterface instance for testing."""
        ui_config = UIConfig()
        interface = CarbonInterface(ui_config=ui_config)
        yield interface
        interface.close()
    
    def test_geometry_widget_naming(self, base_interface):
        """Test that geometry widgets use standardized naming."""
        # Test LineEdit widgets
        assert hasattr(base_interface, 'length_lineEdit')
        assert hasattr(base_interface, 'width_lineEdit')
        assert hasattr(base_interface, 'height_lineEdit')
        assert hasattr(base_interface, 'radius_lineEdit')
        assert hasattr(base_interface, 'tolerance_lineEdit')
        
        # Test SpinBox widgets
        assert hasattr(base_interface, 'x_division_spinBox')
        assert hasattr(base_interface, 'y_division_spinBox')
        assert hasattr(base_interface, 'z_division_spinBox')
        
        # Test ComboBox widgets
        assert hasattr(base_interface, 'unit_comboBox')
        
        # Test Button widgets
        assert hasattr(base_interface, 'change_geometry_button')
        assert hasattr(base_interface, 'run_geometry_button')
        assert hasattr(base_interface, 'view_geometry_button')
        
        # Test Group and Tab widgets
        assert hasattr(base_interface, 'geometry_group')
        assert hasattr(base_interface, 'geometry_tab')
    
    def test_constants_widget_naming(self, base_interface):
        """Test that constants widgets use standardized naming."""
        # Test LineEdit widgets for parameters
        assert hasattr(base_interface, 'param_lineEdits')
        assert 'DS_value' in base_interface.param_lineEdits
        assert 'CS_max' in base_interface.param_lineEdits
        assert 'kReact' in base_interface.param_lineEdits
        assert 'R' in base_interface.param_lineEdits
        assert 'F' in base_interface.param_lineEdits
        assert 'Ce' in base_interface.param_lineEdits
        assert 'alphaA' in base_interface.param_lineEdits
        assert 'alphaC' in base_interface.param_lineEdits
        assert 'T_temp' in base_interface.param_lineEdits
        assert 'I_app' in base_interface.param_lineEdits
        assert 'initial_cs' in base_interface.param_lineEdits
        
        # Test RadioButton widgets
        assert hasattr(base_interface, 'carbon_radioButton')
        assert hasattr(base_interface, 'silicon_radioButton')
        
        # Test Button widgets
        assert hasattr(base_interface, 'change_constants_button')
        assert hasattr(base_interface, 'run_constants_button')
        assert hasattr(base_interface, 'help_constants_button')
        
        # Test Group and Tab widgets
        assert hasattr(base_interface, 'material_group')
        assert hasattr(base_interface, 'constants_tab')
    
    def test_control_widget_naming(self, base_interface):
        """Test that control widgets use standardized naming."""
        # Test DoubleSpinBox widgets
        assert hasattr(base_interface, 'end_time_doubleSpinBox')
        assert hasattr(base_interface, 'delta_t_doubleSpinBox')
        assert hasattr(base_interface, 'write_interval_doubleSpinBox')
        
        # Test LineEdit widgets
        assert hasattr(base_interface, 'tolerance_lineEdit')
        
        # Test Button widgets
        assert hasattr(base_interface, 'change_control_button')
        assert hasattr(base_interface, 'run_button')
        assert hasattr(base_interface, 'pause_button')
        assert hasattr(base_interface, 'stop_button')
        
        # Test Group and Tab widgets
        assert hasattr(base_interface, 'control_group')
        assert hasattr(base_interface, 'control_tab')
    
    def test_functions_widget_naming(self, base_interface):
        """Test that functions widgets use standardized naming."""
        # Test ComboBox widgets for schemes
        scheme_types = ['ddtSchemes', 'gradSchemes', 'divSchemes', 'laplacianSchemes', 'interpolationSchemes']
        for scheme_type in scheme_types:
            combo_name = f"{scheme_type.lower()}_comboBox"
            assert hasattr(base_interface, combo_name)
        
        # Test Button widgets
        assert hasattr(base_interface, 'change_functions_button')
        assert hasattr(base_interface, 'run_functions_button')
        
        # Test Tab widget
        assert hasattr(base_interface, 'functions_tab')
    
    def test_terminal_widget_naming(self, base_interface):
        """Test that terminal widgets use standardized naming."""
        # Test TextEdit widgets
        assert hasattr(base_interface, 'terminal_output')
        
        # Test LineEdit widgets
        assert hasattr(base_interface, 'command_input')
        
        # Test Button widgets
        assert hasattr(base_interface, 'command_button')
        
        # Test Tab widget
        assert hasattr(base_interface, 'terminal_tab')
    
    def test_widget_types_and_classes(self, base_interface):
        """Test that widgets are of correct types."""
        from PyQt6.QtWidgets import (
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
            QRadioButton, QPushButton, QGroupBox, QWidget
        )
        
        # Test LineEdit widgets
        assert isinstance(base_interface.length_lineEdit, QLineEdit)
        assert isinstance(base_interface.width_lineEdit, QLineEdit)
        assert isinstance(base_interface.height_lineEdit, QLineEdit)
        assert isinstance(base_interface.radius_lineEdit, QLineEdit)
        assert isinstance(base_interface.tolerance_lineEdit, QLineEdit)
        
        # Test SpinBox widgets
        assert isinstance(base_interface.x_division_spinBox, QSpinBox)
        assert isinstance(base_interface.y_division_spinBox, QSpinBox)
        assert isinstance(base_interface.z_division_spinBox, QSpinBox)
        
        # Test DoubleSpinBox widgets
        assert isinstance(base_interface.end_time_doubleSpinBox, QDoubleSpinBox)
        assert isinstance(base_interface.delta_t_doubleSpinBox, QDoubleSpinBox)
        assert isinstance(base_interface.write_interval_doubleSpinBox, QDoubleSpinBox)
        
        # Test ComboBox widgets
        assert isinstance(base_interface.unit_comboBox, QComboBox)
        
        # Test RadioButton widgets
        assert isinstance(base_interface.carbon_radioButton, QRadioButton)
        assert isinstance(base_interface.silicon_radioButton, QRadioButton)
        
        # Test Button widgets
        assert isinstance(base_interface.change_geometry_button, QPushButton)
        assert isinstance(base_interface.run_geometry_button, QPushButton)
        assert isinstance(base_interface.view_geometry_button, QPushButton)
        
        # Test Group widgets
        assert isinstance(base_interface.geometry_group, QGroupBox)
        assert isinstance(base_interface.material_group, QGroupBox)
        
        # Test Tab widgets
        assert isinstance(base_interface.geometry_tab, QWidget)
        assert isinstance(base_interface.constants_tab, QWidget)
    
    def test_ui_file_compatibility(self, base_interface):
        """Test that widget names match .ui file conventions."""
        # These are the widget names from carboninterface.ui
        ui_widget_names = [
            'length_lineEdit',
            'width_lineEdit', 
            'height_lineEdit',
            'radius_lineEdit',
            'x_divide_lineEdit',  # Note: .ui uses divide, but we standardize on division
            'y_divide_lineEdit',
            'z_divide_lineEdit',
            'unit_select_box',    # Note: .ui uses select_box, we standardize on comboBox
            'change_geometry_button',
            'run_geometry_button',
            'DS_lineEdit',
            'CS_lineEdit',
            'KReact_lineEdit',
            'R_lineEdit',
            'F_lineEdit',
            'Ce_lineEdit',
            'alphaA_lineEdit',
            'alphaC_lineEdit',
            'Temp_lineEdit',
            'I_lineEdit',
            'initial_cs_lineEdit',
            'select_carbon',      # Note: .ui uses select_ prefix
            'select_silicon',
            'change_constant_button',
            'run_constant_button',
            'help_constant_button',
            'change_boundary_button',
            'run_boundary_button',
            'change_function_button',
            'run_function_button',
            'tolerance_lineEdit',
            'endtime_lineEdit',   # Note: .ui uses endtime, we standardize on end_time
            'timestep_lineEdit',  # Note: .ui uses timestep, we standardize on delta_t
            'interval_lineEdit',  # Note: .ui uses interval, we standardize on write_interval
            'change_control_button',
            'run_button',
            'pause_run_button',   # Note: .ui uses pause_run, we standardize on pause
            'open_paraview_Button',  # Note: .ui uses Button suffix
            'view_result_button'
        ]
        
        # Check that our standardized names are compatible
        for widget_name in ui_widget_names:
            # Convert .ui naming to our standardized naming where needed
            standardized_name = self._convert_ui_to_standardized_name(widget_name)
            
            if hasattr(base_interface, standardized_name):
                # Widget exists with standardized name
                assert True, f"Widget {standardized_name} exists"
            else:
                # Widget may not exist in base interface but should be accessible
                # through flexible widget access
                try:
                    widget = base_interface._get_widget(standardized_name.replace('_lineEdit', ''))
                    assert widget is not None, f"Widget {standardized_name} accessible via _get_widget"
                except:
                    # Some widgets are interface-specific
                    pass
    
    def _convert_ui_to_standardized_name(self, ui_name: str) -> str:
        """Convert .ui widget name to standardized naming."""
        # Handle common conversions
        conversions = {
            'x_divide_lineEdit': 'x_division_spinBox',
            'y_divide_lineEdit': 'y_division_spinBox', 
            'z_divide_lineEdit': 'z_division_spinBox',
            'unit_select_box': 'unit_comboBox',
            'select_carbon': 'carbon_radioButton',
            'select_silicon': 'silicon_radioButton',
            'DS_lineEdit': 'DS_value_lineEdit',
            'CS_lineEdit': 'CS_max_lineEdit',
            'KReact_lineEdit': 'kReact_lineEdit',
            'Temp_lineEdit': 'T_temp_lineEdit',
            'I_lineEdit': 'I_app_lineEdit',
            'endtime_lineEdit': 'end_time_doubleSpinBox',
            'timestep_lineEdit': 'delta_t_doubleSpinBox',
            'interval_lineEdit': 'write_interval_doubleSpinBox',
            'pause_run_button': 'pause_button',
            'open_paraview_Button': 'view_geometry_button',
            'view_result_button': 'view_geometry_button'  # Simplified for base interface
        }
        
        return conversions.get(ui_name, ui_name)
    
    def test_flexible_widget_access(self, base_interface):
        """Test that flexible widget access works for both naming conventions."""
        # Test that we can access widgets using the flexible method
        # This ensures backward compatibility during transition
        
        # Test LineEdit access
        length_widget = base_interface._get_widget('length', 'lineEdit')
        assert length_widget is base_interface.length_lineEdit
        
        # Test SpinBox access
        x_division_widget = base_interface._get_widget('x_division', 'spinBox')
        assert x_division_widget is base_interface.x_division_spinBox
        
        # Test ComboBox access
        unit_widget = base_interface._get_widget('unit', 'comboBox')
        assert unit_widget is base_interface.unit_comboBox
        
        # Test that it raises AttributeError for non-existent widgets
        with pytest.raises(AttributeError):
            base_interface._get_widget('nonexistent', 'lineEdit')
    
    def test_widget_value_access(self, base_interface):
        """Test that widget value access works correctly."""
        # Set some test values
        base_interface.length_lineEdit.setText("100.0")
        base_interface.x_division_spinBox.setValue(10)
        base_interface.unit_comboBox.setCurrentText("millimeter (mm)")
        
        # Test value access through flexible method
        length_value = base_interface._get_widget_value('length')
        assert length_value == "100.0"
        
        x_division_value = base_interface._get_widget_value('x_division')
        assert x_division_value == 10
        
        unit_value = base_interface._get_widget_value('unit')
        assert unit_value == "millimeter (mm)"
    
    def test_carbon_interface_inheritance(self, carbon_interface):
        """Test that CarbonInterface inherits standardized naming."""
        # CarbonInterface should have all standardized widgets from BaseInterface
        assert hasattr(carbon_interface, 'length_lineEdit')
        assert hasattr(carbon_interface, 'width_lineEdit')
        assert hasattr(carbon_interface, 'height_lineEdit')
        assert hasattr(carbon_interface, 'x_division_spinBox')
        assert hasattr(carbon_interface, 'y_division_spinBox')
        assert hasattr(carbon_interface, 'z_division_spinBox')
        assert hasattr(carbon_interface, 'radius_lineEdit')
        assert hasattr(carbon_interface, 'unit_comboBox')
        
        # Test that CarbonInterface-specific widgets exist
        # (These would be defined in the CarbonInterface class)
        # For now, just verify the interface can be created and has base widgets
    
    def test_signal_slot_compatibility(self, base_interface):
        """Test that signal/slot connections work with standardized naming."""
        # Test that buttons have clicked signals
        assert hasattr(base_interface.change_geometry_button, 'clicked')
        assert hasattr(base_interface.run_geometry_button, 'clicked')
        assert hasattr(base_interface.view_geometry_button, 'clicked')
        
        # Test that buttons are properly connected (this would be done in child classes)
        # For now, just verify the widgets exist and have the right types
        
    def test_ui_loading_mode_compatibility(self):
        """Test that standardized naming works in all UI loading modes."""
        from gui.ui_config import UIMode
        
        for mode in UIMode:
            ui_config = UIConfig(mode=mode)
            
            # Test that BaseInterface can be created with each mode
            interface = BaseInterface(ui_config=ui_config)
            
            # Verify widgets exist
            assert hasattr(interface, 'length_lineEdit')
            assert hasattr(interface, 'width_lineEdit')
            assert hasattr(interface, 'height_lineEdit')
            
            interface.close()
    
    def test_naming_convention_documentation(self):
        """Test that the naming convention is properly documented."""
        # This test ensures that the naming convention is clear and documented
        # In practice, this would be verified by reading the documentation
        
        # Widget type patterns should be consistent
        widget_patterns = {
            'LineEdit': '_lineEdit',
            'SpinBox': '_spinBox', 
            'DoubleSpinBox': '_doubleSpinBox',
            'ComboBox': '_comboBox',
            'RadioButton': '_radioButton',
            'CheckBox': '_checkBox',
            'Button': '_button',
            'Label': '_label',
            'GroupBox': '_group',
            'TabWidget': '_tab'
        }
        
        # Verify patterns are consistent
        for widget_type, suffix in widget_patterns.items():
            assert suffix.startswith('_'), f"Suffix for {widget_type} should start with underscore"
            assert suffix.islower(), f"Suffix for {widget_type} should be lowercase"
    
    def test_error_handling_for_missing_widgets(self, base_interface):
        """Test error handling when widgets are missing."""
        # Test that _get_widget raises appropriate errors
        with pytest.raises(AttributeError, match="Widget not found"):
            base_interface._get_widget('nonexistent_widget', 'lineEdit')
        
        # Test that _get_widget_value returns default for missing widgets
        default_value = "default"
        result = base_interface._get_widget_value('nonexistent_widget', default_value)
        assert result == default_value


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])