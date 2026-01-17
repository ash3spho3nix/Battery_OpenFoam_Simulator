"""
Test GUI MSYS2Executor Integration

Tests that the CarbonInterface properly integrates with MSYS2Executor
for OpenFOAM command execution.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from PyQt6.QtWidgets import QApplication
from src.core.project_manager import ProjectManager
from src.gui.interfaces.carbon_interface import CarbonInterface
from src.openfoam.msys2_executor import MSYS2Executor


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestGUIMSYS2Integration:
    """Test CarbonInterface MSYS2Executor integration."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing."""
        temp_dir = tempfile.mkdtemp()
        pm = ProjectManager(temp_dir)
        project_name = 'test_project'
        success = pm.create_project(project_name, 'SPM')

        project_path = Path(temp_dir) / project_name
        case_path = project_path / 'SPMFoam' / 'Case'

        yield str(case_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_carbon_interface(self, qapp, temp_project):
        """Create a mocked CarbonInterface for testing."""
        with patch('src.gui.ui_loader.UILoader.load_ui'):
            interface = CarbonInterface()
            interface.case_path = temp_project
            interface._current_success_callback = None
            interface._current_error_callback = None
            return interface

    def test_msys2_executor_initialization(self, mock_carbon_interface):
        """Test that MSYS2Executor is properly initialized."""
        assert hasattr(mock_carbon_interface, 'msys2_executor')
        assert isinstance(mock_carbon_interface.msys2_executor, MSYS2Executor)

    def test_execute_command_with_callback_integration(self, mock_carbon_interface):
        """Test that _execute_command_with_callback uses MSYS2Executor."""
        # Mock the MSYS2Executor methods
        mock_carbon_interface.msys2_executor.execute_command_with_callback = Mock()

        # Mock the callback methods
        mock_carbon_interface._on_execution_started = Mock()
        mock_carbon_interface._on_msys2_output = Mock()
        mock_carbon_interface._on_msys2_error = Mock()
        mock_carbon_interface._on_msys2_completion = Mock()

        # Test command execution
        test_command = "blockMesh"
        success_callback = Mock()
        error_callback = Mock()

        mock_carbon_interface._execute_command_with_callback(
            test_command, success_callback, error_callback
        )

        # Verify MSYS2Executor was called with correct parameters
        mock_carbon_interface.msys2_executor.execute_command_with_callback.assert_called_once_with(
            test_command,
            mock_carbon_interface.case_path,
            mock_carbon_interface._on_msys2_output,
            mock_carbon_interface._on_msys2_error,
            mock_carbon_interface._on_msys2_completion
        )

        # Verify execution started was called
        mock_carbon_interface._on_execution_started.assert_called_once()

    def test_msys2_output_handling(self, mock_carbon_interface):
        """Test that MSYS2 output is properly forwarded to terminal."""
        mock_carbon_interface._append_terminal = Mock()

        test_output = "blockMesh output line"
        mock_carbon_interface._on_msys2_output(test_output)

        mock_carbon_interface._append_terminal.assert_called_once_with(test_output)

    def test_msys2_error_handling(self, mock_carbon_interface):
        """Test that MSYS2 errors trigger error callbacks."""
        error_callback = Mock()
        mock_carbon_interface._current_error_callback = error_callback

        test_error = "blockMesh failed"
        mock_carbon_interface._on_msys2_error(test_error)

        error_callback.assert_called_once_with(test_error)
        assert mock_carbon_interface._current_error_callback is None

    def test_msys2_completion_success(self, mock_carbon_interface):
        """Test successful MSYS2 command completion."""
        success_callback = Mock()
        mock_carbon_interface._current_success_callback = success_callback
        mock_carbon_interface._update_execution_buttons = Mock()

        mock_carbon_interface._on_msys2_completion(0)  # Success exit code

        mock_carbon_interface._update_execution_buttons.assert_called_once_with(running=False)
        success_callback.assert_called_once()
        assert mock_carbon_interface._current_success_callback is None

    def test_msys2_completion_failure(self, mock_carbon_interface):
        """Test failed MSYS2 command completion."""
        error_callback = Mock()
        mock_carbon_interface._current_error_callback = error_callback
        mock_carbon_interface._update_execution_buttons = Mock()

        mock_carbon_interface._on_msys2_completion(1)  # Failure exit code

        mock_carbon_interface._update_execution_buttons.assert_called_once_with(running=False)
        error_callback.assert_called_once_with("Command failed with exit code 1")
        assert mock_carbon_interface._current_error_callback is None

    def test_workflow_command_format(self, mock_carbon_interface):
        """Test that workflow commands are properly formatted for MSYS2Executor."""
        # The commands should be simple OpenFOAM commands without shell prefixes
        # since MSYS2Executor handles the environment and path conversion

        test_commands = [
            "blockMesh",
            "topoSet -dict system/topoSetDict",
            "splitMeshRegions -cellZones -overwrite",
            "SPMFoam_OF6"
        ]

        for cmd in test_commands:
            with patch.object(mock_carbon_interface.msys2_executor, 'execute_command_with_callback') as mock_exec:
                mock_carbon_interface._execute_command_with_callback(cmd, None, None)
                # Verify the command was passed as-is to MSYS2Executor
                call_args = mock_exec.call_args[0]
                assert call_args[0] == cmd  # First argument should be the command

    def test_simulate_workflow_integration(self, mock_carbon_interface):
        """Test the complete simulate workflow integration with MSYS2Executor."""
        # Mock all the validation and execution methods
        mock_carbon_interface._validate_all_parameters = Mock(return_value=True)
        mock_carbon_interface._execute_command_with_callback = Mock()
        mock_carbon_interface._update_execution_buttons = Mock()

        # Mock the workflow steps
        with patch.object(mock_carbon_interface, '_execute_command_with_callback') as mock_exec:
            # Call the simulate method
            mock_carbon_interface._on_run_simulation()

            # Verify that the workflow commands were called in sequence
            expected_calls = [
                call("cd " + mock_carbon_interface.case_path + " && blockMesh", mock_carbon_interface._on_block_mesh_complete, mock_carbon_interface._on_block_mesh_failed),
                call("cd " + mock_carbon_interface.case_path + " && topoSet -dict system/topoSetDict", mock_carbon_interface._on_topo_set_complete, mock_carbon_interface._on_topo_set_failed),
                call("cd " + mock_carbon_interface.case_path + " && splitMeshRegions -cellZones -overwrite", mock_carbon_interface._on_split_mesh_regions_complete, mock_carbon_interface._on_split_mesh_regions_failed),
                call("cd " + mock_carbon_interface.case_path + " && SPMFoam_OF6", mock_carbon_interface._on_spm_solver_complete, mock_carbon_interface._on_spm_solver_failed)
            ]

            mock_exec.assert_has_calls(expected_calls)

    def test_simulate_workflow_validation_failure(self, mock_carbon_interface):
        """Test that simulate workflow stops if validation fails."""
        # Mock validation to fail
        mock_carbon_interface._validate_all_parameters = Mock(return_value=False)
        mock_carbon_interface._execute_command_with_callback = Mock()

        # Call the simulate method
        mock_carbon_interface._on_run_simulation()

        # Verify that no commands were executed
        mock_carbon_interface._execute_command_with_callback.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])