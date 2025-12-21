#!/usr/bin/env python3
"""
Test script for Battery Simulator Python application.

This script tests the application with different UI loading modes and validates
OpenFOAM integration. It can be run independently to verify the fixes.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test all import statements to ensure no packaging issues."""
    print("Testing imports...")
    try:
        # Test core imports
        from src.core.constants import APP_NAME, APP_VERSION, UI_WIDGET_NAMES
        print(f"✓ Core constants imported: {APP_NAME} v{APP_VERSION}")
        
        # Test GUI imports
        from src.gui.main_window import MainWindow
        from src.gui.ui_config import UIConfig, UILoadingMode
        from src.gui.ui_loader import UILoader
        from src.gui.interface_factory import InterfaceFactory
        print("✓ GUI modules imported successfully")
        
        # Test interface imports
        from src.gui.interfaces.base_interface import BaseInterface
        from src.gui.interfaces.carbon_interface import CarbonInterface
        from src.gui.interfaces.halfcell_interface import HalfCellInterface
        from src.gui.interfaces.fullcell_interface import FullCellInterface
        from src.gui.interfaces.result_interface import ResultInterface
        print("✓ Interface modules imported successfully")
        
        # Test utility imports
        from src.utils.debug_utils import OpenFOAMDebugger, validate_openfoam_installation
        print("✓ Utility modules imported successfully")
        
        assert True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        assert False

def test_ui_loading_modes():
    """Test different UI loading modes."""
    print("\nTesting UI loading modes...")
    try:
        from src.gui.ui_config import UIConfig, UILoadingMode
        from src.gui.ui_loader import UILoader
        
        # Test UI_FILES mode
        ui_config_ui_files = UIConfig()
        ui_config_ui_files.set_mode(UILoadingMode.UI_FILES)
        assert ui_config_ui_files.should_load_ui_files()
        print(f"✓ UI_FILES mode configured: {ui_config_ui_files.should_load_ui_files()}")
        
        # Test HAND_CODED mode
        ui_config_hand_coded = UIConfig()
        ui_config_hand_coded.set_mode(UILoadingMode.HAND_CODED)
        assert not ui_config_hand_coded.should_load_ui_files()
        print(f"✓ HAND_CODED mode configured: {not ui_config_hand_coded.should_load_ui_files()}")
        
        # Test AUTO_DETECT mode
        ui_config_auto = UIConfig()
        ui_config_auto.set_mode(UILoadingMode.AUTO_DETECT)
        print(f"✓ AUTO_DETECT mode configured: {ui_config_auto.should_load_ui_files()}")
        
        # Test UI file existence
        ui_files_path = Path(__file__).parent.parent / "src" / "resources" / "ui"
        ui_files_exist = UILoader.ui_file_exists("mainwindow", str(ui_files_path))
        assert ui_files_exist
        print(f"✓ UI files exist: {ui_files_exist}")
        
    except Exception as e:
        print(f"✗ UI loading mode test failed: {e}")
        assert False

def test_openfoam_integration():
    """Test OpenFOAM integration and debugging utilities."""
    print("\nTesting OpenFOAM integration...")
    try:
        from src.utils.debug_utils import (
            OpenFOAMDebugger, 
            validate_openfoam_installation, 
            check_solver_availability
        )
        
        # Test OpenFOAM installation validation
        openfoam_valid = validate_openfoam_installation()
        assert openfoam_valid
        print(f"✓ OpenFOAM installation valid: {openfoam_valid}")
        
        # Test solver availability
        solver_status = check_solver_availability()
        assert solver_status
        print(f"✓ Solver availability: {solver_status}")
        
        # Test debugger initialization
        debugger = OpenFOAMDebugger()
        assert debugger is not None
        print("✓ OpenFOAM debugger initialized")
        
    except Exception as e:
        print(f"✗ OpenFOAM integration test failed: {e}")
        assert False

def test_constants_and_ui_values():
    """Test that hardcoded values from .ui files are properly loaded."""
    print("\nTesting constants and UI values...")
    try:
        from src.core.constants import UI_WIDGET_NAMES, UI_TAB_TITLES, UI_DEFAULT_VALUES
        
        # Test widget names
        main_window_widgets = UI_WIDGET_NAMES.get("main_window", {})
        carbon_interface_widgets = UI_WIDGET_NAMES.get("carbon_interface", {})
        assert main_window_widgets
        assert carbon_interface_widgets
        print(f"✓ Main window widgets: {len(main_window_widgets)} items")
        print(f"✓ Carbon interface widgets: {len(carbon_interface_widgets)} items")
        
        # Test tab titles
        main_window_tabs = UI_TAB_TITLES.get("main_window", {})
        carbon_interface_tabs = UI_TAB_TITLES.get("carbon_interface", {})
        assert main_window_tabs
        assert carbon_interface_tabs
        print(f"✓ Main window tabs: {list(main_window_tabs.values())}")
        print(f"✓ Carbon interface tabs: {list(carbon_interface_tabs.values())}")
        
        # Test default values
        main_window_defaults = UI_DEFAULT_VALUES.get("main_window", {})
        carbon_interface_defaults = UI_DEFAULT_VALUES.get("carbon_interface", {})
        assert main_window_defaults
        assert carbon_interface_defaults
        print(f"✓ Main window defaults: {main_window_defaults}")
        print(f"✓ Carbon interface defaults: {carbon_interface_defaults}")
        
    except Exception as e:
        print(f"✗ Constants and UI values test failed: {e}")
        assert False

def test_application_initialization(qtbot):
    """Test application initialization with different configurations."""
    print("\nTesting application initialization...")
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.main_window import MainWindow
        from src.gui.ui_config import UIConfig, UILoadingMode
        
        # Create Qt application (headless)
        app = QApplication.instance() or QApplication(sys.argv)
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
                qtbot.addWidget(window)
                print(f"✓ {config_name} mode: MainWindow created successfully")
                window.close()
            except Exception as e:
                print(f"✗ {config_name} mode failed: {e}")
                assert False
        
    except Exception as e:
        print(f"✗ Application initialization test failed: {e}")
        assert False


