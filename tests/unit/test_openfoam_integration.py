"""
Unit tests for OpenFOAM integration components.

This module tests the enhanced OpenFOAM integration including:
- ProcessController functionality
- OpenFOAMSolverManager operations
- Error detection and handling
- Cross-platform compatibility
"""

import unittest
import unittest.mock as mock
import os
import sys
import tempfile
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEventLoop, QTimer

# Import the modules to test
from src.openfoam.process_controller_enhanced import (
    ProcessController, PlatformDetector, PathHandler, 
    ProcessMonitor, OpenFOAMError, ErrorRecovery
)
from src.openfoam.solver_manager_enhanced import (
    OpenFOAMSolverManager, SolverValidator
)


class TestProcessController(unittest.TestCase):
    """Test cases for ProcessController."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_send_signal_method_exists(self):
        """Test that send_signal method exists and works."""
        controller = ProcessController()
        
        # Test that method exists
        self.assertTrue(hasattr(controller, 'send_signal'))
        
        # Test with mock process
        mock_process = mock.Mock()
        controller.process = mock_process
        controller._running = True
        
        controller.send_signal(19)  # SIGSTOP
        
        # Verify send_signal was called on process
        mock_process.send_signal.assert_called_once_with(19)
    
    def test_get_exit_code_method_exists(self):
        """Test that get_exit_code method exists and works."""
        controller = ProcessController()
        
        # Test that method exists
        self.assertTrue(hasattr(controller, 'get_exit_code'))
        
        # Test with mock process
        mock_process = mock.Mock()
        mock_process.returncode = 0
        controller.process = mock_process
        
        exit_code = controller.get_exit_code()
        self.assertEqual(exit_code, 0)
    
    def test_compilation_error_detection(self):
        """Test compilation error detection."""
        controller = ProcessController()
        
        # Test compilation error patterns
        test_output = "error: undefined reference to 'some_function'"
        errors = controller._detect_compilation_errors(test_output)
        
        self.assertTrue(len(errors) > 0)
        self.assertIn('some_function', errors[0])
    
    def test_runtime_error_detection(self):
        """Test runtime error detection."""
        controller = ProcessController()
        
        # Test runtime error patterns
        test_output = "FOAM FATAL ERROR: Divergence detected"
        errors = controller._detect_runtime_errors(test_output)
        
        self.assertTrue(len(errors) > 0)
        self.assertIn('Divergence detected', errors[0])
    
    def test_platform_detection(self):
        """Test platform detection functionality."""
        platform_info = PlatformDetector.get_platform_info()
        
        # Check that all expected keys are present
        expected_keys = ['system', 'release', 'architecture', 'processor', 'openfoam_compatible']
        for key in expected_keys:
            self.assertIn(key, platform_info)
        
        # Check system is valid
        self.assertIn(platform_info['system'], ['Windows', 'Linux', 'Darwin'])


class TestOpenFOAMSolverManager(unittest.TestCase):
    """Test cases for OpenFOAMSolverManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.temp_dir = tempfile.mkdtemp()
        self.solver_path = self.temp_dir
        self.solver_name = "testSolver"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_send_signal_method_exists(self):
        """Test that send_signal method exists in solver manager."""
        manager = OpenFOAMSolverManager(self.solver_path, self.solver_name)
        
        # Test that method exists
        self.assertTrue(hasattr(manager, 'send_signal'))
        
        # Test with mock process controller
        with mock.patch.object(manager.process_controller, 'send_signal') as mock_send_signal:
            manager.send_signal(18)  # SIGCONT
            mock_send_signal.assert_called_once_with(18)
    
    def test_get_exit_code_method_exists(self):
        """Test that get_exit_code method exists in solver manager."""
        manager = OpenFOAMSolverManager(self.solver_path, self.solver_name)
        
        # Test that method exists
        self.assertTrue(hasattr(manager, 'get_exit_code'))
        
        # Test with mock process controller
        with mock.patch.object(manager.process_controller, 'get_exit_code', return_value=0):
            exit_code = manager.get_exit_code()
            self.assertEqual(exit_code, 0)
    
    def test_platform_info(self):
        """Test platform information retrieval."""
        manager = OpenFOAMSolverManager(self.solver_path, self.solver_name)
        
        platform_info = manager._get_platform_info()
        
        # Check that platform info is returned
        self.assertIsInstance(platform_info, dict)
        self.assertIn('system', platform_info)
    
    def test_solver_executable_path(self):
        """Test solver executable path generation."""
        manager = OpenFOAMSolverManager(self.solver_path, self.solver_name)
        
        executable_path = manager.get_solver_executable()
        
        # Check that path contains solver name
        self.assertIn(self.solver_name, executable_path)
        
        # Check that path is absolute
        self.assertTrue(os.path.isabs(executable_path))


class TestPathHandler(unittest.TestCase):
    """Test cases for PathHandler."""
    
    @mock.patch('platform.system')
    def test_windows_path_conversion(self, mock_system):
        """Test Windows to MSYS2 path conversion."""
        mock_system.return_value = 'Windows'
        
        windows_path = r"C:\Users\test\project"
        msys2_path = PathHandler.convert_path_for_openfoam(windows_path)
        
        expected_path = "/c/Users/test/project"
        self.assertEqual(msys2_path, expected_path)
    
    @mock.patch('platform.system')
    def test_linux_path_conversion(self, mock_system):
        """Test Linux path conversion."""
        mock_system.return_value = 'Linux'
        
        linux_path = "/home/user/project"
        converted_path = PathHandler.convert_path_for_openfoam(linux_path)
        
        # Should return the same path on Linux
        self.assertEqual(converted_path, linux_path)


