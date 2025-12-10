#!/usr/bin/env python3
"""
Simple test script to validate UI loading functionality without GUI display.
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_ui_paths():
    """Test that UI paths are correctly resolved."""
    print("=" * 60)
    print("UI PATH RESOLUTION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Import constants
        print("\n1. Testing constants import...")
        from src.core.constants import UI_FILES_PATH
        print(f"OK - UI_FILES_PATH: {UI_FILES_PATH}")
        
        # Test 2: Import UI loader
        print("\n2. Testing UI loader import...")
        from src.gui.ui_loader import UILoader
        print("OK - UI loader imported successfully")
        
        # Test 3: Check if UI files exist
        print("\n3. Checking UI file paths...")
        ui_files = [
            "carboninterface.ui",
            "halfcellinterface.ui", 
            "fullcellfoam.ui",
            "mainwindow.ui",
            "resultinterface.ui"
        ]
        
        all_files_exist = True
        for ui_file in ui_files:
            ui_path = UILoader.get_ui_path(ui_file)
            exists = os.path.exists(ui_path)
            status = "OK" if exists else "MISSING"
            print(f"  {ui_file}: {status} {ui_path}")
            if not exists:
                all_files_exist = False
        
        if all_files_exist:
            print("\n✓ All UI files found!")
        else:
            print("\n✗ Some UI files are missing!")
        
        # Test 4: Test UI file validation
        print("\n4. Testing UI file validation...")
        for ui_file in ui_files:
            ui_path = UILoader.get_ui_path(ui_file)
            if os.path.exists(ui_path):
                try:
                    is_valid = UILoader.validate_ui_integrity(ui_path)
                    status = "OK" if is_valid else "INVALID"
                    print(f"  {ui_file} integrity: {status}")
                except Exception as e:
                    print(f"  {ui_file} integrity: ERROR - {e}")
        
        print("\n" + "=" * 60)
        print("UI PATH TEST COMPLETE")
        print("=" * 60)
        
        return all_files_exist
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\nERROR - Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_ui_paths()
    sys.exit(0 if success else 1)