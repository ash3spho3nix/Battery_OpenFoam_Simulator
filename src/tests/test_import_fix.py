#!/usr/bin/env python3
"""
Simple test script to verify the import fix without Unicode characters.
This test validates that the circular import issue has been resolved.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing Python module imports...")
    print("=" * 50)
    
    modules_to_test = [
        'src.gui.main_window',
        'src.gui.interface_factory', 
        'src.gui.interfaces.base_interface',
        'src.gui.interfaces.carbon_interface',
        'src.gui.interfaces.halfcell_interface',
        'src.gui.interfaces.fullcell_interface',
        'src.gui.interfaces.result_interface',
        'src.openfoam.process_controller',
        'src.openfoam.solver_manager',
        'src.utils.parameter_parser',
        'src.utils.file_operations',
        'src.core.constants',
        'src.main'
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"OK: {module_name}")
            success_count += 1
        except Exception as e:
            print(f"FAILED: {module_name} - {e}")
    
    print("=" * 50)
    print(f"Import test results: {success_count}/{total_count} modules imported successfully")
    
    if success_count == total_count:
        print("SUCCESS: All modules imported without errors!")
        print("The circular import issue has been resolved.")
        return True
    else:
        print(f"FAILURE: {total_count - success_count} modules failed to import.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
