"""
Test suite for Carbon Interface OpenFOAM execution workflow.

This module tests the complete OpenFOAM execution workflow including
process control, progress tracking, and error handling.
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

from src.gui.interfaces.carbon_interface_execution import CarbonInterfaceExecution


class TestCarbonInterfaceExecution:
    """Test class for Carbon Interface execution workflow."""
    
    @pytest.fixture
    def app(self):
        """Create Qt application for testing."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app
    
    @pytest.fixture
    def execution_interface(self, app):
        """Create Carbon interface execution instance for testing."""
        # Mock UI config
        ui_config = Mock()
        
        # Create interface
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
    
    def test_execution_ui_setup(self, execution_interface):
        """Test that execution UI elements are properly set up."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing execution UI setup...")
        
        # Check that progress elements exist
        assert hasattr(execution_interface, 'progress_bar')
        assert hasattr(execution_interface, 'progress_label')
        assert hasattr(execution_interface, 'time_estimate_label')
        
        # Check progress bar properties
        assert execution_interface.progress_bar.minimum() == 0
        assert execution_interface.progress_bar.maximum() == 100
        assert execution_interface.progress_bar.value() == 0
        
        # Check initial labels
        assert "Ready to run simulation" in execution_interface.progress_label.text()
        assert "Estimated time: Calculating" in execution_interface.time_estimate_label.text()
        
        logger.debug("Execution UI setup tests passed")
    
    def test_execution_state_initialization(self, execution_interface):
        """Test execution state initialization."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing execution state initialization...")
        
        # Check initial state
        assert execution_interface.execution_state['current_step'] == 0
        assert execution_interface.execution_state['total_steps'] == 5
        assert execution_interface.execution_state['execution_completed'] == False
        assert execution_interface.execution_state['current_process'] is None
        
        # Check step names
        expected_steps = ['blockMesh', 'topoSet', 'splitMeshRegions', 'SPMFoam', 'Complete']
        assert execution_interface.execution_state['step_names'] == expected_steps
        
        logger.debug("Execution state initialization tests passed")
    
    def test_parameter_validation(self, execution_interface):
        """Test parameter validation functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing parameter validation...")
        
        # Set valid parameters
        execution_interface.length_edit.setText("100")
        execution_interface.width_edit.setText("100")
        execution_interface.height_edit.setText("100")
        execution_interface.radius_edit.setText("50")
        
        execution_interface.param_edits["DS_value"].setText("1e-14")
        execution_interface.param_edits["CS_max"].setText("30000")
        execution_interface.param_edits["kReact"].setText("1e-11")
        execution_interface.param_edits["alphaA"].setText("0.5")
        execution_interface.param_edits["alphaC"].setText("0.5")
        execution_interface.param_edits["I_app"].setText("0.0")
        
        execution_interface.end_time_edit.setValue(10.0)
        execution_interface.delta_t_edit.setValue(0.1)
        execution_interface.write_interval_edit.setValue(1.0)
        execution_interface.tolerance_edit.setText("1e-6")
        
        # Test valid parameters
        is_valid = execution_interface._validate_all_parameters()
        assert is_valid == True, "Valid parameters should pass validation"
        
        # Test invalid parameters
        execution_interface.length_edit.setText("-10")
        is_valid = execution_interface._validate_all_parameters()
        assert is_valid == False, "Invalid parameters should fail validation"
        
        logger.debug("Parameter validation tests passed")
    
    def test_progress_update(self, execution_interface):
        """Test progress update functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing progress update...")
        
        # Test initial progress
        execution_interface._update_progress(0, "Test message 0")
        assert execution_interface.execution_state['current_step'] == 0
        assert execution_interface.progress_bar.value() == 0
        assert "Test message 0" in execution_interface.progress_label.text()
        
        # Test intermediate progress
        execution_interface._update_progress(2, "Test message 2")
        assert execution_interface.execution_state['current_step'] == 2
        assert execution_interface.progress_bar.value() == 40  # 2/5 * 100
        assert "Test message 2" in execution_interface.progress_label.text()
        
        # Test final progress
        execution_interface._update_progress(4, "Test message 4")
        assert execution_interface.execution_state['current_step'] == 4
        assert execution_interface.progress_bar.value() == 80  # 4/5 * 100
        assert "Test message 4" in execution_interface.progress_label.text()
        
        logger.debug("Progress update tests passed")
    
    def test_button_state_updates(self, execution_interface):
        """Test button state updates during execution."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing button state updates...")
        
        # Test running state
        execution_interface._update_execution_buttons(running=True)
        
        # Check that run button is disabled
        assert execution_interface.run_button.isEnabled() == False
        
        # Check that control buttons are enabled
        assert execution_interface.pause_button.isEnabled() == True
        assert execution_interface.stop_button.isEnabled() == True
        
        # Check that parameter buttons are disabled
        assert execution_interface.change_geometry_button.isEnabled() == False
        assert execution_interface.change_constants_button.isEnabled() == False
        assert execution_interface.change_boundary_button.isEnabled() == False
        assert execution_interface.change_functions_button.isEnabled() == False
        assert execution_interface.change_control_button.isEnabled() == False
        
        # Test stopped state
        execution_interface._update_execution_buttons(running=False)
        
        # Check that run button is enabled
        assert execution_interface.run_button.isEnabled() == True
        
        # Check that control buttons are disabled
        assert execution_interface.pause_button.isEnabled() == False
        assert execution_interface.stop_button.isEnabled() == False
        
        # Check that parameter buttons are enabled
        assert execution_interface.change_geometry_button.isEnabled() == True
        assert execution_interface.change_constants_button.isEnabled() == True
        assert execution_interface.change_boundary_button.isEnabled() == True
        assert execution_interface.change_functions_button.isEnabled() == True
        assert execution_interface.change_control_button.isEnabled() == True
        
        logger.debug("Button state update tests passed")
    
    def test_execution_workflow_steps(self, execution_interface):
        """Test the complete execution workflow steps."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing execution workflow steps...")
        
        # Mock the command execution
        with patch.object(execution_interface, '_execute_command_with_callback') as mock_execute:
            with patch.object(execution_interface, '_compile_solver') as mock_compile:
                
                # Test blockMesh execution
                execution_interface._execute_block_mesh()
                
                # Verify blockMesh command was called
                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                assert "blockMesh" in args[0]
                
                # Reset mock
                mock_execute.reset_mock()
                
                # Test topoSet execution
                execution_interface._execute_topo_set()
                
                # Verify topoSet command was called
                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                assert "topoSet" in args[0]
                
                # Reset mock
                mock_execute.reset_mock()
                
                # Test splitMeshRegions execution
                execution_interface._execute_split_mesh_regions()
                
                # Verify splitMeshRegions command was called
                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                assert "splitMeshRegions" in args[0]
                
                # Reset mock
                mock_execute.reset_mock()
                
                # Test SPMFoam execution
                execution_interface._execute_spm_solver()
                
                # Verify solver compilation was called
                mock_compile.assert_called_once()
                
                # Verify SPMFoam command was called
                mock_execute.assert_called_once()
                args, kwargs = mock_execute.call_args
                assert "SPMFoam" in args[0]
        
        logger.debug("Execution workflow step tests passed")
    
    def test_error_handling(self, execution_interface):
        """Test error handling during execution."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing error handling...")
        
        # Mock process controller to simulate errors
        with patch.object(execution_interface, '_show_error_message') as mock_show_error:
            with patch.object(execution_interface, '_update_execution_buttons') as mock_update_buttons:
                
                # Test blockMesh failure
                execution_interface._on_block_mesh_failed("blockMesh error")
                
                # Verify error message was shown
                mock_show_error.assert_called_once_with("Geometry generation failed: blockMesh error")
                
                # Verify buttons were updated
                mock_update_buttons.assert_called_once_with(running=False)
                
                # Reset mocks
                mock_show_error.reset_mock()
                mock_update_buttons.reset_mock()
                
                # Test topoSet failure
                execution_interface._on_topo_set_failed("topoSet error")
                
                # Verify error message was shown
                mock_show_error.assert_called_once_with("Region setup failed: topoSet error")
                
                # Verify buttons were updated
                mock_update_buttons.assert_called_once_with(running=False)
        
        logger.debug("Error handling tests passed")
    
    def test_process_control(self, execution_interface):
        """Test process control functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing process control...")
        
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
        
        logger.debug("Process control tests passed")
    
    def test_time_estimation(self, execution_interface):
        """Test time estimation functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing time estimation...")
        
        # Set execution start time
        execution_interface.execution_state['execution_start_time'] = time.time() - 10.0
        
        # Update progress to step 2 (40%)
        execution_interface._update_progress(2, "Test progress")
        
        # Check that time estimate label was updated
        time_label_text = execution_interface.time_estimate_label.text()
        assert "Elapsed time: 10.0s" in time_label_text
        
        # Check that remaining time is estimated
        assert "Estimated remaining:" in time_label_text
        
        logger.debug("Time estimation tests passed")
    
    def test_solver_compilation(self, execution_interface):
        """Test solver compilation functionality."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing solver compilation...")
        
        # Mock subprocess.run
        with patch('subprocess.run') as mock_run:
            # Mock successful compilation
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            # Test compilation
            execution_interface._compile_solver()
            
            # Verify commands were executed
            assert mock_run.call_count == 2  # wclean and wmake
            
            # Check wclean command
            wclean_call = mock_run.call_args_list[0]
            assert "wclean" in str(wclean_call)
            
            # Check wmake command
            wmake_call = mock_run.call_args_list[1]
            assert "wmake" in str(wmake_call)
        
        logger.debug("Solver compilation tests passed")
    
    def test_completion_workflow(self, execution_interface):
        """Test workflow completion."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing workflow completion...")
        
        # Set execution start time
        execution_interface.execution_state['execution_start_time'] = time.time() - 30.0
        
        # Mock QMessageBox
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
            with patch.object(execution_interface, '_update_execution_buttons') as mock_update_buttons:
                
                # Complete execution
                execution_interface._complete_execution()
                
                # Verify completion state
                assert execution_interface.execution_state['execution_completed'] == True
                
                # Verify progress was updated
                assert execution_interface.progress_bar.value() == 100
                
                # Verify success message was shown
                mock_info.assert_called_once()
                args = mock_info.call_args[0]
                assert "Simulation Complete" in args[1]
                assert "30.0 seconds" in args[2]
                
                # Verify buttons were updated
                mock_update_buttons.assert_called_once_with(running=False)
        
        logger.debug("Workflow completion tests passed")
    
    def test_signal_connections(self, execution_interface):
        """Test execution signal connections."""
        logger = logging.getLogger(__name__)
        logger.debug("Testing execution signal connections...")
        
        # Check that process controller signals are connected
        assert execution_interface.process_controller is not None
        
        # Check that execution-specific methods exist
        assert hasattr(execution_interface, '_on_execution_output')
        assert hasattr(execution_interface, '_on_execution_error')
        assert hasattr(execution_interface, '_on_execution_started')
        assert hasattr(execution_interface, '_on_execution_finished')
        
        logger.debug("Signal connection tests passed")


def run_execution_tests():
    """Run all execution workflow tests."""
    logger = logging.getLogger(__name__)
    logger.info("Starting Carbon Interface execution workflow tests...")
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create test instance
    test_instance = TestCarbonInterfaceExecution()
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create interface with temporary directory
    ui_config = Mock()
    execution_interface = CarbonInterfaceExecution(ui_config=ui_config)
    execution_interface.show()
    
    # Mock project paths
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        project_name = "test_project"
        project_path = os.path.join(temp_dir, project_name)
        case_path = os.path.join(project_path, "Case")
        
        # Create directories
        os.makedirs(case_path, exist_ok=True)
        
        # Set paths
        execution_interface.project_path = project_path
        execution_interface.project_name = project_name
        execution_interface.case_path = case_path
        execution_interface.solver_path = project_path
        
        try:
            # Run tests
            test_instance.test_execution_ui_setup(execution_interface)
            test_instance.test_execution_state_initialization(execution_interface)
            test_instance.test_parameter_validation(execution_interface)
            test_instance.test_progress_update(execution_interface)
            test_instance.test_button_state_updates(execution_interface)
            test_instance.test_execution_workflow_steps(execution_interface)
            test_instance.test_error_handling(execution_interface)
            test_instance.test_process_control(execution_interface)
            test_instance.test_time_estimation(execution_interface)
            test_instance.test_solver_compilation(execution_interface)
            test_instance.test_completion_workflow(execution_interface)
            test_instance.test_signal_connections(execution_interface)
            
            logger.info("All execution workflow tests passed successfully!")
            
        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
            raise
        
        finally:
            # Cleanup
            execution_interface.close()


if __name__ == "__main__":
    run_execution_tests()