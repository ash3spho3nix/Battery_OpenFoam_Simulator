"""
Integration test suite for complete Carbon Interface implementation.

This module tests the complete Carbon interface implementation including
signal connections, parameter management, OpenFOAM execution, and
end-to-end workflow validation.
"""

import pytest
import sys
import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.gui.interfaces.carbon_interface import CarbonInterface
from src.gui.interfaces.carbon_interface_execution import CarbonInterfaceExecution


class TestCarbonInterfaceIntegration:
    """Integration test class for complete Carbon Interface."""
    
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
        ui_config = Mock()
        interface = CarbonInterface(ui_config=ui_config)
        interface.show()
        
        # Mock project paths
        with tempfile.TemporaryDirectory() as temp_dir:
            project_name = "test_project"
            project_path = os.path.join(temp_dir, project_name)
            case_path = os.path.join(project_path, "Case")
            
            # Create directories
            os.makedirs(case_path, exist_ok=True)
            
            # Set paths
            interface.project_path = project_path
            interface.project_name = project_name
            interface.case_path = case_path
            interface.solver_path = project_path
            
            yield interface
    
    @pytest.fixture
    def execution_interface(self, app):
        """Create Carbon interface execution instance for testing."""
        ui_config = Mock()
        interface = CarbonInterfaceExecution(ui_config=ui_config)
        interface.show()
        
        # Mock project paths
        with tempfile.TemporaryDirectory() as temp_dir:
            project_name = "test_project"
            project_path = os.path.join(temp_dir, project_name)
            case_path = os.path.join(project_path, "Case")
            
            # Create directories
            os.makedirs(case_path, exist_ok=True)
            
            # Set paths
            interface.project_path = project_path
            interface.project_name = project_name
            interface.case_path = case_path
            interface.solver_path = project_path
            
            yield interface
    
    def test_complete_signal_integration(self, carbon_interface):
        """Test complete signal integration across all tabs."""
        logger = logging.getLogger(__name__)
        logger.info("Testing complete signal integration...")
        
        # Verify all signal connections are established
        assert hasattr(carbon_interface, '_connect_all_signals')
        assert hasattr(carbon_interface, '_connect_geometry_signals')
        assert hasattr(carbon_interface, '_connect_constants_signals')
        assert hasattr(carbon_interface, '_connect_boundary_signals')
        assert hasattr(carbon_interface, '_connect_functions_signals')
        assert hasattr(carbon_interface, '_connect_control_signals')
        assert hasattr(carbon_interface, '_connect_terminal_signals')
        
        # Verify widget availability
        widgets_to_check = [
            'length_edit', 'width_edit', 'height_edit', 'radius_edit',
            'unit_combo', 'x_div_edit', 'y_div_edit', 'z_div_edit',
            'param_edits', 'material_carbon', 'material_silicon',
            'initial_cs_edit', 'ddtschemes_combo', 'gradschemes_combo',
            'divschemes_combo', 'laplacianschemes_combo', 'interpolationschemes_combo',
            'end_time_edit', 'delta_t_edit', 'write_interval_edit', 'tolerance_edit',
            'terminal_output', 'command_input'
        ]
        
        for widget_name in widgets_to_check:
            assert hasattr(carbon_interface, widget_name), f"Missing widget: {widget_name}"
        
        logger.info("Complete signal integration test passed")
    
    def test_parameter_management_integration(self, carbon_interface):
        """Test complete parameter management integration."""
        logger = logging.getLogger(__name__)
        logger.info("Testing parameter management integration...")
        
        # Test geometry parameter updates
        carbon_interface.length_edit.setText("200")
        carbon_interface.width_edit.setText("150")
        carbon_interface.height_edit.setText("100")
        carbon_interface.radius_edit.setText("40")
        
        # Test material parameter updates
        carbon_interface.param_edits["DS_value"].setText("1e-13")
        carbon_interface.param_edits["CS_max"].setText("25000")
        carbon_interface.param_edits["kReact"].setText("1e-10")
        
        # Test control parameter updates
        carbon_interface.end_time_edit.setValue(20.0)
        carbon_interface.delta_t_edit.setValue(0.05)
        carbon_interface.write_interval_edit.setValue(0.5)
        carbon_interface.tolerance_edit.setText("1e-7")
        
        # Test boundary parameter updates
        carbon_interface.initial_cs_edit.setText("15000")
        
        # Test scheme parameter updates
        carbon_interface.ddtschemes_combo.setCurrentText("backward")
        carbon_interface.gradschemes_combo.setCurrentText("Gauss cubic")
        
        # Validate all parameters
        geometry_errors = carbon_interface._validate_geometry_parameters()
        material_errors = carbon_interface._validate_material_parameters()
        control_errors = carbon_interface._validate_control_parameters()
        
        assert len(geometry_errors) == 0, f"Geometry validation errors: {geometry_errors}"
        assert len(material_errors) == 0, f"Material validation errors: {material_errors}"
        assert len(control_errors) == 0, f"Control validation errors: {control_errors}"
        
        logger.info("Parameter management integration test passed")
    
    def test_openfoam_file_generation(self, carbon_interface):
        """Test OpenFOAM configuration file generation."""
        logger = logging.getLogger(__name__)
        logger.info("Testing OpenFOAM file generation...")
        
        # Set test parameters
        carbon_interface.length_edit.setText("100")
        carbon_interface.width_edit.setText("100")
        carbon_interface.height_edit.setText("100")
        carbon_interface.radius_edit.setText("50")
        
        carbon_interface.param_edits["DS_value"].setText("1e-14")
        carbon_interface.param_edits["CS_max"].setText("30000")
        carbon_interface.param_edits["kReact"].setText("1e-11")
        
        carbon_interface.end_time_edit.setValue(10.0)
        carbon_interface.delta_t_edit.setValue(0.1)
        carbon_interface.write_interval_edit.setValue(1.0)
        carbon_interface.tolerance_edit.setText("1e-6")
        
        # Test blockMeshDict generation
        try:
            carbon_interface._update_geometry_parameters()
            block_mesh_path = os.path.join(carbon_interface.case_path, "system", "blockMeshDict")
            assert os.path.exists(block_mesh_path), "blockMeshDict not created"
            
            with open(block_mesh_path, 'r') as f:
                content = f.read()
                assert "100" in content, "Length not found in blockMeshDict"
                assert "convertToMeters 1e-6" in content, "Unit conversion not found"
            
            logger.debug("blockMeshDict generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate blockMeshDict: {e}")
            raise
        
        # Test LiProperties generation
        try:
            carbon_interface._update_constants_parameters()
            li_props_path = os.path.join(carbon_interface.case_path, "constant", "LiProperties")
            assert os.path.exists(li_props_path), "LiProperties not created"
            
            with open(li_props_path, 'r') as f:
                content = f.read()
                assert "DS" in content, "DS parameter not found in LiProperties"
                assert "CS_max" in content, "CS_max parameter not found in LiProperties"
            
            logger.debug("LiProperties generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate LiProperties: {e}")
            raise
        
        # Test fvSchemes generation
        try:
            carbon_interface._update_functions_parameters()
            fv_schemes_path = os.path.join(carbon_interface.case_path, "system", "fvSchemes")
            assert os.path.exists(fv_schemes_path), "fvSchemes not created"
            
            with open(fv_schemes_path, 'r') as f:
                content = f.read()
                assert "ddtSchemes" in content, "ddtSchemes not found in fvSchemes"
                assert "gradSchemes" in content, "gradSchemes not found in fvSchemes"
            
            logger.debug("fvSchemes generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate fvSchemes: {e}")
            raise
        
        # Test fvSolution generation
        try:
            fv_solution_path = os.path.join(carbon_interface.case_path, "system", "fvSolution")
            assert os.path.exists(fv_solution_path), "fvSolution not created"
            
            with open(fv_solution_path, 'r') as f:
                content = f.read()
                assert "solvers" in content, "solvers not found in fvSolution"
                assert "cs" in content, "cs solver not found in fvSolution"
            
            logger.debug("fvSolution generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate fvSolution: {e}")
            raise
        
        # Test controlDict generation
        try:
            carbon_interface._update_control_parameters()
            control_dict_path = os.path.join(carbon_interface.case_path, "system", "controlDict")
            assert os.path.exists(control_dict_path), "controlDict not created"
            
            with open(control_dict_path, 'r') as f:
                content = f.read()
                assert "endTime" in content, "endTime not found in controlDict"
                assert "deltaT" in content, "deltaT not found in controlDict"
                assert "SPMFoam_OF6" in content, "Solver name not found in controlDict"
            
            logger.debug("controlDict generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate controlDict: {e}")
            raise
        
        logger.info("OpenFOAM file generation test passed")
    
    def test_execution_workflow_integration(self, execution_interface):
        """Test complete execution workflow integration."""
        logger = logging.getLogger(__name__)
        logger.info("Testing execution workflow integration...")
        
        # Test execution UI setup
        assert hasattr(execution_interface, 'progress_bar')
        assert hasattr(execution_interface, 'progress_label')
        assert hasattr(execution_interface, 'time_estimate_label')
        
        # Test execution state initialization
        assert execution_interface.execution_state['current_step'] == 0
        assert execution_interface.execution_state['total_steps'] == 5
        assert execution_interface.execution_state['execution_completed'] == False
        
        # Test parameter validation integration
        execution_interface.length_edit.setText("100")
        execution_interface.width_edit.setText("100")
        execution_interface.height_edit.setText("100")
        execution_interface.radius_edit.setText("50")
        
        execution_interface.param_edits["DS_value"].setText("1e-14")
        execution_interface.param_edits["CS_max"].setText("30000")
        execution_interface.param_edits["kReact"].setText("1e-11")
        
        execution_interface.end_time_edit.setValue(10.0)
        execution_interface.delta_t_edit.setValue(0.1)
        execution_interface.write_interval_edit.setValue(1.0)
        execution_interface.tolerance_edit.setText("1e-6")
        
        is_valid = execution_interface._validate_all_parameters()
        assert is_valid == True, "Parameters should be valid"
        
        # Test progress update integration
        execution_interface._update_progress(2, "Test progress message")
        assert execution_interface.execution_state['current_step'] == 2
        assert execution_interface.progress_bar.value() == 40  # 2/5 * 100
        
        # Test button state integration
        execution_interface._update_execution_buttons(running=True)
        assert execution_interface.run_button.isEnabled() == False
        assert execution_interface.pause_button.isEnabled() == True
        assert execution_interface.stop_button.isEnabled() == True
        
        execution_interface._update_execution_buttons(running=False)
        assert execution_interface.run_button.isEnabled() == True
        assert execution_interface.pause_button.isEnabled() == False
        assert execution_interface.stop_button.isEnabled() == False
        
        logger.info("Execution workflow integration test passed")
    
    def test_error_handling_integration(self, execution_interface):
        """Test complete error handling integration."""
        logger = logging.getLogger(__name__)
        logger.info("Testing error handling integration...")
        
        # Test validation error handling
        execution_interface.length_edit.setText("-10")  # Invalid
        is_valid = execution_interface._validate_all_parameters()
        assert is_valid == False, "Invalid parameters should fail validation"
        
        # Test file generation error handling
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            try:
                execution_interface._update_geometry_parameters()
                assert False, "Should have raised an exception"
            except Exception as e:
                assert "Failed to update geometry parameters" in str(e)
        
        # Test execution error handling
        with patch.object(execution_interface, '_show_error_message') as mock_show_error:
            execution_interface._on_block_mesh_failed("Test error")
            mock_show_error.assert_called_once_with("Geometry generation failed: Test error")
        
        logger.info("Error handling integration test passed")
    
    def test_process_control_integration(self, execution_interface):
        """Test complete process control integration."""
        logger = logging.getLogger(__name__)
        logger.info("Testing process control integration...")
        
        # Mock process controller
        mock_process_controller = Mock()
        execution_interface.process_controller = mock_process_controller
        
        # Test stop functionality
        with patch.object(execution_interface, '_update_progress') as mock_update_progress:
            with patch.object(execution_interface, '_update_execution_buttons') as mock_update_buttons:
                with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                    
                    execution_interface._on_stop_clicked()
                    
                    # Verify process was terminated
                    mock_process_controller.terminate_process.assert_called_once()
                    
                    # Verify progress was updated
                    mock_update_progress.assert_called_once()
                    
                    # Verify buttons were updated
                    mock_update_buttons.assert_called_once_with(running=False)
                    
                    # Verify message was shown
                    mock_info.assert_called_once()
        
        # Test pause/resume functionality
        with patch.object(execution_interface, '_pause_simulation') as mock_pause:
            with patch.object(execution_interface, '_resume_simulation') as mock_resume:
                
                # Test pause
                execution_interface.simulation_paused = False
                execution_interface._on_pause_clicked()
                mock_pause.assert_called_once()
                
                # Test resume
                execution_interface.simulation_paused = True
                execution_interface._on_pause_clicked()
                mock_resume.assert_called_once()
        
        logger.info("Process control integration test passed")
    
    def test_time_tracking_integration(self, execution_interface):
        """Test complete time tracking integration."""
        logger = logging.getLogger(__name__)
        logger.info("Testing time tracking integration...")
        
        # Set execution start time
        execution_interface.execution_state['execution_start_time'] = time.time() - 15.0
        
        # Test progress updates with time tracking
        execution_interface._update_progress(1, "Step 1")
        time.sleep(0.1)  # Small delay to ensure time difference
        execution_interface._update_progress(2, "Step 2")
        execution_interface._update_progress(3, "Step 3")
        execution_interface._update_progress(4, "Step 4")
        
        # Check that time estimates are being calculated
        time_label_text = execution_interface.time_estimate_label.text()
        assert "Elapsed time:" in time_label_text
        assert "Estimated remaining:" in time_label_text
        
        # Check that progress bar is updating
        assert execution_interface.progress_bar.value() == 80  # 4/5 * 100
        
        logger.info("Time tracking integration test passed")
    
    def test_complete_workflow_simulation(self, execution_interface):
        """Test complete workflow simulation with mocked execution."""
        logger = logging.getLogger(__name__)
        logger.info("Testing complete workflow simulation...")
        
        # Set valid parameters
        execution_interface.length_edit.setText("100")
        execution_interface.width_edit.setText("100")
        execution_interface.height_edit.setText("100")
        execution_interface.radius_edit.setText("50")
        
        execution_interface.param_edits["DS_value"].setText("1e-14")
        execution_interface.param_edits["CS_max"].setText("30000")
        execution_interface.param_edits["kReact"].setText("1e-11")
        
        execution_interface.end_time_edit.setValue(10.0)
        execution_interface.delta_t_edit.setValue(0.1)
        execution_interface.write_interval_edit.setValue(1.0)
        execution_interface.tolerance_edit.setText("1e-6")
        
        # Mock the complete execution workflow
        with patch.object(execution_interface, '_execute_command_with_callback') as mock_execute:
            with patch.object(execution_interface, '_compile_solver') as mock_compile:
                with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
                    with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
                        
                        # Mock user confirmation
                        mock_question.return_value = 16384  # QMessageBox.Yes
                        
                        # Mock successful execution of each step
                        def mock_success_callback():
                            pass
                        
                        def mock_error_callback(error):
                            pass
                        
                        # Set up mock to call success callbacks
                        mock_execute.side_effect = [
                            None,  # blockMesh
                            None,  # topoSet
                            None,  # splitMeshRegions
                            None   # SPMFoam
                        ]
                        
                        # Start execution
                        execution_interface._on_run_clicked()
                        
                        # Verify execution was initiated
                        assert execution_interface.execution_state['execution_start_time'] is not None
                        assert execution_interface.execution_state['current_step'] == 0
                        
                        # Verify buttons were updated
                        assert execution_interface.run_button.isEnabled() == False
                        assert execution_interface.pause_button.isEnabled() == True
                        assert execution_interface.stop_button.isEnabled() == True
        
        logger.info("Complete workflow simulation test passed")
    
    def test_signal_slot_cleanup(self, carbon_interface):
        """Test proper signal-slot cleanup."""
        logger = logging.getLogger(__name__)
        logger.info("Testing signal-slot cleanup...")
        
        # Verify that signals are properly connected
        widget_signals = [
            'textChanged', 'valueChanged', 'currentTextChanged', 'toggled'
        ]
        
        for attr_name in dir(carbon_interface):
            attr = getattr(carbon_interface, attr_name, None)
            if hasattr(attr, 'connect'):
                # Widget has signals, check if they're connected
                logger.debug(f"Widget {attr_name} has signals")
        
        # Test that interface can be closed without issues
        carbon_interface.close()
        
        logger.info("Signal-slot cleanup test passed")


