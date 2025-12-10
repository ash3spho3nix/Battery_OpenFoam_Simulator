#!/usr/bin/env python3
"""
Debug script to test ProjectManager instantiation.
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

def test_project_manager_instantiation():
    """Test ProjectManager instantiation with and without arguments."""
    
    print("=== Testing ProjectManager Instantiation ===")
    
    try:
        # Test 1: Try to import ProjectManager
        print("1. Importing ProjectManager...")
        from core.project_manager import ProjectManager
        print("   ✓ ProjectManager imported successfully")
        
        # Test 2: Try instantiation without arguments (current MainWindow approach)
        print("2. Testing ProjectManager() without arguments...")
        try:
            pm = ProjectManager()
            print("   ✓ ProjectManager() worked (unexpected)")
        except TypeError as e:
            print(f"   ✗ ProjectManager() failed: {e}")
            
        # Test 3: Try instantiation with arguments
        print("3. Testing ProjectManager() with base_projects_path...")
        try:
            test_path = Path(__file__).parent / "test_projects"
            pm = ProjectManager(test_path)
            print(f"   ✓ ProjectManager({test_path}) worked")
            print(f"   ✓ ProjectManager.base_projects_path = {pm.base_projects_path}")
        except Exception as e:
            print(f"   ✗ ProjectManager with args failed: {e}")
            
        # Test 4: Check if UIConfig import works
        print("4. Testing UIConfig import...")
        try:
            from gui.ui_config import UIConfig
            print("   ✓ UIConfig imported successfully")
        except Exception as e:
            print(f"   ✗ UIConfig import failed: {e}")
            
    except Exception as e:
        print(f"Failed to import ProjectManager: {e}")
        return False
        
    return True

if __name__ == "__main__":
    test_project_manager_instantiation()