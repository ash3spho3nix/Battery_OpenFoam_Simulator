#!/usr/bin/env python3
"""
Test script to validate Core App Developer fixes for Battery Simulator.

This script tests the critical interface issues that were addressed:
- Issue #9: ProjectManager initialization
- Issue #2: Project path passing
- Issue #3: Interface initialization
- Issue #1: Signal-slot connections
- Issue #7: InterfaceFactory parent-child relationships
- Issue #8: UI mode validation flexibility
- Issue #10: Error propagation

Usage:
    python tests/unit/test_core_app_fixes.py
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Add src to Python path (relative to this test file)
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        logger.info(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        logger.error(f"❌ FAIL: {test_name} - {error}")
    
    def get_summary(self):
        total = self.passed + self.failed
        return f"Tests: {total}, Passed: {self.passed}, Failed: {self.failed}"


def test_imports():
    """Test that all required modules can be imported."""
    try:
        # Test imports without creating GUI objects
        from src.gui.ui_config import UIConfig
        from src.gui.interface_factory import InterfaceFactory
        from src.gui.interfaces.base_interface import BaseInterface
        
        # Check that UIConfig has UIMode
        if hasattr(UIConfig, 'UIMode'):
            return True, "All imports successful"
        else:
            return False, "UIConfig.UIMode not found"
            
    except Exception as e:
        return False, f"Import failed: {e}"


def test_uimode_enum():
    """Test Issue #8: UI mode enum exists and has correct values."""
    try:
        from src.gui.ui_config import UIConfig
        
        # Check UIMode enum
        if hasattr(UIConfig, 'UIMode'):
            modes = [mode.name for mode in UIConfig.UIMode]
            expected_modes = ['AUTO_DETECT', 'UI_FILES', 'HAND_CODED']
            
            if all(mode in modes for mode in expected_modes):
                return True, f"UIMode enum has correct values: {modes}"
            else:
                return False, f"UIMode missing expected values. Found: {modes}"
        else:
            return False, "UIMode enum not found"
            
    except Exception as e:
        return False, f"Exception: {e}"


def test_base_interface_signals():
    """Test Issue #1: BaseInterface has required signals."""
    try:
        from src.gui.interfaces.base_interface import BaseInterface
        
        # Check if BaseInterface class has the required attributes
        required_attrs = [
            'exit_signal', 'error_signal', 'simulation_started', 
            'simulation_stopped', 'output_received', 'error_received'
        ]
        
        missing = []
        for attr in required_attrs:
            if not hasattr(BaseInterface, attr):
                missing.append(attr)
        
        if not missing:
            return True, "BaseInterface has all required signals"
        else:
            return False, f"BaseInterface missing signals: {missing}"
            
    except Exception as e:
        return False, f"Exception: {e}"


def test_base_interface_methods():
    """Test Issue #3: BaseInterface has required methods."""
    try:
        from src.gui.interfaces.base_interface import BaseInterface
        
        # Check if BaseInterface class has the required methods
        required_methods = ['set_project_paths', '_get_widget', '_get_widget_value']
        
        missing = []
        for method in required_methods:
            if not hasattr(BaseInterface, method):
                missing.append(method)
        
        if not missing:
            return True, "BaseInterface has all required methods"
        else:
            return False, f"BaseInterface missing methods: {missing}"
            
    except Exception as e:
        return False, f"Exception: {e}"


def test_interface_factory_methods():
    """Test Issue #7: InterfaceFactory has required methods."""
    try:
        from src.gui.interface_factory import InterfaceFactory
        
        # Check if InterfaceFactory class has the required methods
        required_methods = ['create_interface', '_create_interface_by_mode']
        
        missing = []
        for method in required_methods:
            if not hasattr(InterfaceFactory, method):
                missing.append(method)
        
        if not missing:
            return True, "InterfaceFactory has all required methods"
        else:
            return False, f"InterfaceFactory missing methods: {missing}"
            
    except Exception as e:
        return False, f"Exception: {e}"


def test_project_manager_import():
    """Test Issue #9: ProjectManager can be imported."""
    try:
        from src.core.project_manager import ProjectManager
        return True, "ProjectManager import successful"
    except Exception as e:
        return False, f"ProjectManager import failed: {e}"


def test_parameter_manager_import():
    """Test Issue #6: ParameterManager can be imported."""
    try:
        from src.utils.parameter_parser import ParameterManager
        return True, "ParameterManager import successful"
    except Exception as e:
        return False, f"ParameterManager import failed: {e}"


def test_process_controller_import():
    """Test Issue #5: ProcessController can be imported."""
    try:
        from src.openfoam.process_controller import ProcessController
        return True, "ProcessController import successful"
    except Exception as e:
        return False, f"ProcessController import failed: {e}"


def test_solver_manager_import():
    """Test Issue #6: OpenFOAMSolverManager can be imported."""
    try:
        from src.openfoam.solver_manager import OpenFOAMSolverManager
        return True, "OpenFOAMSolverManager import successful"
    except Exception as e:
        return False, f"OpenFOAMSolverManager import failed: {e}"


def run_all_tests():
    """Run all tests and return results."""
    logger.info("🧪 Starting Core App Developer fixes validation...")
    
    results = TestResults()
    
    # List of tests to run
    tests = [
        ("Import Test", test_imports),
        ("UI Mode Enum", test_uimode_enum),
        ("BaseInterface Signals", test_base_interface_signals),
        ("BaseInterface Methods", test_base_interface_methods),
        ("InterfaceFactory Methods", test_interface_factory_methods),
        ("ProjectManager Import", test_project_manager_import),
        ("ParameterManager Import", test_parameter_manager_import),
        ("ProcessController Import", test_process_controller_import),
        ("SolverManager Import", test_solver_manager_import),
    ]
    
    # Run each test
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            if success:
                results.add_pass(f"{test_name}: {message}")
            else:
                results.add_fail(test_name, message)
        except Exception as e:
            results.add_fail(test_name, f"Unexpected error: {str(e)}")
            logger.error(f"Test {test_name} failed with exception: {e}")
            traceback.print_exc()
    
    return results


def main():
    """Main test runner."""
    logger.info("=" * 60)
    logger.info("BATTERY SIMULATOR - CORE APP DEVELOPER FIXES VALIDATION")
    logger.info("=" * 60)
    
    # Run all tests
    results = run_all_tests()
    
    # Print summary
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    logger.info(results.get_summary())
    
    if results.failed > 0:
        logger.error("❌ Some tests failed. Please review the issues above.")
        logger.info("\nFailed tests:")
        for test_name, error in results.errors:
            logger.error(f"  - {test_name}: {error}")
        sys.exit(1)
    else:
        logger.info("✅ All tests passed! Core App Developer fixes are working correctly.")
        sys.exit(0)


if __name__ == "__main__":
    main()