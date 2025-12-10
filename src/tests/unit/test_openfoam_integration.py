"""
Unit tests for OpenFOAM integration components.

This module tests the OpenFOAM integration including:
- ProcessController (subprocess management)
- OpenFOAMSolverManager (solver execution and management)
- Integration with GUI components
"""

import pytest
import os
import tempfile
import shutil
import subprocess
import threading
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

from PyQt6.QtCore import QObject, pyqtSignal

from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.core.constants import PROCESS_TIMEOUT


class TestProcessController:
    """Test suite for ProcessController class."""
    
    def test_process_controller_initialization(self):
        """Test ProcessController initialization."""
        controller = ProcessController()
        
        assert controller.process is None
        assert controller.stdout_thread is None
        assert controller.stderr_thread is None
        assert controller._running is False
    
    def test_start_process_success(self):
        """Test successful process start."""
        controller = ProcessController()
        
        # Mock subprocess.Popen
        mock_process = Mock()
        mock_process.stdout = iter(['stdout line 1\n', 'stdout line 2\n'])
        mock_process.stderr = iter(['stderr line 1\n'])
        mock_process.wait.return_value = 0
        
        with patch('subprocess.Popen', return_value=mock_process):
            controller.start_process('echo test')
            
            assert controller._running is True
            assert controller.process == mock_process
    
    def test_start_process_failure(self):
        """Test process start failure."""
        controller = ProcessController()
        
        with patch('subprocess.Popen', side_effect=Exception("Test error")):
            controller.start_process('invalid command')
            
            # Error should be emitted via signal
            # Note: In a real test, you'd connect to the signal and verify it was emitted
    
    def test_terminate_process(self):
        """Test process termination."""
        controller = ProcessController()
        
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.wait.return_value = 0
        
        controller.process = mock_process
        controller._running = True
        
        controller.terminate_process()
        
        assert controller._running is False
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    def test_terminate_process_timeout(self):
        """Test process termination with timeout."""
        controller = ProcessController()
        
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.wait.side_effect = subprocess.TimeoutExpired('test', 1)
        mock_process.returncode = 1
        
        controller.process = mock_process
        controller._running = True
        
        controller.terminate_process()
        
        # Should call kill() after timeout
        mock_process.kill.assert_called_once()
    
    def test_is_running(self):
        """Test is_running method."""
        controller = ProcessController()
        
        assert controller.is_running() is False
        
        controller._running = True
        assert controller.is_running() is True
    
    def test_get_exit_code(self):
        """Test get_exit_code method."""
        controller = ProcessController()
        
        # No process
        assert controller.get_exit_code() is None
        
        # Process with exit code
        mock_process = Mock()
        mock_process.returncode = 0
        controller.process = mock_process
        
        assert controller.get_exit_code() == 0
    
    def test_send_signal(self):
        """Test send_signal method."""
        controller = ProcessController()
        
        mock_process = Mock()
        controller.process = mock_process
        controller._running = True
        
        controller.send_signal(9)  # SIGKILL
        
        mock_process.send_signal.assert_called_once_with(9)
    
    def test_send_signal_not_running(self):
        """Test send_signal when process is not running."""
        controller = ProcessController()
        
        mock_process = Mock()
        controller.process = mock_process
        controller._running = False
        
        controller.send_signal(9)
        
        # Should not call send_signal on process
        mock_process.send_signal.assert_not_called()
    
    def test_write_to_stdin(self):
        """Test write_to_stdin method."""
        controller = ProcessController()
        
        mock_process = Mock()
        mock_process.stdin = Mock()
        controller.process = mock_process
        controller._running = True
        
        controller.write_to_stdin('test input')
        
        mock_process.stdin.write.assert_called_once_with('test input\n')
        mock_process.stdin.flush.assert_called_once()
    
    def test_write_to_stdin_not_running(self):
        """Test write_to_stdin when process is not running."""
        controller = ProcessController()
        
        mock_process = Mock()
        mock_process.stdin = Mock()
        controller.process = mock_process
        controller._running = False
        
        controller.write_to_stdin('test input')
        
        # Should not write to stdin
        mock_process.stdin.write.assert_not_called()
    
    def test_cleanup(self):
        """Test cleanup method."""
        controller = ProcessController()
        
        mock_process = Mock()
        controller.process = mock_process
        controller._running = True
        
        controller.cleanup()
        
        assert controller.process is None
        assert controller._running is False
        mock_process.terminate.assert_called_once()
    
    def test_output_stream_reading(self):
        """Test output stream reading in separate threads."""
        controller = ProcessController()
        
        # Create mock streams
        stdout_lines = ['line 1\n', 'line 2\n', 'line 3\n']
        stderr_lines = ['error 1\n', 'error 2\n']
        
        mock_process = Mock()
        mock_process.stdout = iter(stdout_lines)
        mock_process.stderr = iter(stderr_lines)
        mock_process.wait.return_value = 0
        
        # Mock the signal emissions
        controller.output_received = Mock()
        controller.error_received = Mock()
        controller.process_started = Mock()
        controller.process_finished = Mock()
        
        with patch('subprocess.Popen', return_value=mock_process):
            controller.start_process('echo test')
            
            # Wait for threads to complete
            if controller.stdout_thread:
                controller.stdout_thread.join(timeout=1)
            if controller.stderr_thread:
                controller.stderr_thread.join(timeout=1)
            if controller.monitor_thread:
                controller.monitor_thread.join(timeout=1)
            
            # Verify output was received
            assert controller.output_received.emit.call_count == len(stdout_lines)
            assert controller.error_received.emit.call_count == len(stderr_lines)
            controller.process_finished.emit.assert_called_once_with(0)
    
    def test_process_monitoring(self):
        """Test process completion monitoring."""
        controller = ProcessController()
        
        mock_process = Mock()
        mock_process.wait.return_value = 42  # Exit code
        
        controller.process = mock_process
        controller._running = True
        
        # Mock signals
        controller.process_finished = Mock()
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=controller._monitor_process)
        monitor_thread.start()
        monitor_thread.join(timeout=1)
        
        assert controller._running is False
        controller.process_finished.emit.assert_called_once_with(42)


