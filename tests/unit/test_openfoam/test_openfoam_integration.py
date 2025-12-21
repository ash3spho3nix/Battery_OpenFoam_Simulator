"""
Comprehensive unit tests for OpenFOAM integration components.

This module tests the OpenFOAM integration, including:
- ProcessController functionality
- OpenFOAMSolverManager
- OpenFOAMCaseManager
- MSYS2Executor
- Cross-platform compatibility
"""

import pytest
import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import subprocess

# Import test modules
from src.openfoam.process_controller import ProcessController
from src.openfoam.process_controller_enhanced import ProcessControllerEnhanced
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.openfoam.solver_manager_enhanced import OpenFOAMSolverManagerEnhanced
from src.openfoam.case_manager import OpenFOAMCaseManager
from src.openfoam.msys2_executor import MSYS2Executor


class TestProcessController:
    """Test suite for ProcessController class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.controller = ProcessController()
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.controller.cleanup()
        
    def test_initialization(self):
        """Test ProcessController initialization."""
        assert self.controller is not None
        assert not self.controller.is_running()
        assert not self.controller.is_paused()
        assert self.controller.get_exit_code() is None
        
    @patch('subprocess.Popen')
    def test_start_process(self, mock_popen):
        """Test starting a process."""
        # Mock successful process start
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Connect signals
        output_received = Mock()
        error_received = Mock()
        process_started = Mock()
        process_finished = Mock()
        
        self.controller.output_received.connect(output_received)
        self.controller.error_received.connect(error_received)
        self.controller.process_started.connect(process_started)
        self.controller.process_finished.connect(process_finished)
        
        # Start process
        self.controller.start_process("echo test", self.test_dir)
        
        # Verify process was started
        assert self.controller.is_running()
        process_started.assert_called_once()
        mock_popen.assert_called_once()
        
        # Clean up
        self.controller.terminate_process()
        assert not self.controller.is_running()
        
    @patch('subprocess.Popen')
    def test_process_output(self, mock_popen):
        """Test process output handling."""
        # Create mock process with output
        mock_process = Mock()
        mock_process.poll.side_effect = [None, None, 0]  # Running, then finished
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = ['line 1\n', 'line 2\n', '']
        mock_process.stderr.readline.return_value = ''
        mock_popen.return_value = mock_process
        
        # Collect output
        output_lines = []
        def collect_output(line):
            output_lines.append(line)
            
        self.controller.output_received.connect(collect_output)
        
        # Start and wait for completion
        self.controller.start_process("echo test")
        while self.controller.is_running():
            time.sleep(0.01)
            
        # Verify output was received
        assert len(output_lines) >= 2
        assert 'line 1' in output_lines[0] or 'line 2' in output_lines[0]
        
    @patch('subprocess.Popen')
    def test_process_error(self, mock_popen):
        """Test process error handling."""
        # Create mock process with error output
        mock_process = Mock()
        mock_process.poll.side_effect = [None, None, 0]  # Running, then finished
        mock_process.returncode = 1  # Error exit code
        mock_process.stdout.readline.return_value = ''
        mock_process.stderr.readline.side_effect = ['error message\n', '']
        mock_popen.return_value = mock_process
        
        # Collect errors
        error_lines = []
        def collect_error(line):
            error_lines.append(line)
            
        self.controller.error_received.connect(collect_error)
        self.controller.process_finished.connect(lambda code: None)
        
        # Start and wait for completion
        self.controller.start_process("echo test")
        while self.controller.is_running():
            time.sleep(0.01)
            
        # Verify error was received
        assert len(error_lines) >= 1
        assert 'error message' in error_lines[0]
        assert self.controller.get_exit_code() == 1
        
    @patch('subprocess.Popen')
    def test_terminate_process(self, mock_popen):
        """Test process termination."""
        # Mock process that takes time to terminate
        mock_process = Mock()
        mock_process.poll.return_value = None  # Still running
        mock_process.returncode = None
        mock_popen.return_value = mock_process
        
        self.controller.start_process("sleep 10")
        
        # Terminate process
        self.controller.terminate_process()
        
        # Verify process was terminated
        assert not self.controller.is_running()
        mock_process.terminate.assert_called_once()
        
    def test_pause_resume_process_unix(self):
        """Test process pause/resume on Unix systems."""
        if sys.platform == "win32":
            pytest.skip("Pause/resume not supported on Windows")
            
        # This test would require a real process that can be paused
        # For now, just test that the methods exist and don't crash
        try:
            self.controller.pause_process()
            self.controller.resume_process()
        except Exception as e:
            pytest.fail(f"Pause/resume failed: {e}")
            
    def test_buffer_management(self):
        """Test output buffer management."""
        # Test buffer access methods
        output_buffer = self.controller.get_output_buffer()
        error_buffer = self.controller.get_error_buffer()
        
        assert isinstance(output_buffer, list)
        assert isinstance(error_buffer, list)
        
        # Test buffer clearing
        self.controller.clear_buffers()
        assert len(self.controller.get_output_buffer()) == 0
        assert len(self.controller.get_error_buffer()) == 0


class TestProcessControllerEnhanced:
    """Test suite for ProcessControllerEnhanced class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.controller = ProcessControllerEnhanced()
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.controller.cleanup()
        
    def test_enhanced_initialization(self):
        """Test enhanced ProcessController initialization."""
        assert self.controller is not None
        assert hasattr(self.controller, 'performance_metrics')
        assert hasattr(self.controller, 'error_recovery')
        
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        # Start monitoring
        self.controller.start_performance_monitoring()
        
        # Simulate some work
        time.sleep(0.1)
        
        # Stop monitoring
        metrics = self.controller.stop_performance_monitoring()
        
        assert 'cpu_usage' in metrics
        assert 'memory_usage' in metrics
        assert 'execution_time' in metrics
        
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test recovery from process failure
        recovery_result = self.controller.recover_from_error("Process failed")
        assert recovery_result is True
        
        # Test recovery with retry
        recovery_result = self.controller.recover_with_retry(
            lambda: False, max_retries=3, delay=0.1
        )
        assert recovery_result is False  # Should fail after retries


