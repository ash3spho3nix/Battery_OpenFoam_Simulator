#!/usr/bin/env python3
"""
Diagnostic script to identify the root cause of the UI loading issues.
This script will help validate our assumptions about the problem sources.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_directory_structure():
    """Check if required directories exist."""
    print("=== Directory Structure Check ===")
    
    base_path = Path("resources")
    ui_path = base_path / "ui"
    templates_path = base_path / "templates"
    
    print(f"Base path exists: {base_path.exists()} - {base_path}")
    print(f"UI path exists: {ui_path.exists()} - {ui_path}")
    print(f"Templates path exists: {templates_path.exists()} - {templates_path}")
    
    if ui_path.exists():
        ui_files = list(ui_path.glob("*.ui"))
        print(f"UI files found: {len(ui_files)}")
        for ui_file in ui_files:
            print(f"  - {ui_file}")
    else:
        print("No UI directory found")
    
    if templates_path.exists():
        template_dirs = [d for d in templates_path.iterdir() if d.is_dir()]
        print(f"Template directories found: {len(template_dirs)}")
        for template_dir in template_dirs:
            print(f"  - {template_dir}")
    else:
        print("No templates directory found")
    
    return ui_path.exists(), templates_path.exists()

def check_ui_file_paths():
    """Check specific UI file paths that are failing."""
    print("\n=== UI File Path Check ===")
    
    from src.gui.ui_loader import UILoader
    from src.gui.ui_config import UIConfig
    
    # Test the specific file that's failing
    ui_name = "carboninterface"
    ui_path = UILoader.get_ui_path(ui_name)
    
    print(f"Expected UI path: {ui_path}")
    print(f"UI file exists: {os.path.exists(ui_path)}")
    
    # Test with different base paths
    test_paths = [
        None,  # Default path
        "resources/ui",  # Relative path
        str(Path("resources/ui")),  # Absolute path
    ]
    
    for test_path in test_paths:
        try:
            path = UILoader.get_ui_path(ui_name, test_path)
            exists = os.path.exists(path)
            print(f"  Path: {path} -> Exists: {exists}")
        except Exception as e:
            print(f"  Path: {test_path} -> Error: {e}")

def check_template_paths():
    """Check template paths that are failing."""
    print("\n=== Template Path Check ===")
    
    from src.core.constants import TEMPLATES_PATH
    
    # Convert string to Path if needed
    if isinstance(TEMPLATES_PATH, str):
        templates_path = Path(TEMPLATES_PATH)
    else:
        templates_path = TEMPLATES_PATH
    
    print(f"TEMPLATES_PATH constant: {TEMPLATES_PATH}")
    print(f"TEMPLATES_PATH exists: {templates_path.exists()}")
    
    # Check SPM template specifically
    spm_path = templates_path / "SPM"
    print(f"SPM template path: {spm_path}")
    print(f"SPM template exists: {spm_path.exists()}")

def test_ui_config_modes():
    """Test different UI configuration modes."""
    print("\n=== UI Configuration Modes Test ===")
    
    from src.gui.ui_config import UIConfig, UILoadingMode
    
    modes = [UILoadingMode.UI_FILES, UILoadingMode.HAND_CODED, UILoadingMode.AUTO_DETECT]
    
    for mode in modes:
        config = UIConfig()
        config.set_mode(mode)
        
        print(f"Mode: {mode.value}")
        print(f"  Should load UI files: {config.should_load_ui_files()}")
        print(f"  Should fallback: {config.should_fallback_to_hand_coded()}")

def test_interface_factory_fallback():
    """Test the interface factory fallback mechanism."""
    print("\n=== Interface Factory Fallback Test ===")
    
    from src.gui.interface_factory import InterfaceFactory
    from src.gui.ui_config import UIConfig
    
    config = UIConfig()
    config.set_mode("auto_detect")  # Test auto-detect mode
    
    print(f"Testing interface creation with auto-detect mode...")
    
    try:
        # This should trigger the fallback mechanism
        interface = InterfaceFactory.create_interface("carbon", ui_config=config, use_cache=False)
        print(f"✅ Interface created successfully: {interface}")
    except Exception as e:
        print(f"❌ Interface creation failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Check creation statistics
        stats = InterfaceFactory.get_creation_stats()
        print(f"Creation stats: {stats}")

def test_enhanced_validation():
    """Test the enhanced validation specifically."""
    print("\n=== Enhanced Validation Test ===")
    
    from src.gui.ui_loader import UILoader
    
    ui_name = "carboninterface"
    
    print(f"Testing enhanced validation for: {ui_name}")
    
    # Test file existence check
    exists = UILoader.ui_file_exists(ui_name)
    print(f"UI file exists (with validation): {exists}")
    
    # Test available UI files
    available = UILoader.get_available_ui_files()
    print(f"Available UI files: {available}")

def main():
    """Run all diagnostic tests."""
    print("Battery Simulator UI Loading Diagnostic Tool")
    print("=" * 50)
    
    # Check directory structure first
    ui_exists, templates_exists = check_directory_structure()
    
    # Check specific paths
    check_ui_file_paths()
    check_template_paths()
    
    # Test configurations
    test_ui_config_modes()
    
    # Test fallback mechanism
    test_interface_factory_fallback()
    
    # Test enhanced validation
    test_enhanced_validation()
    
    print("\n" + "=" * 50)
    print("Diagnostic Summary:")
    print(f"UI directory exists: {ui_exists}")
    print(f"Templates directory exists: {templates_exists}")
    
    if not ui_exists:
        print("❌ RECOMMENDATION: Create resources/ui directory and add .ui files")
    if not templates_exists:
        print("❌ RECOMMENDATION: Create resources/templates directory and add template files")
    
    print("\nNext steps:")
    print("1. Create missing directories if they don't exist")
    print("2. Add required .ui files to resources/ui/")
    print("3. Add required template files to resources/templates/")
    print("4. Test the application again")

if __name__ == "__main__":
    main()