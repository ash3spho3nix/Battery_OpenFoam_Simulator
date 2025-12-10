#!/usr/bin/env python3
"""
Simple test for UI file existence without PyQt6 initialization.
"""

import sys
from pathlib import Path

def test_ui_file_existence():
    """Test if UI files exist in the correct location."""
    print("Testing UI file existence...")
    
    # Construct the path to the .ui file
    ui_file_path = Path(__file__).parent / "src" / "resources" / "ui" / "files" / "mainwindow.ui"
    
    print(f"Looking for UI file at: {ui_file_path}")
    
    if ui_file_path.exists():
        print(f'UI file exists: {ui_file_path}')
        print(f'File size: {ui_file_path.stat().st_size} bytes')
        return True
    else:
        print(f'UI file not found: {ui_file_path}')
        return False

if __name__ == "__main__":
    success = test_ui_file_existence()
    sys.exit(0 if success else 1)