def run_integration_tests():
    """Run all integration tests."""
    logger = logging.getLogger(__name__)
    logger.info("Starting Carbon Interface integration tests...")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create test instance
    test_instance = TestCarbonInterfaceIntegration()
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    try:
        # Run integration tests
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock interface for signal integration test
            ui_config = Mock()
            carbon_interface = CarbonInterface(ui_config=ui_config)
            carbon_interface.show()
            
            # Mock project paths
            project_name = "test_project"
            project_path = os.path.join(temp_dir, project_name)
            case_path = os.path.join(project_path, "Case")
            os.makedirs(case_path, exist_ok=True)
            
            carbon_interface.project_path = project_path
            carbon_interface.project_name = project_name
            carbon_interface.case_path = case_path
            carbon_interface.solver_path = project_path
            
            # Run signal integration test
            test_instance.test_complete_signal_integration(carbon_interface)
            
            # Run parameter management test
            test_instance.test_parameter_management_integration(carbon_interface)
            
            # Run OpenFOAM file generation test
            test_instance.test_openfoam_file_generation(carbon_interface)
            
            # Create execution interface for execution tests
            execution_interface = CarbonInterfaceExecution(ui_config=ui_config)
            execution_interface.show()
            
            execution_interface.project_path = project_path
            execution_interface.project_name = project_name
            execution_interface.case_path = case_path
            execution_interface.solver_path = project_path
            
            # Run execution workflow test
            test_instance.test_execution_workflow_integration(execution_interface)
            
            # Run error handling test
            test_instance.test_error_handling_integration(execution_interface)
            
            # Run process control test
            test_instance.test_process_control_integration(execution_interface)
            
            # Run time tracking test
            test_instance.test_time_tracking_integration(execution_interface)
            
            # Run complete workflow simulation test
            test_instance.test_complete_workflow_simulation(execution_interface)
            
            # Run signal-slot cleanup test
            test_instance.test_signal_slot_cleanup(carbon_interface)
            
            # Cleanup
            carbon_interface.close()
            execution_interface.close()
        
        logger.info("All integration tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_integration_tests()