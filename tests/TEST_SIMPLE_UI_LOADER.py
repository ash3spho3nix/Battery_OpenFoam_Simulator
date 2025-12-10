#!/usr/bin/env python3
"""
Simple test for the UI loader without circular imports.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import just the UI loader directly
from gui.ui_loader import UiLoader

def test_ui_loader():
    """Test the UI loader."""
    print("Testing UI loader...")
    
    # Test loading a UI
    widget = UiLoader.load_ui('mainwindow')
    if widget:
        print('UI loaded successfully')
        return True
    else:
        print('Failed to load UI')
        return False

if __name__ == "__main__":
    success = test_ui_loader()
    sys.exit(0 if success else 1)