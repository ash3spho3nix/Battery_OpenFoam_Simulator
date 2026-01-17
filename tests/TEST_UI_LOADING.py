#!/usr/bin/env python3
"""
Test script for UI loading functionality.

This script tests the basic UI loading capabilities.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from src.gui.ui_loader import UILoader
from src.gui.ui_config import UIConfig


def test_ui_loader():
    """Test the UI loader functionality."""
    print("Testing UI Loader...")
    
    # Test individual file existence
    for ui_name in ["mainwindow", "carboninterface", "halfcellinterface", "fullcellfoam", "resultinterface"]:
        exists = UILoader.ui_file_exists(ui_name)
        print(f"  {ui_name}.ui exists: {exists}")
    
    print("UI Loader test completed.\n")


def test_ui_config():
    """Test the UI configuration functionality."""
    print("Testing UI Configuration...")
    
    # Test default configuration
    config = UIConfig()
    print(f"Default config: {config}")
    
    print("UI Configuration test completed.\n")


def test_main_window_loading():
    """Test loading main window from .ui file."""
    print("Testing Main Window Loading...")
    
    try:
        # Try to load main window from .ui file
        main_window = UILoader.load_main_window()
        print(f"Successfully loaded main window from .ui file: {type(main_window)}")
        print(f"Window title: {main_window.windowTitle()}")
        print(f"Window size: {main_window.size()}")
        return True
    except Exception as e:
        print(f"Failed to load main window from .ui file: {e}")
        return False


def test_carbon_interface_loading():
    """Test loading carbon interface from .ui file."""
    print("Testing Carbon Interface Loading...")
    
    try:
        # Try to load carbon interface from .ui file
        carbon_interface = UILoader.load_carbon_interface()
        print(f"Successfully loaded carbon interface from .ui file: {type(carbon_interface)}")
        return True
    except Exception as e:
        print(f"Failed to load carbon interface from .ui file: {e}")
        return False


def main():
    """Main test function."""
    print("Battery Simulator UI Loading Test")
    print("=" * 40)
    print()
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Run tests
    test_ui_loader()
    test_ui_config()
    
    # Test .ui file loading
    main_window_success = test_main_window_loading()
    carbon_interface_success = test_carbon_interface_loading()
    
    print("=" * 40)
    print("Test Summary:")
    print(f"Main Window .ui loading: {'✓' if main_window_success else '✗'}")
    print(f"Carbon Interface .ui loading: {'✓' if carbon_interface_success else '✗'}")
    print()
    
    if main_window_success and carbon_interface_success:
        print("All .ui file loading tests passed! ✓")
    else:
        print("Some .ui file loading tests failed. ✗")
        print("This might be expected if the .ui files have compatibility issues.")
    
    print()
    print("To test different UI modes, run:")
    print("  python test_ui_loading.py")
    print("  BATTERY_SIM_UI_MODE=ui_files python test_ui_loading.py")
    print("  BATTERY_SIM_UI_MODE=hand_coded python test_ui_loading.py")
    print("  BATTERY_SIM_UI_MODE=auto python test_ui_loading.py")


if __name__ == "__main__":
    main()
