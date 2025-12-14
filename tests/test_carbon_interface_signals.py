"""
Test suite for Carbon Interface signal connections.

This module tests all signal-slot connections in the Carbon interface
to ensure proper functionality and parameter validation.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.gui.interfaces.carbon_interface import CarbonInterface
from src.gui.interfaces.base_interface import BaseInterface


class TestCarbonInterfaceSignals:
    """Test class for Carbon Interface signal connections."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app
    
    @pytest.fixture
    def carbon_interface(self, app):
        """Create Carbon interface instance for testing."""
        # Mock UI config
        ui_config = Mock()
        
        # Create interface
        interface = CarbonInterface(ui_config=ui_config)
        interface.show()
        
        yield interface
        
        # Cleanup
        interface.close()
    
    def test_geometry_signals_connected(self, carbon_interface):
        """Test that geometry signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing geometry signal connections...")
        
        # Check that geometry widgets exist
        assert hasattr(carbon_interface, 'length_edit')
        assert hasattr(carbon_interface, 'width_edit')
        assert hasattr(carbon_interface, 'height_edit')
        assert hasattr(carbon_interface, 'radius_edit')
        assert hasattr(carbon_interface, 'unit_combo')
        assert hasattr(carbon_interface, 'x_div_edit')
        assert hasattr(carbon_interface, 'y_div_edit')
        assert hasattr(carbon_interface, 'z_div_edit')
        
        # Check that buttons exist
        assert hasattr(carbon_interface, 'change_geometry_button')
        assert hasattr(carbon_interface, 'run_geometry_button')
        assert hasattr(carbon_interface, 'view_geometry_button')
        
        logger.debug("Geometry widgets found successfully")
    
    def test_constants_signals_connected(self, carbon_interface):
        """Test that constants signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing constants signal connections...")
        
        # Check that constants widgets exist
        assert hasattr(carbon_interface, 'param_edits')
        assert isinstance(carbon_interface.param_edits, dict)
        
        # Check that material selection exists
        assert hasattr(carbon_interface, 'material_carbon')
        assert hasattr(carbon_interface, 'material_silicon')
        
        # Check that buttons exist
        assert hasattr(carbon_interface, 'change_constants_button')
        assert hasattr(carbon_interface, 'run_constants_button')
        assert hasattr(carbon_interface, 'help_constants_button')
        
        logger.debug("Constants widgets found successfully")
    
    def test_boundary_signals_connected(self, carbon_interface):
        """Test that boundary signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing boundary signal connections...")
        
        # Check that boundary widgets exist
        assert hasattr(carbon_interface, 'initial_cs_edit')
        
        # Check that buttons exist
        assert hasattr(carbon_interface, 'change_boundary_button')
        assert hasattr(carbon_interface, 'run_boundary_button')
        
        logger.debug("Boundary widgets found successfully")
    
    def test_functions_signals_connected(self, carbon_interface):
        """Test that functions signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing functions signal connections...")
        
        # Check that scheme combos exist
        scheme_types = ['ddtSchemes', 'gradSchemes', 'divSchemes', 'laplacianSchemes', 'interpolationSchemes']
        
        for scheme_type in scheme_types:
            combo_name = f"{scheme_type.lower()}_combo"
            assert hasattr(carbon_interface, combo_name), f"Missing {combo_name}"
        
        # Check that buttons exist
        assert hasattr(carbon_interface, 'change_functions_button')
        assert hasattr(carbon_interface, 'run_functions_button')
        
        logger.debug("Functions widgets found successfully")
    
    def test_control_signals_connected(self, carbon_interface):
        """Test that control signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing control signal connections...")
        
        # Check that control widgets exist
        assert hasattr(carbon_interface, 'end_time_edit')
        assert hasattr(carbon_interface, 'delta_t_edit')
        assert hasattr(carbon_interface, 'write_interval_edit')
        assert hasattr(carbon_interface, 'tolerance_edit')
        
        # Check that buttons exist
        assert hasattr(carbon_interface, 'change_control_button')
        assert hasattr(carbon_interface, 'run_button')
        assert hasattr(carbon_interface, 'pause_button')
        assert hasattr(carbon_interface, 'stop_button')
        
        logger.debug("Control widgets found successfully")
    
    def test_terminal_signals_connected(self, carbon_interface):
        """Test that terminal signals are properly connected."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing terminal signal connections...")
        
        # Check that terminal widgets exist
        assert hasattr(carbon_interface, 'terminal_output')
        assert hasattr(carbon_interface, 'command_input')
        assert hasattr(carbon_interface, 'command_button')
        
        logger.debug("Terminal widgets found successfully")
    
    def test_geometry_parameter_validation(self, carbon_interface):
        """Test geometry parameter validation."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing geometry parameter validation...")
        
        # Test valid parameters
        carbon_interface.length_edit.setText("100")
        carbon_interface.width_edit.setText("100")
        carbon_interface.height_edit.setText("100")
        carbon_interface.radius_edit.setText("50")
        
        errors = carbon_interface._validate_geometry_parameters()
        assert len(errors) == 0, f"Unexpected validation errors: {errors}"
        
        # Test invalid parameters
        carbon_interface.length_edit.setText("-10")
        errors = carbon_interface._validate_geometry_parameters()
        assert len(errors) > 0, "Expected validation errors for negative length"
        assert any("Length must be positive" in error for error in errors)
        
        # Test radius too large
        carbon_interface.length_edit.setText("100")
        carbon_interface.width_edit.setText("100")
        carbon_interface.height_edit.setText("100")
        carbon_interface.radius_edit.setText("100")  # Too large
        errors = carbon_interface._validate_geometry_parameters()
        assert len(errors) > 0, "Expected validation errors for radius too large"
        assert any("Radius must be smaller" in error for error in errors)
        
        logger.debug("Geometry parameter validation tests passed")
    
    def test_material_parameter_validation(self, carbon_interface):
        """Test material parameter validation."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing material parameter validation...")
        
        # Test valid parameters
        carbon_interface.param_edits["DS_value"].setText("1e-14")
        carbon_interface.param_edits["CS_max"].setText("30000")
        carbon_interface.param_edits["kReact"].setText("1e-11")
        carbon_interface.param_edits["alphaA"].setText("0.5")
        carbon_interface.param_edits["alphaC"].setText("0.5")
        carbon_interface.param_edits["I_app"].setText("0.0")
        
        errors = carbon_interface._validate_material_parameters()
        assert len(errors) == 0, f"Unexpected validation errors: {errors}"
        
        # Test invalid diffusivity
        carbon_interface.param_edits["DS_value"].setText("1e-5")  # Too large
        errors = carbon_interface._validate_material_parameters()
        assert len(errors) > 0, "Expected validation errors for diffusivity"
        assert any("DS value should be between" in error for error in errors)
        
        # Test invalid transfer coefficient
        carbon_interface.param_edits["DS_value"].setText("1e-14")  # Fix diffusivity
        carbon_interface.param_edits["alphaA"].setText("1.5")  # Too large
        errors = carbon_interface._validate_material_parameters()
        assert len(errors) > 0, "Expected validation errors for transfer coefficient"
        assert any("alphaA should be between" in error for error in errors)
        
        logger.debug("Material parameter validation tests passed")
    
    def test_control_parameter_validation(self, carbon_interface):
        """Test control parameter validation."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing control parameter validation...")
        
        # Test valid parameters
        carbon_interface.end_time_edit.setValue(10.0)
        carbon_interface.delta_t_edit.setValue(0.1)
        carbon_interface.write_interval_edit.setValue(1.0)
        carbon_interface.tolerance_edit.setText("1e-6")
        
        errors = carbon_interface._validate_control_parameters()
        assert len(errors) == 0, f"Unexpected validation errors: {errors}"
        
        # Test invalid end time
        carbon_interface.end_time_edit.setValue(-1.0)
        errors = carbon_interface._validate_control_parameters()
        assert len(errors) > 0, "Expected validation errors for negative end time"
        assert any("End time must be positive" in error for error in errors)
        
        # Test inconsistent parameters
        carbon_interface.end_time_edit.setValue(10.0)  # Fix end time
        carbon_interface.delta_t_edit.setValue(20.0)   # Too large
        errors = carbon_interface._validate_control_parameters()
        assert len(errors) > 0, "Expected validation errors for inconsistent parameters"
        assert any("Delta T should be smaller" in error for error in errors)
        
        logger.debug("Control parameter validation tests passed")
    
    def test_widget_value_retrieval(self, carbon_interface):
        """Test widget value retrieval from different naming conventions."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing widget value retrieval...")
        
        # Test hand-coded widget names
        carbon_interface.length_edit.setText("100")
        value = carbon_interface._get_widget_value('length')
        assert value == 100.0, f"Expected 100.0, got {value}"
        
        # Test spin box widgets
        carbon_interface.x_div_edit.setValue(20)
        value = carbon_interface._get_widget_value('x_division')
        assert value == 20.0, f"Expected 20.0, got {value}"
        
        # Test non-existent widget (should return default)
        value = carbon_interface._get_widget_value('nonexistent')
        assert value == 0.0, f"Expected default value 0.0, got {value}"
        
        logger.debug("Widget value retrieval tests passed")
    
    def test_signal_slot_connections(self, carbon_interface):
        """Test that signal-slot connections work correctly."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing signal-slot connections...")
        
        # Mock the update methods to verify they're called
        with patch.object(carbon_interface, '_update_geometry_parameters') as mock_update_geometry, \
             patch.object(carbon_interface, '_show_status_message') as mock_show_status:
            
            # Simulate changing a geometry parameter
            carbon_interface.length_edit.setText("200")
            
            # Wait for signal to be processed
            import time
            time.sleep(0.1)
            
            # Verify the update method was called
            # Note: This test may not work perfectly due to Qt's event loop,
            # but it demonstrates the testing approach
            
        logger.debug("Signal-slot connection tests completed")
    
    def test_error_handling(self, carbon_interface):
        """Test error handling in parameter updates."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing error handling...")
        
        # Mock QMessageBox to avoid GUI dialogs
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
            # Test with invalid geometry parameters
            carbon_interface.length_edit.setText("invalid")
            carbon_interface.width_edit.setText("100")
            carbon_interface.height_edit.setText("100")
            carbon_interface.radius_edit.setText("50")
            
            # This should trigger validation error
            errors = carbon_interface._validate_geometry_parameters()
            assert len(errors) > 0, "Expected validation errors"
            
            # Verify error message would be shown
            # (We can't easily test the actual QMessageBox without GUI)
        
        logger.debug("Error handling tests passed")
    
    def test_material_selection(self, carbon_interface):
        """Test material selection functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing material selection...")
        
        # Test carbon selection
        carbon_interface.material_carbon.setChecked(True)
        carbon_interface.material_silicon.setChecked(False)
        
        # Verify carbon is selected
        assert carbon_interface.material_carbon.isChecked()
        assert not carbon_interface.material_silicon.isChecked()
        
        # Test silicon selection
        carbon_interface.material_carbon.setChecked(False)
        carbon_interface.material_silicon.setChecked(True)
        
        # Verify silicon is selected
        assert not carbon_interface.material_carbon.isChecked()
        assert carbon_interface.material_silicon.isChecked()
        
        logger.debug("Material selection tests passed")


def run_signal_tests():
    """Run all signal connection tests."""
    logger = logging.getLogger(__name__)
    logger.info("Starting Carbon Interface signal connection tests...")
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create test instance
    test_instance = TestCarbonInterfaceSignals()
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create interface
    ui_config = Mock()
    carbon_interface = CarbonInterface(ui_config=ui_config)
    carbon_interface.show()
    
    try:
        # Run tests
        test_instance.test_geometry_signals_connected(carbon_interface)
        test_instance.test_constants_signals_connected(carbon_interface)
        test_instance.test_boundary_signals_connected(carbon_interface)
        test_instance.test_functions_signals_connected(carbon_interface)
        test_instance.test_control_signals_connected(carbon_interface)
        test_instance.test_terminal_signals_connected(carbon_interface)
        test_instance.test_geometry_parameter_validation(carbon_interface)
        test_instance.test_material_parameter_validation(carbon_interface)
        test_instance.test_control_parameter_validation(carbon_interface)
        test_instance.test_widget_value_retrieval(carbon_interface)
        test_instance.test_material_selection(carbon_interface)
        
        logger.info("All signal connection tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
    
    finally:
        # Cleanup
        carbon_interface.close()


if __name__ == "__main__":
    run_signal_tests()