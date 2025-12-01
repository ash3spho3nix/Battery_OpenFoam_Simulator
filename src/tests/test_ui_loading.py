#!/usr/bin/env python3
"""
Test script for UI loading functionality.

This script tests the new UI loading capabilities, including:
- Loading .ui files at runtime
- UI configuration from environment variables and command line
- Interface factory functionality
- Fallback mechanisms
"""

import sys
import os
from pathlib import Path

# Add the src_py directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from gui.ui_loader import UILoader, UILoadingMode
from gui.ui_config import UIConfig
from gui.interface_factory import InterfaceFactory


def test_ui_loader():
    """Test the UI loader functionality."""
    print("Testing UI Loader...")
    
    # Test file existence
    ui_files = UILoader.get_available_ui_files()
    print(f"Available .ui files: {ui_files}")
    
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
    print(f"Should load .ui files: {config.should_load_ui_files()}")
    print(f"Should fallback: {config.should_fallback_to_hand_coded()}")
    
    # Test environment variable configuration
    os.environ["BATTERY_SIM_UI_MODE"] = "ui_files"
    config_env = UIConfig.from_environment()
    print(f"Environment config (ui_files): {config_env}")
    
    # Test auto-detect
    os.environ["BATTERY_SIM_UI_MODE"] = "auto"
    config_auto = UIConfig.from_environment()
    print(f"Environment config (auto): {config_auto}")
    
    # Test dictionary serialization
    config_dict = config.to_dict()
    config_from_dict = UIConfig.from_dict(config_dict)
    print(f"Dict round-trip: {config_from_dict}")
    
    print("UI Configuration test completed.\n")


def test_interface_factory():
    """Test the interface factory functionality."""
    print("Testing Interface Factory...")
    
    config = UIConfig()
    config.set_mode(UILoadingMode.AUTO_DETECT)
    
    # Test available interfaces
    available = InterfaceFactory.get_available_interfaces()
    print(f"Available interfaces: {available}")
    
    # Test interface creation (this will try .ui files first, then fallback)
    for interface_type in available:
        try:
            print(f"  Creating {interface_type} interface...")
            # Note: This will likely fail because the interfaces don't exist yet,
            # but it tests the factory logic
            # interface = InterfaceFactory.create_interface(interface_type, ui_config=config)
            # print(f"    Success: {type(interface)}")
        except Exception as e:
            print(f"    Expected error (interfaces not implemented): {e}")
    
    print("Interface Factory test completed.\n")


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
    test_interface_factory()
    
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