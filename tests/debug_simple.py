#!/usr/bin/env python3
"""
Simple debug script to test the main issue.
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

def test_main_window_instantiation():
    """Test MainWindow instantiation to reproduce the error."""
    
    print("=== Testing MainWindow Instantiation ===")
    
    try:
        # Test 1: Import MainWindow
        print("1. Importing MainWindow...")
        from gui.main_window import MainWindow
        print("   MainWindow imported successfully")
        
        # Test 2: Try to instantiate MainWindow (this should fail)
        print("2. Testing MainWindow() instantiation...")
        try:
            window = MainWindow()
            print("   MainWindow() worked (unexpected)")
        except Exception as e:
            print(f"   MainWindow() failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
        # Test 3: Check ProjectManager signature
        print("3. Checking ProjectManager signature...")
        from core.project_manager import ProjectManager
        import inspect
        sig = inspect.signature(ProjectManager.__init__)
        print(f"   ProjectManager.__init__ signature: {sig}")
        
    except Exception as e:
        print(f"Failed to import: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_main_window_instantiation()