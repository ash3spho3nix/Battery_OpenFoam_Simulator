#!/usr/bin/env python3
"""
Test script to validate circular import fixes.

This script tests the import chain to ensure no circular dependencies exist.
"""

import sys
import logging
from pathlib import Path

# Set up logging to see the import order
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to Python path for imports
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def test_import_chain():
    """Test the import chain to detect circular imports."""
    print("Testing import chain for circular dependencies...")
    print("=" * 60)
    
    try:
        # Test 1: Import interface_factory directly
        print("1. Testing interface_factory import...")
        from src.gui.interface_factory import InterfaceFactory
        print("   ✓ interface_factory imported successfully")
        
        # Test 2: Import main_window directly
        print("2. Testing main_window import...")
        from src.gui.main_window import MainWindow
        print("   ✓ main_window imported successfully")
        
        # Test 3: Test InterfaceFactory.create_main_window method
        print("3. Testing InterfaceFactory.create_main_window method...")
        from src.gui.ui_config import UIConfig
        ui_config = UIConfig()
        ui_config.set_mode("hand_coded")  # Force hand-coded mode to avoid .ui file issues
        
        # This should trigger the import inside the method
        main_window = InterfaceFactory.create_main_window(ui_config)
        print("   ✓ InterfaceFactory.create_main_window() executed successfully")
        main_window.close()  # Clean up
        
        # Test 4: Test MainWindow initialization
        print("4. Testing MainWindow initialization...")
        main_window2 = MainWindow(ui_config=ui_config)
        print("   ✓ MainWindow initialized successfully")
        main_window2.close()  # Clean up
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - No circular imports detected!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("This indicates a circular import or missing dependency.")
        return False
    except Exception as e:
        print(f"\n❌ RUNTIME ERROR: {e}")
        print("This indicates an issue with the circular import fix.")
        return False

def test_individual_modules():
    """Test individual module imports to isolate issues."""
    print("\nTesting individual module imports...")
    print("-" * 40)
    
    modules_to_test = [
        "src.gui.ui_loader",
        "src.gui.ui_config", 
        "src.gui.interface_factory",
        "src.gui.main_window",
        "src.core.application"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
            return False
    
    print("✅ All individual modules imported successfully")
    return True

if __name__ == "__main__":
    print("CIRCULAR IMPORT VALIDATION TEST")
    print("=" * 60)
    print("This test validates that the circular import issue has been fixed.")
    print("If successful, the application should run without import errors.")
    print()
    
    # Test individual modules first
    individual_success = test_individual_modules()
    
    # Test the full import chain
    chain_success = test_import_chain()
    
    print("\nFINAL RESULTS:")
    print("=" * 60)
    if individual_success and chain_success:
        print("🎉 SUCCESS: Circular import issue has been resolved!")
        print("\nYou can now run the application with:")
        print("  python src/main.py")
        sys.exit(0)
    else:
        print("❌ FAILURE: Circular import issue still exists.")
        print("\nPlease check the error messages above for details.")
        sys.exit(1)