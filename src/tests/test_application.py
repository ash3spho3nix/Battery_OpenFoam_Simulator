#!/usr/bin/env python3
"""
Test script for Battery Simulator Python application.

This script tests the application with different UI loading modes and validates
OpenFOAM integration. It can be run independently to verify the fixes.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the src_py directory to Python path for imports
current_dir = Path(__file__).parent
src_py_path = current_dir / "src_py"
sys.path.insert(0, str(src_py_path))

def test_imports():
    """Test all import statements to ensure no packaging issues."""
    print("Testing imports...")
    try:
        # Test core imports
        from src_py.core.constants import APP_NAME, APP_VERSION, UI_WIDGET_NAMES
        print(f"✓ Core constants imported: {APP_NAME} v{APP_VERSION}")
        
        # Test GUI imports
        from src_py.gui.main_window import MainWindow
        from src_py.gui.ui_config import UIConfig, UILoadingMode
        from src_py.gui.ui_loader import UILoader
        from src_py.gui.interface_factory import InterfaceFactory
        print("✓ GUI modules imported successfully")
        
        # Test interface imports
        from src_py.gui.interfaces.base_interface import BaseInterface
        from src_py.gui.interfaces.carbon_interface import CarbonInterface
        from src_py.gui.interfaces.halfcell_interface import HalfCellInterface
        from src_py.gui.interfaces.fullcell_interface import FullCellInterface
        from src_py.gui.interfaces.result_interface import ResultInterface
        print("✓ Interface modules imported successfully")
        
        # Test utility imports
        from src_py.utils.debug_utils import OpenFOAMDebugger, validate_openfoam_installation
        print("✓ Utility modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_ui_loading_modes():
    """Test different UI loading modes."""
    print("\nTesting UI loading modes...")
    try:
        from src_py.gui.ui_config import UIConfig, UILoadingMode
        from src_py.gui.ui_loader import UILoader
        
        # Test UI_FILES mode
        ui_config_ui_files = UIConfig()
        ui_config_ui_files.set_mode(UILoadingMode.UI_FILES)
        print(f"✓ UI_FILES mode configured: {ui_config_ui_files.should_load_ui_files()}")
        
        # Test HAND_CODED mode
        ui_config_hand_coded = UIConfig()
        ui_config_hand_coded.set_mode(UILoadingMode.HAND_CODED)
        print(f"✓ HAND_CODED mode configured: {ui_config_hand_coded.should_load_ui_files()}")
        
        # Test AUTO_DETECT mode
        ui_config_auto = UIConfig()
        ui_config_auto.set_mode(UILoadingMode.AUTO_DETECT)
        print(f"✓ AUTO_DETECT mode configured: {ui_config_auto.should_load_ui_files()}")
        
        # Test UI file existence
        ui_files_path = src_py_path.parent / "src_py" / "resources" / "ui"
        ui_files_exist = UILoader.ui_file_exists("mainwindow", str(ui_files_path))
        print(f"✓ UI files exist: {ui_files_exist}")
        
        return True
    except Exception as e:
        print(f"✗ UI loading mode test failed: {e}")
        return False

def test_openfoam_integration():
    """Test OpenFOAM integration and debugging utilities."""
    print("\nTesting OpenFOAM integration...")
    try:
        from src_py.utils.debug_utils import (
            OpenFOAMDebugger, 
            validate_openfoam_installation, 
            check_solver_availability
        )
        
        # Test OpenFOAM installation validation
        openfoam_valid = validate_openfoam_installation()
        print(f"✓ OpenFOAM installation valid: {openfoam_valid}")
        
        # Test solver availability
        solver_status = check_solver_availability()
        print(f"✓ Solver availability: {solver_status}")
        
        # Test debugger initialization
        debugger = OpenFOAMDebugger()
        print("✓ OpenFOAM debugger initialized")
        
        return True
    except Exception as e:
        print(f"✗ OpenFOAM integration test failed: {e}")
        return False

def test_constants_and_ui_values():
    """Test that hardcoded values from .ui files are properly loaded."""
    print("\nTesting constants and UI values...")
    try:
        from src_py.core.constants import UI_WIDGET_NAMES, UI_TAB_TITLES, UI_DEFAULT_VALUES
        
        # Test widget names
        main_window_widgets = UI_WIDGET_NAMES.get("main_window", {})
        carbon_interface_widgets = UI_WIDGET_NAMES.get("carbon_interface", {})
        print(f"✓ Main window widgets: {len(main_window_widgets)} items")
        print(f"✓ Carbon interface widgets: {len(carbon_interface_widgets)} items")
        
        # Test tab titles
        main_window_tabs = UI_TAB_TITLES.get("main_window", {})
        carbon_interface_tabs = UI_TAB_TITLES.get("carbon_interface", {})
        print(f"✓ Main window tabs: {list(main_window_tabs.values())}")
        print(f"✓ Carbon interface tabs: {list(carbon_interface_tabs.values())}")
        
        # Test default values
        main_window_defaults = UI_DEFAULT_VALUES.get("main_window", {})
        carbon_interface_defaults = UI_DEFAULT_VALUES.get("carbon_interface", {})
        print(f"✓ Main window defaults: {main_window_defaults}")
        print(f"✓ Carbon interface defaults: {carbon_interface_defaults}")
        
        return True
    except Exception as e:
        print(f"✗ Constants and UI values test failed: {e}")
        return False

def test_application_initialization():
    """Test application initialization with different configurations."""
    print("\nTesting application initialization...")
    try:
        from PyQt6.QtWidgets import QApplication
        from src_py.gui.main_window import MainWindow
        from src_py.gui.ui_config import UIConfig, UILoadingMode
        
        # Create Qt application (headless)
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Test different UI configurations
        test_configs = [
            ("UI_FILES", UILoadingMode.UI_FILES),
            ("HAND_CODED", UILoadingMode.HAND_CODED),
            ("AUTO_DETECT", UILoadingMode.AUTO_DETECT)
        ]
        
        for config_name, mode in test_configs:
            ui_config = UIConfig()
            ui_config.set_mode(mode)
            ui_config.set_fallback_enabled(True)
            
            try:
                window = MainWindow(ui_config=ui_config)
                print(f"✓ {config_name} mode: MainWindow created successfully")
                window.close()
            except Exception as e:
                print(f"✗ {config_name} mode failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Application initialization test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and generate a report."""
    print("=" * 80)
    print("BATTERY SIMULATOR PYTHON APPLICATION - COMPREHENSIVE TEST")
    print("=" * 80)
    
    test_results = {}
    
    # Run all tests
    test_results['imports'] = test_imports()
    test_results['ui_loading'] = test_ui_loading_modes()
    test_results['openfoam'] = test_openfoam_integration()
    test_results['constants'] = test_constants_and_ui_values()
    test_results['initialization'] = test_application_initialization()
    
    # Generate report
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.upper()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application should now run without import errors.")
        print("\nTo run the application, use:")
        print("  python src_py/main.py")
        print("\nTo test with specific UI mode:")
        print("  python src_py/main.py --ui-mode ui_files")
        print("  python src_py/main.py --ui-mode hand_coded")
        print("  python src_py/main.py --ui-mode auto")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return passed == total

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test Battery Simulator Python application")
    parser.add_argument('--test', choices=['all', 'imports', 'ui', 'openfoam', 'constants', 'init'], 
                       default='all', help='Specific test to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script location: {__file__}")
        print(f"Source path: {src_py_path}")
    
    if args.test == 'all':
        success = run_comprehensive_test()
    elif args.test == 'imports':
        success = test_imports()
    elif args.test == 'ui':
        success = test_ui_loading_modes()
    elif args.test == 'openfoam':
        success = test_openfoam_integration()
    elif args.test == 'constants':
        success = test_constants_and_ui_values()
    elif args.test == 'init':
        success = test_application_initialization()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()