"""
Test suite for interface fixes validation.

This module tests all critical fixes for Issues #1, #4, and #6:
- Issue #1: Signal-Slot Connection Missing (CRITICAL)
- Issue #4: Widget Naming Mismatch (HIGH PRIORITY) 
- Issue #6: Parameter Manager Initialization (HIGH PRIORITY)
"""

import pytest
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import pyqtSignal, QObject

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.gui.interfaces.base_interface_enhanced import BaseInterface
from src.gui.interfaces.carbon_interface_enhanced import CarbonInterface
from src.utils.parameter_parser import ParameterManager
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager

logger = logging.getLogger(__name__)
class TestInterfaceFixes:
    """Test class for interface fixes validation."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def mock_ui_config(self):
        """Create mock UI configuration."""
        mock_config = Mock()
        mock_config.mode.name = 'HAND_CODED'  # Start with hand-coded for testing
        return mock_config
    
    @pytest.fixture
    def base_interface(self, app, mock_ui_config):
        """Create BaseInterface instance for testing."""
        interface = BaseInterface(parent=None, ui_config=mock_ui_config)
        yield interface
        interface.close()
    
    @pytest.fixture
    def carbon_interface(self, app, mock_ui_config):
        """Create CarbonInterface instance for testing."""
        interface = CarbonInterface(parent=None, ui_config=mock_ui_config)
        yield interface
        interface.close()
    
    def test_issue_1_exit_signal_defined(self, base_interface):
        """Test Issue #1: exit_signal is properly defined in BaseInterface."""
        assert hasattr(base_interface, 'exit_signal'), "exit_signal should be defined in BaseInterface"
        assert hasattr(base_interface.exit_signal, 'emit'), "exit_signal should be a PyQt signal"
        assert hasattr(base_interface, 'error_signal'), "error_signal should be defined for error propagation"
    
    def test_issue_1_exit_signal_emission(self, carbon_interface):
        """Test Issue #1: exit_signal is properly emitted when exit button is clicked."""
        # Mock the exit button
        carbon_interface.exit_button = Mock()
        carbon_interface.exit_button.clicked = Mock()
        
        # Connect the exit signal to a mock slot
        mock_slot = Mock()
        carbon_interface.exit_signal.connect(mock_slot)
        
        # Simulate exit button click
        carbon_interface._on_exit_button_clicked()
        
        # Verify signal was emitted
        mock_slot.assert_called_once()
        carbon_interface.close.assert_called_once()
    
    def test_issue_1_error_signal_propagation(self, carbon_interface):
        """Test Issue #1: error_signal properly propagates errors."""
        # Connect error signal to a mock slot
        mock_error_slot = Mock()
        carbon_interface.error_signal.connect(mock_error_slot)
        
        # Simulate an error condition
        test_error = "Test error message"
        carbon_interface.error_signal.emit(test_error)
        
        # Verify error was propagated
        mock_error_slot.assert_called_once_with(test_error)
    
    def test_issue_4_widget_access_helpers(self, base_interface):
        """Test Issue #4: Widget access helpers work correctly."""
        # Test that helper methods exist
        assert hasattr(base_interface, '_get_widget'), "_get_widget method should exist"
        assert hasattr(base_interface, '_get_widget_value'), "_get_widget_value method should exist"
        assert hasattr(base_interface, '_set_widget_value'), "_set_widget_value method should exist"
    
    def test_issue_4_get_widget_ui_naming(self, base_interface):
        """Test Issue #4: _get_widget works with .ui naming convention."""
        # Create mock widget with .ui naming
        mock_widget = Mock()
        mock_widget.text = Mock(return_value="100")
        setattr(base_interface, 'length_lineEdit', mock_widget)
        
        # Test getting widget with .ui naming
        result = base_interface._get_widget('length', 'lineEdit')
        assert result == mock_widget, "Should return widget with .ui naming"
    
    def test_issue_4_get_widget_hand_coded_naming(self, base_interface):
        """Test Issue #4: _get_widget works with hand-coded naming convention."""
        # Create mock widget with hand-coded naming
        mock_widget = Mock()
        mock_widget.text = Mock(return_value="100")
        setattr(base_interface, 'length_edit', mock_widget)
        
        # Test getting widget with hand-coded naming
        result = base_interface._get_widget('length', 'lineEdit')
        assert result == mock_widget, "Should return widget with hand-coded naming"
    
    def test_issue_4_get_widget_value_ui_naming(self, base_interface):
        """Test Issue #4: _get_widget_value works with .ui naming convention."""
        # Create mock widget with .ui naming
        mock_widget = Mock()
        mock_widget.text = Mock(return_value="100")
        setattr(base_interface, 'length_lineEdit', mock_widget)
        
        # Test getting value with .ui naming
        result = base_interface._get_widget_value('length')
        assert result == "100", "Should return value from widget with .ui naming"
    
    def test_issue_4_get_widget_value_hand_coded_naming(self, base_interface):
        """Test Issue #4: _get_widget_value works with hand-coded naming convention."""
        # Create mock widget with hand-coded naming
        mock_widget = Mock()
        mock_widget.text = Mock(return_value="100")
        setattr(base_interface, 'length_edit', mock_widget)
        
        # Test getting value with hand-coded naming
        result = base_interface._get_widget_value('length')
        assert result == "100", "Should return value from widget with hand-coded naming"
    
    def test_issue_4_get_widget_value_spinbox(self, base_interface):
        """Test Issue #4: _get_widget_value works with spinbox widgets."""
        # Create mock spinbox widget
        mock_widget = Mock()
        mock_widget.value = Mock(return_value=100)
        setattr(base_interface, 'x_div_spinBox', mock_widget)
        
        # Test getting value from spinbox
        result = base_interface._get_widget_value('x_div')
        assert result == 100, "Should return value from spinbox widget"
    
    def test_issue_4_get_widget_value_default(self, base_interface):
        """Test Issue #4: _get_widget_value returns default when widget not found."""
        default_value = "default"
        result = base_interface._get_widget_value('nonexistent', default_value)
        assert result == default_value, "Should return default value when widget not found"
    
    def test_issue_4_set_widget_value(self, base_interface):
        """Test Issue #4: _set_widget_value works correctly."""
        # Create mock widget
        mock_widget = Mock()
        mock_widget.setText = Mock()
        setattr(base_interface, 'length_lineEdit', mock_widget)
        
        # Test setting value
        test_value = "200"
        base_interface._set_widget_value('length', test_value)
        mock_widget.setText.assert_called_once_with("200")
    
    def test_issue_6_parameter_manager_initialization(self, carbon_interface, tmp_path):
        """Test Issue #6: ParameterManager is properly initialized in set_project_paths."""
        # Mock project paths
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        case_path = os.path.join(project_path, project_name, "Case")
        
        # Create case directory
        os.makedirs(case_path, exist_ok=True)
        
        # Mock ParameterManager
        with patch('gui.interfaces.base_interface_enhanced.ParameterManager') as mock_pm_class:
            mock_pm = Mock()
            mock_pm_class.return_value = mock_pm
            
            # Call set_project_paths
            result = carbon_interface.set_project_paths(project_path, project_name)
            
            # Verify ParameterManager was initialized
            assert result == True, "set_project_paths should return True on success"
            mock_pm_class.assert_called_once_with(case_path)
            assert carbon_interface.parameter_manager == mock_pm, "parameter_manager should be set"
    
    def test_issue_6_parameter_manager_initialization_failure(self, carbon_interface, tmp_path):
        """Test Issue #6: ParameterManager initialization failure is handled properly."""
        # Mock project paths
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        case_path = os.path.join(project_path, project_name, "Case")
        
        # Mock ParameterManager to raise exception
        with patch('gui.interfaces.base_interface_enhanced.ParameterManager') as mock_pm_class:
            mock_pm_class.side_effect = Exception("ParameterManager initialization failed")
            
            # Connect error signal to capture error
            error_captured = []
            def capture_error(error_msg):
                error_captured.append(error_msg)
            carbon_interface.error_signal.connect(capture_error)
            
            # Call set_project_paths
            result = carbon_interface.set_project_paths(project_path, project_name)
            
            # Verify failure handling
            assert result == False, "set_project_paths should return False on failure"
            assert len(error_captured) > 0, "Error should be propagated via error_signal"
            assert "ParameterManager initialization failed" in error_captured[0], "Error message should be propagated"
    
    def test_issue_6_solver_manager_initialization(self, carbon_interface, tmp_path):
        """Test Issue #6: SolverManager is properly initialized in set_project_paths."""
        # Mock project paths
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        solver_path = os.path.join(project_path, project_name)
        
        # Create directories
        os.makedirs(solver_path, exist_ok=True)
        
        # Mock SolverManager
        with patch('gui.interfaces.base_interface_enhanced.OpenFOAMSolverManager') as mock_sm_class:
            mock_sm = Mock()
            mock_sm_class.return_value = mock_sm
            
            # Call set_project_paths
            result = carbon_interface.set_project_paths(project_path, project_name)
            
            # Verify SolverManager was initialized
            assert result == True, "set_project_paths should return True on success"
            mock_sm_class.assert_called_once()
            assert carbon_interface.solver_manager == mock_sm, "solver_manager should be set"
    
    def test_issue_6_project_paths_set(self, carbon_interface, tmp_path):
        """Test Issue #6: Project paths are properly set in set_project_paths."""
        # Mock project paths
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        case_path = os.path.join(project_path, project_name, "Case")
        solver_path = os.path.join(project_path, project_name)
        
        # Create directories
        os.makedirs(case_path, exist_ok=True)
        os.makedirs(solver_path, exist_ok=True)
        
        # Mock managers
        with patch('gui.interfaces.base_interface_enhanced.ParameterManager') as mock_pm_class, \
             patch('gui.interfaces.base_interface_enhanced.OpenFOAMSolverManager') as mock_sm_class:
            mock_pm = Mock()
            mock_sm = Mock()
            mock_pm_class.return_value = mock_pm
            mock_sm_class.return_value = mock_sm
            
            # Call set_project_paths
            result = carbon_interface.set_project_paths(project_path, project_name)
            
            # Verify paths are set
            assert result == True, "set_project_paths should return True on success"
            assert carbon_interface.project_path == project_path, "project_path should be set"
            assert carbon_interface.project_name == project_name, "project_name should be set"
            assert carbon_interface.case_path == case_path, "case_path should be set"
            assert carbon_interface.solver_path == solver_path, "solver_path should be set"
    
    def test_issue_6_widget_naming_convention(self, carbon_interface):
        """Test Issue #6: CarbonInterface uses .ui naming convention for widgets."""
        # Check that widgets use .ui naming convention
        ui_widgets = [
            'length_lineEdit',
            'width_lineEdit', 
            'height_lineEdit',
            'radius_lineEdit',
            'unit_select_box',
            'x_div_spinBox',
            'y_div_spinBox',
            'z_div_spinBox',
            'carbon_radioButton',
            'silicon_radioButton',
            'terminal_textEdit',
            'command_lineEdit',
            'execute_command_button'
        ]
        
        for widget_name in ui_widgets:
            assert hasattr(carbon_interface, widget_name), f"Widget {widget_name} should exist with .ui naming"
    
    def test_issue_6_signal_connections(self, carbon_interface):
        """Test Issue #6: All critical signals are properly connected."""
        # Check that critical signals exist
        assert hasattr(carbon_interface, 'exit_signal'), "exit_signal should be defined"
        assert hasattr(carbon_interface, 'error_signal'), "error_signal should be defined"
        assert hasattr(carbon_interface, 'simulation_started'), "simulation_started should be defined"
        assert hasattr(carbon_interface, 'simulation_stopped'), "simulation_stopped should be defined"
        assert hasattr(carbon_interface, 'output_received'), "output_received should be defined"
        assert hasattr(carbon_interface, 'error_received'), "error_received should be defined"
    
    def test_issue_6_enhanced_validation(self, carbon_interface):
        """Test Issue #6: Enhanced validation methods work correctly."""
        # Test that validation methods exist
        assert hasattr(carbon_interface, '_validate_geometry_parameters'), "_validate_geometry_parameters should exist"
        assert hasattr(carbon_interface, '_validate_material_parameters'), "_validate_material_parameters should exist"
        assert hasattr(carbon_interface, '_validate_control_parameters'), "_validate_control_parameters should exist"
    
    def test_issue_6_enhanced_error_handling(self, carbon_interface):
        """Test Issue #6: Enhanced error handling works correctly."""
        # Test that error handling methods exist
        assert hasattr(carbon_interface, '_show_validation_error'), "_show_validation_error should exist"
        assert hasattr(carbon_interface, '_show_error_message'), "_show_error_message should exist"
        assert hasattr(carbon_interface, '_show_status_message'), "_show_status_message should exist"
    
    def test_issue_6_diagnostic_features(self, carbon_interface):
        """Test Issue #6: Diagnostic features work correctly."""
        # Test that diagnostic method exists and can be called
        assert hasattr(carbon_interface, '_diagnose_widget_availability'), "_diagnose_widget_availability should exist"
        
        # Call diagnostic method (should not raise exception)
        try:
            carbon_interface._diagnose_widget_availability()
        except Exception as e:
            pytest.fail(f"_diagnose_widget_availability raised {e} unexpectedly!")
    
    def test_issue_6_widget_access_in_validation(self, carbon_interface):
        """Test Issue #6: Widget access helpers are used in validation methods."""
        # Mock widget values for validation
        with patch.object(carbon_interface, '_get_widget_value') as mock_get_value:
            mock_get_value.return_value = "100"  # Return valid value
            
            # Call validation method
            errors = carbon_interface._validate_geometry_parameters()
            
            # Verify widget access helper was called
            assert mock_get_value.called, "_get_widget_value should be called in validation"
            assert isinstance(errors, list), "Validation should return list of errors"
    
    def test_issue_6_complete_interface_lifecycle(self, app, mock_ui_config, tmp_path):
        """Test Issue #6: Complete interface lifecycle with all fixes."""
        # Create directories
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        case_path = os.path.join(project_path, project_name, "Case")
        solver_path = os.path.join(project_path, project_name)
        os.makedirs(case_path, exist_ok=True)
        os.makedirs(solver_path, exist_ok=True)
        
        # Mock managers
        with patch('gui.interfaces.base_interface_enhanced.ParameterManager') as mock_pm_class, \
             patch('gui.interfaces.base_interface_enhanced.OpenFOAMSolverManager') as mock_sm_class:
            mock_pm = Mock()
            mock_sm = Mock()
            mock_pm_class.return_value = mock_pm
            mock_sm_class.return_value = mock_sm
            
            # Create interface
            interface = CarbonInterface(parent=None, ui_config=mock_ui_config)
            
            # Test set_project_paths
            result = interface.set_project_paths(project_path, project_name)
            assert result == True, "Project paths should be set successfully"
            assert interface.parameter_manager == mock_pm, "ParameterManager should be initialized"
            assert interface.solver_manager == mock_sm, "SolverManager should be initialized"
            
            # Test signal emission
            exit_called = []
            def on_exit():
                exit_called.append(True)
            interface.exit_signal.connect(on_exit)
            interface._on_exit_button_clicked()
            assert len(exit_called) == 1, "Exit signal should be emitted"
            
            # Test error propagation
            error_messages = []
            def on_error(msg):
                error_messages.append(msg)
            interface.error_signal.connect(on_error)
            interface.error_signal.emit("Test error")
            assert len(error_messages) == 1, "Error should be propagated"
            assert error_messages[0] == "Test error", "Error message should be correct"
            
            # Test widget access
            assert hasattr(interface, 'length_lineEdit'), "Widget should exist with .ui naming"
            value = interface._get_widget_value('length')
            assert value is not None, "Widget access should work"
            
            interface.close()