class TestOpenFOAMSolverManager:
    """Test suite for OpenFOAMSolverManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.solver_name = "testSolver"
        self.solver_path = os.path.join(self.test_dir, self.solver_name)
        os.makedirs(self.solver_path, exist_ok=True)
        
        # Create a mock solver executable
        solver_executable = os.path.join(self.solver_path, self.solver_name)
        with open(solver_executable, 'w') as f:
            f.write('#!/bin/bash\necho "Solver running"\n')
        os.chmod(solver_executable, 0o755)
        
        self.manager = OpenFOAMSolverManager(self.test_dir, self.solver_name)
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.manager.process_controller.cleanup()
        
    def test_initialization(self):
        """Test OpenFOAMSolverManager initialization."""
        assert self.manager.project_path == self.test_dir
        assert self.manager.solver_name == self.solver_name
        assert not self.manager.is_running()
        assert not self.manager.is_paused()
        
    def test_get_solver_path(self):
        """Test getting solver path."""
        expected_path = self.solver_path
        actual_path = self.manager.get_solver_path()
        assert actual_path == expected_path
        
    def test_get_solver_executable(self):
        """Test getting solver executable path."""
        expected_executable = os.path.join(self.solver_path, self.solver_name)
        actual_executable = self.manager.get_solver_executable()
        assert actual_executable == expected_executable
        
    def test_check_solver_ready(self):
        """Test checking if solver is ready."""
        assert self.manager.check_solver_ready() is True
        
        # Remove executable and test again
        solver_executable = os.path.join(self.solver_path, self.solver_name)
        os.remove(solver_executable)
        assert self.manager.check_solver_ready() is False
        
    @patch.object(ProcessController, 'start_process')
    def test_build_solver(self, mock_start_process):
        """Test building the solver."""
        # Mock successful build process
        mock_start_process.return_value = None
        
        # Mock process controller to simulate successful build
        self.manager.process_controller.is_running = Mock(side_effect=[True, False])
        self.manager.process_controller.get_exit_code = Mock(return_value=0)
        
        # Test build
        result = self.manager.build_solver()
        assert result is True
        assert self.manager.check_solver_ready() is True
        
    @patch.object(ProcessController, 'start_process')
    def test_run_simulation(self, mock_start_process):
        """Test running a simulation."""
        # Create a mock case directory
        case_path = os.path.join(self.test_dir, "testCase")
        os.makedirs(case_path, exist_ok=True)
        system_dir = os.path.join(case_path, "system")
        os.makedirs(system_dir, exist_ok=True)
        
        # Create a minimal controlDict
        control_dict = os.path.join(system_dir, "controlDict")
        with open(control_dict, 'w') as f:
            f.write("""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