class TestErrorRecovery(unittest.TestCase):
    """Test cases for ErrorRecovery."""
    
    def test_compilation_error_recovery(self):
        """Test recovery suggestions for compilation errors."""
        error = OpenFOAMError("COMPILATION_ERROR", "Solver compilation failed")
        recovery_actions = ErrorRecovery.suggest_recovery(error)
        
        self.assertTrue(len(recovery_actions) > 0)
        self.assertIn("Check OpenFOAM installation", recovery_actions[0])
        self.assertIn("wclean && wmake", recovery_actions[-1])
    
    def test_runtime_error_recovery(self):
        """Test recovery suggestions for runtime errors."""
        error = OpenFOAMError("RUNTIME_ERROR", "Divergence detected")
        recovery_actions = ErrorRecovery.suggest_recovery(error)
        
        self.assertTrue(len(recovery_actions) > 0)
        self.assertIn("Check case setup", recovery_actions[0])
        self.assertIn("Reduce time step size", recovery_actions[-1])


class TestSolverValidator(unittest.TestCase):
    """Test cases for SolverValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_solver_setup_validation(self):
        """Test solver setup validation."""
        # Create a mock solver manager
        manager = mock.Mock()
        manager.solver_path = self.temp_dir
        manager.solver_name = "testSolver"
        
        # Mock the platform info to be compatible
        with mock.patch.object(OpenFOAMSolverManager, '_get_platform_info', 
                              return_value={'openfoam_compatible': True}):
            report = SolverValidator.validate_solver_setup(manager)
        
        # Should be valid since path exists and platform is compatible
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['issues']), 0)
    
    def test_case_setup_validation(self):
        """Test case setup validation."""
        case_path = self.temp_dir
        
        # Create required directories
        os.makedirs(os.path.join(case_path, 'system'))
        os.makedirs(os.path.join(case_path, 'constant'))
        os.makedirs(os.path.join(case_path, '0'))
        
        # Create required files
        with open(os.path.join(case_path, 'system', 'blockMeshDict'), 'w') as f:
            f.write("// blockMeshDict")
        with open(os.path.join(case_path, 'system', 'controlDict'), 'w') as f:
            f.write("// controlDict")
        with open(os.path.join(case_path, 'constant', 'LiProperties'), 'w') as f:
            f.write("// LiProperties")
        
        report = SolverValidator.validate_case_setup(case_path)
        
        # Should be valid since all required files and directories exist
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['issues']), 0)


class TestProcessMonitor(unittest.TestCase):
    """Test cases for ProcessMonitor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_monitor_initialization(self):
        """Test process monitor initialization."""
        # Create a mock process controller
        controller = mock.Mock()
        controller.process = None
        controller.is_running.return_value = False
        
        monitor = ProcessMonitor(controller)
        
        # Test that monitor can be initialized
        self.assertFalse(monitor.monitoring)
        self.assertIsNone(monitor.monitor_thread)
    
    @unittest.skipUnless(os.name == 'posix', "Requires psutil and POSIX system")
    def test_resource_monitoring(self):
        """Test resource monitoring (requires psutil)."""
        try:
            import psutil
        except ImportError:
            self.skipTest("psutil not available")
        
        # Create a mock process controller with a real process
        controller = mock.Mock()
        controller.process = psutil.Process()
        controller.is_running.return_value = True
        
        monitor = ProcessMonitor(controller)
        
        # Test that monitor can be started and stopped
        monitor.start_monitoring(interval=0.1)
        self.assertTrue(monitor.monitoring)
        
        # Give it a moment to run
        time.sleep(0.2)
        
        monitor.stop_monitoring()
        self.assertFalse(monitor.monitoring)


class TestIntegration(unittest.TestCase):
    """Integration tests for OpenFOAM components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = QApplication.instance() or QApplication([])
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_solver_manager_workflow(self):
        """Test the complete solver manager workflow."""
        solver_path = self.temp_dir
        solver_name = "testSolver"
        
        # Create a minimal solver directory structure
        os.makedirs(os.path.join(solver_path, 'platforms', 'linux64GccDPInt32Opt', 'bin'))
        
        manager = OpenFOAMSolverManager(solver_path, solver_name)
        
        # Test that all critical methods exist
        self.assertTrue(hasattr(manager, 'send_signal'))
        self.assertTrue(hasattr(manager, 'get_exit_code'))
        self.assertTrue(hasattr(manager, 'compile_solver'))
        self.assertTrue(hasattr(manager, 'run_simulation'))
        self.assertTrue(hasattr(manager, 'check_solver_ready'))
        
        # Test executable path generation
        executable_path = manager.get_solver_executable()
        self.assertIn(solver_name, executable_path)
    
    def test_error_propagation(self):
        """Test error propagation through the system."""
        controller = ProcessController()
        
        # Test error signal emission
        error_received = []
        controller.error_received.connect(lambda msg: error_received.append(msg))
        
        # Simulate an error
        controller.error_received.emit("Test error message")
        
        # Check that error was received
        self.assertEqual(len(error_received), 1)
        self.assertEqual(error_received[0], "Test error message")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)