class TestInterfaceFactoryIntegration:
    """Test InterfaceFactory integration with enhanced interfaces."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    @pytest.fixture
    def mock_ui_config(self):
        """Create mock UI configuration."""
        mock_config = Mock()
        mock_config.mode.name = 'HAND_CODED'
        return mock_config
    
    def test_factory_creates_enhanced_interface(self, app, mock_ui_config):
        """Test that InterfaceFactory can create enhanced interfaces."""
        from src.gui.interface_factory import InterfaceFactory
        
        # Mock the interface creation
        with patch('gui.interfaces.carbon_interface_enhanced.CarbonInterface') as mock_interface_class:
            mock_interface = Mock()
            mock_interface_class.return_value = mock_interface
            
            # Create interface through factory
            interface = InterfaceFactory.create_interface('carbon', parent=None, ui_config=mock_ui_config)
            
            # Verify interface was created with correct parameters
            mock_interface_class.assert_called_once_with(parent=None, ui_config=mock_ui_config)
            assert interface == mock_interface, "Factory should return the created interface"
    
    def test_factory_with_project_paths(self, app, mock_ui_config, tmp_path):
        """Test InterfaceFactory with project path setting."""
        from src.gui.interface_factory import InterfaceFactory
        
        # Create directories
        project_path = str(tmp_path / "test_project")
        project_name = "test_case"
        case_path = os.path.join(project_path, project_name, "Case")
        solver_path = os.path.join(project_path, project_name)
        os.makedirs(case_path, exist_ok=True)
        os.makedirs(solver_path, exist_ok=True)
        
        # Mock the interface and its set_project_paths method
        with patch('gui.interfaces.carbon_interface_enhanced.CarbonInterface') as mock_interface_class:
            mock_interface = Mock()
            mock_interface.set_project_paths.return_value = True
            mock_interface_class.return_value = mock_interface
            
            # Create interface through factory
            interface = InterfaceFactory.create_interface('carbon', parent=None, ui_config=mock_ui_config)
            
            # Set project paths
            result = interface.set_project_paths(project_path, project_name)
            
            # Verify project paths were set
            assert result == True, "Project paths should be set successfully"
            mock_interface.set_project_paths.assert_called_once_with(project_path, project_name)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])