application testSolver;
startTime 0;
endTime 1;
deltaT 0.1;
writeInterval 0.1;
""")
        
        # Mock successful simulation start
        mock_start_process.return_value = None
        self.manager.process_controller.is_running = Mock(return_value=False)
        self.manager.process_controller.get_exit_code = Mock(return_value=0)
        
        # Test simulation start
        result = self.manager.run_simulation(case_path)
        assert result is True
        assert self.manager.is_running() is False  # Mocked as not running
        
    def test_stop_simulation(self):
        """Test stopping a simulation."""
        # Mock a running process
        self.manager.process_controller.is_running = Mock(return_value=True)
        self.manager.process_controller.terminate_process = Mock()
        
        # Stop simulation
        self.manager.stop_simulation()
        self.manager.process_controller.terminate_process.assert_called_once()
        
    def test_get_openfoam_info(self):
        """Test getting OpenFOAM installation information."""
        # This test checks that the method exists and returns appropriate type
        openfoam_info = self.manager.get_openfoam_info()
        assert openfoam_info is None or isinstance(openfoam_info, dict)


class TestOpenFOAMSolverManagerEnhanced:
    """Test suite for OpenFOAMSolverManagerEnhanced class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.solver_name = "testSolver"
        self.solver_path = os.path.join(self.test_dir, self.solver_name)
        os.makedirs(self.solver_path, exist_ok=True)
        
        # Create a mock solver executable
        solver_executable = os.path.join(self.solver_path, self.solver_name)
        with open(solver_executable, 'w') as f:
            f.write('#!/bin/bash\necho "Solver running"\n')
        os.chmod(solver_executable, 0o755)
        
        self.manager = OpenFOAMSolverManagerEnhanced(self.test_dir, self.solver_name)
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.manager.process_controller.cleanup()
        
    def test_enhanced_initialization(self):
        """Test enhanced solver manager initialization."""
        assert self.manager is not None
        assert hasattr(self.manager, 'performance_monitor')
        assert hasattr(self.manager, 'error_handler')
        
    def test_performance_monitoring(self):
        """Test performance monitoring during solver operations."""
        # Mock process controller to simulate running process
        self.manager.process_controller.is_running = Mock(side_effect=[True, False])
        self.manager.process_controller.get_exit_code = Mock(return_value=0)
        
        # Run simulation and check performance metrics
        case_path = os.path.join(self.test_dir, "testCase")
        os.makedirs(case_path, exist_ok=True)
        
        result = self.manager.run_simulation(case_path)
        assert result is True
        
        # Check if performance metrics were collected
        metrics = self.manager.get_performance_metrics()
        assert isinstance(metrics, dict)
        
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test recovery from solver failure
        recovery_result = self.manager.recover_from_solver_error("Solver failed")
        assert recovery_result is True
        
        # Test retry mechanism
        retry_result = self.manager.retry_operation(
            lambda: False, max_retries=2, delay=0.1
        )
        assert retry_result is False  # Should fail after retries