class TestOpenFOAMSolverManager:
    """Test suite for OpenFOAMSolverManager class."""
    
    def test_solver_manager_initialization(self, temp_dir):
        """Test OpenFOAMSolverManager initialization."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        assert manager.solver_path == str(solver_path)
        assert manager.solver_name == "SPMFoam_OF6"
        assert manager.process_controller is not None
    
    def test_build_solver_success(self, temp_dir):
        """Test successful solver building."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Create Make directory and files
        make_dir = solver_path / "Make"
        make_dir.mkdir()
        make_files = make_dir / "files"
        make_files.write_text("SPMFoam\n")
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = manager.build_solver()
            
            assert result is True
            mock_run.assert_called()
    
    def test_build_solver_no_make_files(self, temp_dir):
        """Test solver building when no Make/files exist."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        result = manager.build_solver()
        
        assert result is False
    
    def test_build_solver_failure(self, temp_dir):
        """Test solver building failure."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Create Make directory and files
        make_dir = solver_path / "Make"
        make_dir.mkdir()
        make_files = make_dir / "files"
        make_files.write_text("SPMFoam\n")
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            
            result = manager.build_solver()
            
            assert result is False
    
    def test_run_simulation_success(self, temp_dir):
        """Test successful simulation execution."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch.object(manager.process_controller, 'start_process') as mock_start:
            manager.run_simulation(str(case_path))
            
            # Verify process was started
            mock_start.assert_called_once()
            args = mock_start.call_args[0]
            assert str(case_path) in args[0]  # Command should contain case path
    
    def test_run_simulation_no_solver(self, temp_dir):
        """Test simulation execution when solver doesn't exist."""
        solver_path = Path(temp_dir) / "SPMFoam"
        # Don't create the directory
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with pytest.raises(FileNotFoundError):
            manager.run_simulation(str(case_path))
    
    def test_is_running(self, temp_dir):
        """Test is_running method."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Initially not running
        assert manager.is_running() is False
        
        # Mock process controller to be running
        manager.process_controller._running = True
        assert manager.is_running() is True
    
    def test_terminate_simulation(self, temp_dir):
        """Test simulation termination."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch.object(manager.process_controller, 'terminate_process') as mock_terminate:
            manager.terminate_simulation()
            
            mock_terminate.assert_called_once()
    
    def test_get_solver_path(self, temp_dir):
        """Test get_solver_path method."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        assert manager.get_solver_path() == str(solver_path)
    
    def test_get_solver_name(self, temp_dir):
        """Test get_solver_name method."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        assert manager.get_solver_name() == "SPMFoam_OF6"
    
    def test_signal_connections(self, temp_dir):
        """Test signal connections to process controller."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock signals
        manager.output_received = Mock()
        manager.error_received = Mock()
        manager.process_started = Mock()
        manager.process_finished = Mock()
        
        # Connect signals (this happens in initialization)
        manager.process_controller.output_received.connect(manager.output_received)
        manager.process_controller.error_received.connect(manager.error_received)
        manager.process_controller.process_started.connect(manager.process_started)
        manager.process_controller.process_finished.connect(manager.process_finished)
        
        # Emit signals from process controller
        manager.process_controller.output_received.emit("test output")
        manager.process_controller.error_received.emit("test error")
        manager.process_controller.process_started.emit()
        manager.process_controller.process_finished.emit(0)
        
        # Verify signals were received
        manager.output_received.emit.assert_called_once_with("test output")
        manager.error_received.emit.assert_called_once_with("test error")
        manager.process_started.emit.assert_called_once()
        manager.process_finished.emit.assert_called_once_with(0)
    
    def test_build_solver_with_clean(self, temp_dir):
        """Test solver building with clean step."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Create Make directory and files
        make_dir = solver_path / "Make"
        make_dir.mkdir()
        make_files = make_dir / "files"
        make_files.write_text("SPMFoam\n")
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = manager.build_solver(clean_first=True)
            
            assert result is True
            # Should call wclean then wmake
            assert mock_run.call_count == 2
    
    def test_run_simulation_with_custom_command(self, temp_dir):
        """Test simulation execution with custom command."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        custom_command = "mpirun -np 4 SPMFoam_OF6 -parallel"
        
        with patch.object(manager.process_controller, 'start_process') as mock_start:
            manager.run_simulation(str(case_path), command=custom_command)
            
            mock_start.assert_called_once_with(custom_command, str(case_path))
    
    def test_run_simulation_invalid_case_path(self, temp_dir):
        """Test simulation execution with invalid case path."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        invalid_case_path = "/invalid/case/path"
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Should not raise exception, but process controller will handle the error
        with patch.object(manager.process_controller, 'start_process') as mock_start:
            mock_start.side_effect = Exception("Invalid path")
            
            # The error should be handled by the process controller
            manager.run_simulation(invalid_case_path)
            
            mock_start.assert_called_once()


