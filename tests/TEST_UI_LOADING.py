#!/usr/bin/env python3
"""
Test script to validate UI loading functionality.
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_ui_loader():
    """Test the enhanced UI loader functionality."""
    print("=" * 60)
    print("UI LOADING DIAGNOSTIC TEST")
    print("=" * 60)
    
    try:
        # Test 1: Import the UI loader
        print("\n1. Testing UI loader import...")
        from src.gui.ui_loader import UILoader
        print("OK - UI loader imported successfully")
        
        # Test 2: Check if UI files exist
        print("\n2. Checking UI file paths...")
        from src.core.constants import UI_FILES_PATH
        print(f"UI_FILES_PATH: {UI_FILES_PATH}")
        
        ui_files = [
            "carboninterface.ui",
            "halfcellinterface.ui", 
            "fullcellfoam.ui",
            "mainwindow.ui",
            "resultinterface.ui"
        ]
        
        for ui_file in ui_files:
            ui_path = UILoader.get_ui_path(ui_file)
            exists = os.path.exists(ui_path)
            print(f"  {ui_file}: {'OK' if exists else 'MISSING'} {ui_path}")
        
        # Test 3: Test UI file validation
        print("\n3. Testing UI file validation...")
        for ui_file in ui_files:
            ui_path = UILoader.get_ui_path(ui_file)
            if os.path.exists(ui_path):
                is_valid = UILoader.validate_ui_integrity(ui_path)
                print(f"  {ui_file} integrity: {'OK' if is_valid else 'INVALID'}")
        
        # Test 4: Test loading main window
        print("\n4. Testing main window loading...")
        try:
            main_window = UILoader.load_main_window()
            if main_window:
                print("OK - Main window loaded successfully")
                # Check if tabWidget exists
                tab_widget = main_window.findChild(QWidget, "tabWidget")
                if tab_widget:
                    print("OK - tabWidget found in main window")
                else:
                    print("ERROR - tabWidget NOT found in main window")
                    # List all widgets
                    all_widgets = main_window.findChildren(QWidget)
                    print(f"  Found {len(all_widgets)} widgets:")
                    for widget in all_widgets[:10]:  # Show first 10
                        print(f"    - {widget.objectName()} ({type(widget).__name__})")
            else:
                print("ERROR - Main window loading failed")
        except Exception as e:
            print(f"ERROR - Main window loading error: {e}")
        
        # Test 5: Test loading carbon interface
        print("\n5. Testing carbon interface loading...")
        try:
            carbon_interface = UILoader.load_carbon_interface()
            if carbon_interface:
                print("OK - Carbon interface loaded successfully")
                # Check if tabWidget exists
                tab_widget = carbon_interface.findChild(QWidget, "tabWidget")
                if tab_widget:
                    print("OK - tabWidget found in carbon interface")
                else:
                    print("ERROR - tabWidget NOT found in carbon interface")
                    # List all widgets
                    all_widgets = carbon_interface.findChildren(QWidget)
                    print(f"  Found {len(all_widgets)} widgets:")
                    for widget in all_widgets[:10]:  # Show first 10
                        print(f"    - {widget.objectName()} ({type(widget).__name__})")
            else:
                print("ERROR - Carbon interface loading failed")
        except Exception as e:
            print(f"ERROR - Carbon interface loading error: {e}")
        
        print("\n" + "=" * 60)
        print("UI LOADING TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\nERROR - Test failed with error: {e}")

if __name__ == "__main__":
    test_ui_loader()