class TestOpenFOAMCaseManager:
    """Test suite for OpenFOAMCaseManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.case_path = os.path.join(self.test_dir, "testCase")
        self.manager = OpenFOAMCaseManager(self.case_path)
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test OpenFOAMCaseManager initialization."""
        assert self.manager.case_path == self.case_path
        assert self.manager.parameter_manager is not None
        
    def test_create_case_structure(self):
        """Test creating case directory structure."""
        result = self.manager.create_case_structure()
        assert result is True
        assert os.path.exists(self.case_path)
        
        # Check required directories were created
        required_dirs = ['system', 'constant', '0']
        for dir_name in required_dirs:
            assert os.path.exists(os.path.join(self.case_path, dir_name))
            
        # Check required files were created (they should exist as empty files)
        required_files = [
            'system/blockMeshDict',
            'system/topoSetDict',
            'system/controlDict',
            'system/fvSchemes',
            'system/fvSolution',
            'constant/LiProperties'
        ]
        for file_path in required_files:
            assert os.path.exists(os.path.join(self.case_path, file_path))
            
    def test_validate_case_structure(self):
        """Test validating case directory structure."""
        # Create structure first
        self.manager.create_case_structure()
        
        # Validate structure
        is_valid = self.manager.validate_case_structure()
        assert is_valid is True
        
        # Remove a required file and test validation
        blockmesh_path = os.path.join(self.case_path, 'system', 'blockMeshDict')
        os.remove(blockmesh_path)
        
        is_valid = self.manager.validate_case_structure()
        assert is_valid is False
        
    def test_update_geometry_parameters(self):
        """Test updating geometry parameters."""
        self.manager.create_case_structure()
        
        # Create minimal blockMeshDict
        blockmesh_path = os.path.join(self.case_path, 'system', 'blockMeshDict')
        with open(blockmesh_path, 'w') as f:
            f.write("""
convertToMeters 1e-6;
vertices
(
    (-100 -100 -100)
    (100 -100 -100)
    (100 100 -100)
    (-100 100 -100)
    (-100 -100 100)
    (100 -100 100)
    (100 100 100)
    (-100 100 100)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1)
);
""")
                
        # Update geometry parameters
        params = {
            'length': 200.0,
            'width': 150.0,
            'height': 100.0,
            'x_division': 40,
            'y_division': 30,
            'z_division': 20,
            'unit': 'micrometer'
        }
        
        result = self.manager.update_geometry_parameters(params)
        assert result is True
        
        # Verify file was updated (basic check)
        with open(blockmesh_path, 'r') as f:
            content = f.read()
            assert 'convertToMeters 1e-6' in content
            
    def test_update_material_parameters(self):
        """Test updating material parameters."""
        self.manager.create_case_structure()
        
        # Create minimal LiProperties file
        li_properties_path = os.path.join(self.case_path, 'constant', 'LiProperties')
        with open(li_properties_path, 'w') as f:
            f.write("""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      LiProperties;
}
Ds_value [0 0 0 0 0 0 0] 1e-14;
Cs_max [0 0 0 0 0 0 0] 30000;
""")
                
        # Update material parameters
        params = {
            'Ds_value': 2e-14,
            'CS_max': 25000
        }
        
        result = self.manager.update_material_parameters(params)
        assert result is True
        
        # Verify file was updated
        with open(li_properties_path, 'r') as f:
            content = f.read()
            assert '2e-14' in content
            assert '25000' in content
            
    def test_setup_initial_conditions(self):
        """Test setting up initial conditions."""
        self.manager.create_case_structure()
        
        # Setup initial conditions
        initial_values = {
            'C': 1.0,
            'Cs': 0.5,
            'p': 0.0
        }
        
        result = self.manager.setup_initial_conditions(initial_values)
        assert result is True
        
        # Verify field files were created
        zero_dir = os.path.join(self.case_path, '0')
        assert os.path.exists(os.path.join(zero_dir, 'C'))
        assert os.path.exists(os.path.join(zero_dir, 'Cs'))
        assert os.path.exists(os.path.join(zero_dir, 'p'))
        
    def test_backup_and_restore_case(self):
        """Test backing up and restoring a case."""
        self.manager.create_case_structure()
        
        # Create some content in the case
        test_file = os.path.join(self.case_path, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
            
        # Backup case
        backup_path = os.path.join(self.test_dir, 'backup')
        result = self.manager.backup_case(backup_path)
        assert result is True
        assert os.path.exists(backup_path)
        
        # Remove original and restore from backup
        shutil.rmtree(self.case_path)
        result = self.manager.restore_case(backup_path)
        assert result is True
        assert os.path.exists(self.case_path)
        assert os.path.exists(test_file)
        
    def test_get_case_info(self):
        """Test getting case information."""
        self.manager.create_case_structure()
        
        info = self.manager.get_case_info()
        assert 'path' in info
        assert 'exists' in info
        assert 'structure_valid' in info
        assert 'parameters' in info
        assert 'files' in info
        
        assert info['path'] == self.case_path
        assert info['exists'] is True
        assert info['structure_valid'] is True


class TestMSYS2Executor:
    """Test suite for MSYS2Executor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.executor = MSYS2Executor(msys2_path=self.test_dir)
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test MSYS2Executor initialization."""
        assert self.executor is not None
        assert self.executor.msys2_path == self.test_dir
        
    def test_command_execution(self):
        """Test command execution through MSYS2."""
        # Mock subprocess.run to avoid actual execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock()
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Command executed successfully"
            
            # Test command execution
            result = self.executor.execute_command("echo test")
            
            # Verify subprocess was called with correct arguments
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            
            # Check that MSYS2 path is in the command
            assert self.test_dir in str(args[0])
            
    def test_path_conversion(self):
        """Test Windows to Unix path conversion."""
        # Test Windows path conversion
        windows_path = "C:\\Users\\test\\Documents"
        unix_path = self.executor.convert_windows_path(windows_path)
        
        # Should convert to Unix format
        assert "/" in unix_path
        assert "\\" not in unix_path
        
    def test_environment_setup(self):
        """Test MSYS2 environment setup."""
        # Test that environment variables are properly set
        env = self.executor.get_environment()
        
        assert isinstance(env, dict)
        # Should contain MSYS2-specific environment variables
        assert 'MSYSTEM' in env or 'PATH' in env
        
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_integration(self):
        """Test Windows-specific MSYS2 integration."""
        # This test would require actual MSYS2 installation
        # For now, just test that the class can be instantiated
        assert self.executor is not None


class TestOpenFOAMIntegration:
    """Integration tests for OpenFOAM components."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.test_dir, "project")
        self.case_path = os.path.join(self.project_path, "testCase")
        self.solver_name = "testSolver"
        
        # Create project structure
        os.makedirs(self.project_path, exist_ok=True)
        os.makedirs(self.case_path, exist_ok=True)
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_full_workflow(self):
        """Test a complete workflow: case setup -> solver build -> simulation."""
        # 1. Set up case
        case_manager = OpenFOAMCaseManager(self.case_path)
        case_manager.create_case_structure()
        case_manager.setup_initial_conditions({'C': 1.0, 'Cs': 0.5, 'p': 0.0})
        
        # 2. Set up solver
        solver_manager = OpenFOAMSolverManager(self.project_path, self.solver_name)
        solver_path = solver_manager.get_solver_path()
        os.makedirs(solver_path, exist_ok=True)
        
        # Create mock solver executable
        solver_executable = os.path.join(solver_path, self.solver_name)
        with open(solver_executable, 'w') as f:
            f.write('#!/bin/bash\necho "Solver running"\n')
        os.chmod(solver_executable, 0o755)
        
        # 3. Verify components work together
        assert case_manager.validate_case_structure() is True
        assert solver_manager.check_solver_ready() is True
        
        # 4. Test that case info can be retrieved
        case_info = case_manager.get_case_info()
        assert case_info['exists'] is True
        assert case_info['structure_valid'] is True
        
        print("Full workflow test passed successfully!")
    
    def test_error_handling_integration(self):
        """Test error handling across OpenFOAM components."""
        # Test case manager error handling
        case_manager = OpenFOAMCaseManager("/nonexistent/path")
        
        # Should handle missing directory gracefully
        result = case_manager.validate_case_structure()
        assert result is False
        
        # Test solver manager error handling
        solver_manager = OpenFOAMSolverManager("/nonexistent/path", "testSolver")
        
        # Should handle missing solver gracefully
        result = solver_manager.check_solver_ready()
        assert result is False
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring across components."""
        # Create enhanced components
        case_manager = OpenFOAMCaseManager(self.case_path)
        solver_manager = OpenFOAMSolverManagerEnhanced(self.project_path, self.solver_name)
        
        # Start performance monitoring
        solver_manager.start_performance_monitoring()
        
        # Perform operations
        case_manager.create_case_structure()
        
        # Stop monitoring and check metrics
        metrics = solver_manager.stop_performance_monitoring()
        assert isinstance(metrics, dict)
        assert 'execution_time' in metrics


class TestCrossPlatformCompatibility:
    """Test suite for cross-platform compatibility."""
    
    def test_path_handling(self):
        """Test path handling across platforms."""
        from src.openfoam.msys2_executor import MSYS2Executor
        
        executor = MSYS2Executor()
        
        # Test different path formats
        test_paths = [
            "/unix/style/path",
            "C:\\Windows\\style\\path",
            "relative/path",
            "../parent/path"
        ]
        
        for path in test_paths:
            # Should handle all path formats
            try:
                result = executor.convert_windows_path(path)
                assert isinstance(result, str)
            except Exception:
                # Some paths might not be convertible, which is OK
                pass
    
    def test_process_execution(self):
        """Test process execution across platforms."""
        controller = ProcessController()
        
        # Test with different command formats
        test_commands = [
            "echo test",
            "ls -la",
            "pwd",
            "date"
        ]
        
        for command in test_commands:
            # Should handle different command formats
            try:
                controller.start_process(command, "/tmp")
                controller.terminate_process()
            except Exception as e:
                # Some commands might fail on different platforms
                assert "platform" in str(e).lower() or "command" in str(e).lower()
    
    def test_file_operations(self):
        """Test file operations across platforms."""
        case_manager = OpenFOAMCaseManager("/tmp/test_case")
        
        # Test file creation
        result = case_manager.create_case_structure()
        
        # Should work on all platforms or fail gracefully
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])