class TestIntegration:
    """Integration tests for OpenFOAM components."""
    
    def test_process_controller_with_solver_manager(self, temp_dir):
        """Test integration between ProcessController and OpenFOAMSolverManager."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock the process controller
        mock_controller = Mock()
        mock_controller.start_process = Mock()
        mock_controller.terminate_process = Mock()
        mock_controller._running = False
        
        manager.process_controller = mock_controller
        
        # Test simulation run
        manager.run_simulation(str(case_path))
        
        mock_controller.start_process.assert_called_once()
        
        # Test termination
        manager.terminate_simulation()
        
        mock_controller.terminate_process.assert_called_once()
    
    def test_solver_building_workflow(self, temp_dir):
        """Test complete solver building workflow."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Create complete Make structure
        make_dir = solver_path / "Make"
        make_dir.mkdir()
        
        # Create files file
        files_file = make_dir / "files"
        files_file.write_text("""SPMFoam.C

EXE = \$(FOAM_APPBIN)/SPMFoam_OF6
""")
        
        # Create options file
        options_file = make_dir / "options"
        options_file.write_text("""EXE_INC = \\
    -I\$(LIB_SRC)/finiteVolume/lnInclude \\
    -I\$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \\
    -lfiniteVolume \\
    -lmeshTools
""")
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Build solver
            result = manager.build_solver()
            
            assert result is True
            
            # Verify build commands were called
            assert mock_run.call_count >= 1
    
    def test_simulation_execution_workflow(self, temp_dir):
        """Test complete simulation execution workflow."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        # Create case structure
        system_dir = case_path / "system"
        system_dir.mkdir()
        constant_dir = case_path / "constant"
        constant_dir.mkdir()
        
        # Create basic OpenFOAM files
        control_dict = system_dir / "controlDict"
        control_dict.write_text("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.1;

writeControl    timeStep;

writeInterval   10;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
""")
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock successful solver building
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                # Run simulation
                manager.run_simulation(str(case_path))
                
                # Verify process was started
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                command = args[0]
                
                # Command should contain solver name and case path
                assert "SPMFoam_OF6" in command
                assert str(case_path) in command
    
    def test_error_handling_integration(self, temp_dir):
        """Test error handling in the integration."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Test build failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            
            result = manager.build_solver()
            assert result is False
        
        # Test simulation failure
        with patch.object(manager.process_controller, 'start_process') as mock_start:
            mock_start.side_effect = Exception("Simulation failed")
            
            # Should handle the exception gracefully
            try:
                manager.run_simulation(str(case_path))
            except Exception:
                pytest.fail("Simulation should handle exceptions gracefully")
    
    def test_parallel_execution(self, temp_dir):
        """Test parallel execution setup."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch.object(manager.process_controller, 'start_process') as mock_start:
            # Test parallel execution
            manager.run_simulation(str(case_path), parallel=True, num_processors=4)
            
            mock_start.assert_called_once()
            args = mock_start.call_args[0]
            command = args[0]
            
            # Command should contain mpirun and -parallel flag
            assert "mpirun" in command
            assert "-parallel" in command
            assert "-np 4" in command
    
    def test_output_streaming_integration(self, temp_dir):
        """Test output streaming during simulation."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock signals
        manager.output_received = Mock()
        manager.error_received = Mock()
        manager.process_started = Mock()
        manager.process_finished = Mock()
        
        # Connect to process controller signals
        manager.process_controller.output_received.connect(manager.output_received)
        manager.process_controller.error_received.connect(manager.error_received)
        manager.process_controller.process_started.connect(manager.process_started)
        manager.process_controller.process_finished.connect(manager.process_finished)
        
        # Mock process with output
        mock_process = Mock()
        mock_process.stdout = iter(['Time = 0\n', 'Time = 1\n', 'Time = 2\n'])
        mock_process.stderr = iter(['Warning: test warning\n'])
        mock_process.wait.return_value = 0
        
        with patch('subprocess.Popen', return_value=mock_process):
            manager.run_simulation(str(case_path))
            
            # Wait for output processing
            time.sleep(0.1)
            
            # Verify output was streamed
            assert manager.output_received.emit.call_count >= 3
            assert manager.error_received.emit.call_count >= 1
            manager.process_started.emit.assert_called_once()
            manager.process_finished.emit.assert_called_once_with(0)


class TestCrossPlatform:
    """Cross-platform compatibility tests."""
    
    def test_windows_path_handling(self, temp_dir):
        """Test path handling on Windows."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Mock Windows platform
        with patch('sys.platform', 'win32'):
            manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
            
            # Should handle Windows paths correctly
            case_path = r"C:\test\case"
            
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                manager.run_simulation(case_path)
                
                # Command should handle Windows paths
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                command = args[0]
                
                # Should contain the case path
                assert case_path in command
    
    def test_linux_path_handling(self, temp_dir):
        """Test path handling on Linux."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        # Mock Linux platform
        with patch('sys.platform', 'linux'):
            manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
            
            case_path = "/home/user/case"
            
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                manager.run_simulation(case_path)
                
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                command = args[0]
                
                # Should contain the case path
                assert case_path in command
    
    def test_process_execution_platform_differences(self, temp_dir):
        """Test process execution differences across platforms."""
        solver_path = Path(temp_dir) / "SPMFoam"
        solver_path.mkdir()
        
        case_path = Path(temp_dir) / "Case"
        case_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Test different platforms
        platforms = ['win32', 'linux', 'darwin']
        
        for platform in platforms:
            with patch('sys.platform', platform):
                with patch.object(manager.process_controller, 'start_process') as mock_start:
                    manager.run_simulation(str(case_path))
                    
                    # Should work on all platforms
                    mock_start.assert_called_once()
                    mock_start.reset_mock()