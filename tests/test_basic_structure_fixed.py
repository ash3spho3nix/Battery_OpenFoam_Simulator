#!/usr/bin/env python3
"""
Fixed basic structure test for Battery Simulator.
This script tests the basic imports and structure of the application
to ensure all components can be loaded without circular import issues.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def test_imports():
    """Test basic imports."""
    logger.info("Testing basic imports...")
    
    try:
        # Test core imports
        from src.core.constants import APP_NAME, APP_VERSION
        logger.info(f"✓ Core constants imported: {APP_NAME} v{APP_VERSION}")
        
        from src.core.project_manager import ProjectManager
        logger.info("✓ ProjectManager imported")
        
        # Test GUI imports
        from src.gui.ui_config import UIConfig, UILoadingMode
        logger.info("✓ UIConfig imported")
        
        from src.gui.ui_loader import UILoader
        logger.info("✓ UILoader imported")
        
        from src.gui.ui_loader_enhanced import UILoaderEnhanced
        logger.info("✓ UILoaderEnhanced imported")
        
        from src.gui.interface_factory import InterfaceFactory
        logger.info("✓ InterfaceFactory imported")
        
        from src.gui.main_window import MainWindow
        logger.info("✓ MainWindow imported")
        
        from src.gui.interfaces.base_interface import BaseInterface
        logger.info("✓ BaseInterface imported")
        
        # Test OpenFOAM imports
        from src.openfoam.process_controller import ProcessController
        logger.info("✓ ProcessController imported")
        
        from src.openfoam.solver_manager import OpenFOAMSolverManager
        logger.info("✓ OpenFOAMSolverManager imported")
        
        # Test utility imports
        from src.utils.file_operations import TemplateManager, FileBackupManager
        logger.info("✓ File operations imported")
        
        from src.utils.parameter_parser import ParameterManager
        logger.info("✓ ParameterManager imported")
        
        logger.info("✓ All imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error during imports: {e}")
        return False

def test_ui_config():
    """Test UI configuration."""
    logger.info("Testing UI configuration...")
    
    try:
        from src.gui.ui_config import UIConfig, UILoadingMode
        
        # Test default configuration
        config = UIConfig()
        logger.info(f"✓ Default config created: {config}")
        
        # Test environment configuration
        os.environ["BATTERY_SIM_UI_MODE"] = "auto_detect"
        env_config = UIConfig.from_environment()
        logger.info(f"✓ Environment config created: {env_config}")
        
        # Test mode switching
        config.set_mode(UILoadingMode.UI_FILES)
        logger.info(f"✓ Mode set to UI_FILES: {config}")
        
        logger.info("✓ UI configuration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ UI configuration test failed: {e}")
        return False

def test_constants():
    """Test constants module."""
    logger.info("Testing constants...")
    
    try:
        from src.core.constants import (
            SUPPORTED_MODULES, SOLVER_NAMES, PARAMETER_FILES,
            DEFAULT_PARAMETERS, ERROR_MESSAGES
        )
        
        logger.info(f"✓ Supported modules: {list(SUPPORTED_MODULES.keys())}")
        logger.info(f"✓ Solver names: {list(SOLVER_NAMES.keys())}")
        logger.info(f"✓ Parameter files: {list(PARAMETER_FILES.keys())}")
        logger.info(f"✓ Default parameters: {len(DEFAULT_PARAMETERS)} items")
        logger.info(f"✓ Error messages: {len(ERROR_MESSAGES)} items")
        
        logger.info("✓ Constants tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Constants test failed: {e}")
        return False

def test_project_manager():
    """Test project manager."""
    logger.info("Testing project manager...")
    
    try:
        from src.core.project_manager import ProjectManager
        
        # Create project manager with default path
        pm = ProjectManager(base_projects_path=os.path.join(os.getcwd(), "test_projects"))
        logger.info("✓ ProjectManager created")
        
        # Test basic functionality
        logger.info("✓ Project manager tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Project manager test failed: {e}")
        return False

def test_ui_loader():
    """Test UI loader functionality."""
    logger.info("Testing UI loader...")
    
    try:
        from src.gui.ui_loader import UILoader
        
        # Test UI path resolution
        ui_path = UILoader.get_ui_path("mainwindow")
        logger.info(f"✓ UI path resolved: {ui_path}")
        
        # Test UI file existence check (may fail if UI files don't exist, but that's OK)
        exists = UILoader.ui_file_exists("mainwindow")
        logger.info(f"✓ UI file exists check: {exists}")
        
        logger.info("✓ UI loader tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ UI loader test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting basic structure tests...")
    
    tests = [
        test_imports,
        test_ui_config,
        test_constants,
        test_project_manager,
        test_ui_loader
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                logger.error(f"✗ Test {test.__name__} failed")
        except Exception as e:
            logger.error(f"✗ Test {test.__name__} crashed: {e}")
    
    logger.info(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Basic structure is working.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())