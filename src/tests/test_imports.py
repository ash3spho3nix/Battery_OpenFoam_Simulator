#!/usr/bin/env python3
"""
Test script to verify that circular imports are fixed and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

def test_imports():
    """Test that all modules can be imported without circular import errors."""
    print("Testing imports...")
    
    try:
        # Test core imports
        print("  - Testing core constants...")
        from src.core.constants import APP_NAME, APP_VERSION
        print(f"    ✓ APP_NAME: {APP_NAME}, APP_VERSION: {APP_VERSION}")
        
        print("  - Testing core application...")
        from src.core.application import BatterySimulatorApp
        print("    ✓ BatterySimulatorApp imported successfully")
        
        print(" . - Testing core project manager...")
        from src.core.project_manager import ProjectManager
        print("    ✓ ProjectManager imported successfully")
        
        # Test GUI imports
        print("  - Testing GUI main window...")
        from src.gui.main_window import MainWindow
        print("    ✓ MainWindow imported successfully")
        
        print("  - Testing GUI interface factory...")
        from src.gui.interface_factory import InterfaceFactory
        print("    ✓ InterfaceFactory imported successfully")
        
        print("  - Testing GUI base interface...")
        from src.gui.interfaces.base_interface import BaseInterface
        print("    ✓ BaseInterface imported successfully")
        
        # Test utils imports
        print("  - Testing utils parameter parser...")
        from src.utils.parameter_parser import ParameterManager
        print("    ✓ ParameterManager imported successfully")
        
        print("  - Testing utils file operations...")
        from src.utils.file_operations import TemplateManager
        print("    ✓ TemplateManager imported successfully")
        
        # Test OpenFOAM imports
        print("  - Testing OpenFOAM process controller...")
        from src.openfoam.process_controller import ProcessController
        print("    ✓ ProcessController imported successfully")
        
        print("  - Testing OpenFOAM solver manager...")
        from src.openfoam.solver_manager import OpenFOAMSolverManager
        print("    ✓ OpenFOAMSolverManager imported successfully")
        
        print("\n✅ All imports successful! No circular import issues detected.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\nTesting basic functionality...")
    
    try:
        # Test constants
        from src.core.constants import SUPPORTED_MODULES, SOLVER_NAMES
        print(f"  - Supported modules: {list(SUPPORTED_MODULES.keys())}")
        print(f"  - Solver names: {list(SOLVER_NAMES.keys())}")
        
        # Test project manager
        from src.core.project_manager import ProjectManager
        pm = ProjectManager()
        templates = pm.list_available_templates()
        print(f"  - Available templates: {list(templates.keys())}")
        
        print("\n✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test error: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("BATTERY SIMULATOR IMPORT AND FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test imports
    import_success = test_imports()
    
    # Test basic functionality
    if import_success:
        functionality_success = test_basic_functionality()
    else:
        functionality_success = False
    
    print("\n" + "=" * 60)
    if import_success and functionality_success:
        print("🎉 ALL TESTS PASSED! The circular import issues have been fixed.")
        print("   You can now run the main application:")
        print("   python src/main.py")
    else:
        print("❌ SOME TESTS FAILED. Please check the errors above.")
    print("=" * 60)
    
    return import_success and functionality_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)