#!/usr/bin/env python3
"""
Test imports for all modules in the Battery Simulator package.

This module tests that all modules can be imported successfully
and that there are no circular import issues.
"""

import sys
import importlib
import logging
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_core_imports():
    """Test importing core modules."""
    logger.info("Testing core module imports...")
    
    try:
        # Test main window import
        logger.info("  - Testing main window...")
        from src.gui.main_window import MainWindow
        logger.info("    ✓ MainWindow imported successfully")
        
        # Test project manager import
        logger.info("  - Testing project manager...")
        from src.core.project_manager_enhanced import EnhancedProjectManager
        logger.info("    ✓ ProjectManager imported successfully")
        
        # Test UI config import
        logger.info("  - Testing UI config...")
        from src.gui.ui_config import UIConfig
        logger.info("    ✓ UIConfig imported successfully")
        
        # Test UI loader import
        logger.info("  - Testing UI loader...")
        from src.gui.ui_loader import UiLoader
        logger.info("    ✓ UiLoader imported successfully")
        
        # Test interface factory import
        logger.info("  - Testing interface factory...")
        from src.gui.interface_factory import InterfaceFactory
        logger.info("    ✓ InterfaceFactory imported successfully")
        
        logger.info("All core imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import core modules: {e}")
        return False

def test_gui_imports():
    """Test importing GUI modules."""
    logger.info("Testing GUI module imports...")
    
    try:
        # Test base interface import
        logger.info("  - Testing base interface...")
        from src.gui.interfaces.base_interface import BaseInterface
        logger.info("    ✓ BaseInterface imported successfully")
        
        # Test carbon interface import
        logger.info("  - Testing carbon interface...")
        from src.gui.interfaces.carbon_interface import CarbonInterface
        logger.info("    ✓ CarbonInterface imported successfully")
        
        # Test halfcell interface import
        logger.info("  - Testing halfcell interface...")
        from src.gui.interfaces.halfcell_interface import HalfCellInterface
        logger.info("    ✓ HalfCellInterface imported successfully")
        
        # Test fullcell interface import
        logger.info("  - Testing fullcell interface...")
        from src.gui.interfaces.fullcell_interface import FullCellInterface
        logger.info("    ✓ FullCellInterface imported successfully")
        
        logger.info("All GUI imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import GUI modules: {e}")
        return False

def test_openfoam_imports():
    """Test importing OpenFOAM modules."""
    logger.info("Testing OpenFOAM module imports...")
    
    try:
        # Test process controller import
        logger.info("  - Testing process controller...")
        from src.openfoam.process_controller import ProcessController
        logger.info("    ✓ ProcessController imported successfully")
        
        # Test solver manager import
        logger.info("  - Testing solver manager...")
        from src.openfoam.solver_manager import SolverManager
        logger.info("    ✓ SolverManager imported successfully")
        
        logger.info("All OpenFOAM imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import OpenFOAM modules: {e}")
        return False

def test_utils_imports():
    """Test importing utility modules."""
    logger.info("Testing utility module imports...")
    
    try:
        # Test file operations import
        logger.info("  - Testing file operations...")
        from src.utils.file_operations import FileOperations
        logger.info("    ✓ FileOperations imported successfully")
        
        # Test parameter parser import
        logger.info("  - Testing parameter parser...")
        from src.utils.parameter_parser import ParameterParser
        logger.info("    ✓ ParameterParser imported successfully")
        
        logger.info("All utility imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import utility modules: {e}")
        return False

def test_package_import():
    """Test importing the entire package."""
    logger.info("Testing package import...")
    
    try:
        # Test package import
        logger.info("  - Testing package import...")
        import src
        logger.info("    ✓ Package imported successfully")
        
        # Test package contents
        logger.info("  - Testing package contents...")
        assert hasattr(src, 'MainWindow'), "MainWindow not found in package"
        assert hasattr(src, 'ProjectManager'), "ProjectManager not found in package"
        assert hasattr(src, 'InterfaceFactory'), "InterfaceFactory not found in package"
        assert hasattr(src, 'UiLoader'), "UiLoader not found in package"
        assert hasattr(src, 'ProcessController'), "ProcessController not found in package"
        assert hasattr(src, 'SolverManager'), "SolverManager not found in package"
        assert hasattr(src, 'FileOperations'), "FileOperations not found in package"
        assert hasattr(src, 'ParameterParser'), "ParameterParser not found in package"
        
        logger.info("    ✓ Package contents verified")
        logger.info("Package import successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import package: {e}")
        return False

def test_circular_imports():
    """Test for circular imports by importing modules in different orders."""
    logger.info("Testing for circular imports...")
    
    # List of modules to test
    modules_to_test = [
        'src.gui.main_window',
        'src.core.project_manager',
        'src.gui.ui_config',
        'src.gui.ui_loader',
        'src.gui.interface_factory',
        'src.gui.interfaces.base_interface',
        'src.gui.interfaces.carbon_interface',
        'src.gui.interfaces.halfcell_interface',
        'src.gui.interfaces.fullcell_interface',
        'src.openfoam.process_controller',
        'src.openfoam.solver_manager',
        'src.utils.file_operations',
        'src.utils.parameter_parser'
    ]
    
    for module_name in modules_to_test:
        try:
            # Clear the module from sys.modules if it exists
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Import the module
            importlib.import_module(module_name)
            logger.info(f"    ✓ {module_name} imported successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import {module_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error importing {module_name}: {e}")
            return False
    
    logger.info("Circular import test successful!")
    return True

def run_all_import_tests():
    """Run all import tests."""
    logger.info("Running all import tests...")
    
    tests = [
        test_core_imports,
        test_gui_imports,
        test_openfoam_imports,
        test_utils_imports,
        test_package_import,
        test_circular_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    logger.info(f"\nImport test summary:")
    logger.info(f"  Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("All import tests passed!")
        return True
    else:
        logger.error("Some import tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_import_tests()
    sys.exit(0 if success else 1)