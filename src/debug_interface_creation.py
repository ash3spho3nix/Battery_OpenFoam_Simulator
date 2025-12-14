#!/usr/bin/env python3
"""
Diagnostic script for interface creation issues.

This script helps diagnose issues with the 'Next' button crash by testing
the interface creation process step by step.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))

# Set up logging with ASCII-only characters
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('interface_creation_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports."""
    logger.info("Testing imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        logger.info("OK - PyQt6 imported successfully")
    except Exception as e:
        logger.error(f"ERROR - PyQt6 import failed: {e}")
        return False
    
    try:
        from src.gui.ui_config import UIConfig
        logger.info("OK - UIConfig imported successfully")
    except Exception as e:
        logger.error(f"ERROR - UIConfig import failed: {e}")
        return False
    
    try:
        from src.gui.interface_factory import InterfaceFactory
        logger.info("OK - InterfaceFactory imported successfully")
    except Exception as e:
        logger.error(f"ERROR - InterfaceFactory import failed: {e}")
        return False
    
    try:
        from src.gui.interfaces.carbon_interface import CarbonInterface
        logger.info("OK - CarbonInterface imported successfully")
    except Exception as e:
        logger.error(f"ERROR - CarbonInterface import failed: {e}")
        return False
    
    try:
        from src.core.project_manager import ProjectManager
        logger.info("OK - ProjectManager imported successfully")
    except Exception as e:
        logger.error(f"ERROR - ProjectManager import failed: {e}")
        return False
    
    return True

def test_ui_config():
    """Test UI configuration."""
    logger.info("Testing UI configuration...")
    
    try:
        from src.gui.ui_config import UIConfig, UILoadingMode
        
        config = UIConfig()
        logger.info(f"OK - UIConfig created: {config}")
        logger.info(f"  Mode: {config.mode}")
        logger.info(f"  Should load UI files: {config.should_load_ui_files()}")
        logger.info(f"  Should fallback: {config.should_fallback_to_hand_coded()}")
        
        return True
    except Exception as e:
        logger.error(f"ERROR - UIConfig test failed: {e}")
        return False

def test_interface_factory():
    """Test interface factory."""
    logger.info("Testing InterfaceFactory...")
    
    try:
        from src.gui.interface_factory import InterfaceFactory
        from src.gui.ui_config import UIConfig
        
        factory = InterfaceFactory
        config = UIConfig()
        
        # Test diagnosis
        logger.info("Running interface creation diagnosis...")
        diagnosis = factory.diagnose_interface_creation("carbon", config)
        
        logger.info(f"Diagnosis results: {diagnosis}")
        
        return True
    except Exception as e:
        logger.error(f"ERROR - InterfaceFactory test failed: {e}", exc_info=True)
        return False

def test_project_manager():
    """Test project manager creation."""
    logger.info("Testing ProjectManager creation...")
    
    try:
        from src.core.project_manager import ProjectManager
        from src.core.constants import DEFAULT_PROJECT_PATH
        
        base_projects_path = Path(DEFAULT_PROJECT_PATH)
        logger.info(f"Creating ProjectManager with path: {base_projects_path}")
        
        pm = ProjectManager(base_projects_path)
        logger.info("OK - ProjectManager created successfully")
        
        return True
    except Exception as e:
        logger.error(f"ERROR - ProjectManager test failed: {e}", exc_info=True)
        return False

def test_carbon_interface_creation():
    """Test CarbonInterface creation."""
    logger.info("Testing CarbonInterface creation...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.interfaces.carbon_interface import CarbonInterface
        from src.gui.ui_config import UIConfig
        
        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        config = UIConfig()
        logger.info("Creating CarbonInterface...")
        
        interface = CarbonInterface(None, config)
        logger.info("OK - CarbonInterface created successfully")
        logger.info(f"Interface type: {type(interface)}")
        logger.info(f"Interface title: {interface.windowTitle()}")
        
        return True
    except Exception as e:
        logger.error(f"ERROR - CarbonInterface creation failed: {e}", exc_info=True)
        return False

def main():
    """Run all diagnostic tests."""
    logger.info("Starting interface creation diagnostics...")
    
    tests = [
        ("Imports", test_imports),
        ("UI Configuration", test_ui_config),
        ("Interface Factory", test_interface_factory),
        ("Project Manager", test_project_manager),
        ("Carbon Interface Creation", test_carbon_interface_creation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            logger.info(f"Test {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}", exc_info=True)
            results[test_name] = False
    
    logger.info(f"\n{'='*50}")
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    logger.info(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        logger.info("OK - All tests passed! The interface creation should work.")
    else:
        logger.error("ERROR - Some tests failed. Check the logs above for details.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)