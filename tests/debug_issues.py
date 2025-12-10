#!/usr/bin/env python3
"""
Comprehensive debugging script for Battery Simulator issues.

This script identifies and fixes common issues:
1. Circular imports
2. Missing imports
3. UI loading problems
4. Configuration issues
5. Path problems
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

# Add src to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

def test_imports():
    """Test all critical imports to identify circular import issues."""
    print("Testing Imports...")
    print("=" * 50)
    
    issues = []
    
    # Test core imports
    try:
        print("Testing core.constants...")
        from src.core import constants
        print("core.constants imported successfully")
    except Exception as e:
        print(f"core.constants import failed: {e}")
        issues.append(f"core.constants: {e}")
    
    try:
        print("Testing core.project_manager...")
        from src.core import project_manager
        print("core.project_manager imported successfully")
    except Exception as e:
        print(f"core.project_manager import failed: {e}")
        issues.append(f"core.project_manager: {e}")
    
    # Test GUI imports
    try:
        print("Testing gui.ui_config...")
        from src.gui import ui_config
        print("gui.ui_config imported successfully")
    except Exception as e:
        print(f"gui.ui_config import failed: {e}")
        issues.append(f"gui.ui_config: {e}")
    
    try:
        print("Testing gui.interface_factory...")
        from src.gui import interface_factory
        print("gui.interface_factory imported successfully")
    except Exception as e:
        print(f"gui.interface_factory import failed: {e}")
        issues.append(f"gui.interface_factory: {e}")
    
    # Test main application
    try:
        print("Testing core.application...")
        from src.core import application
        print("core.application imported successfully")
    except Exception as e:
        print(f"core.application import failed: {e}")
        issues.append(f"core.application: {e}")
    
    # Test main window
    try:
        print("Testing gui.main_window...")
        from src.gui import main_window
        print("gui.main_window imported successfully")
    except Exception as e:
        print(f"gui.main_window import failed: {e}")
        issues.append(f"gui.main_window: {e}")
    
    # Test main.py imports
    try:
        print("Testing main.py imports...")
        from src.gui.main_window import MainWindow
        from src.gui.ui_config import UIConfig
        from src.core.constants import APP_NAME, APP_VERSION
        print("main.py imports successful")
    except Exception as e:
        print(f"main.py imports failed: {e}")
        issues.append(f"main.py imports: {e}")
    
    return issues

def check_file_structure():
    """Check if all required files exist."""
    print("\nChecking File Structure...")
    print("=" * 50)
    
    required_files = [
        "src/core/constants.py",
        "src/core/project_manager.py",
        "src/core/application.py",
        "src/gui/main_window.py",
        "src/gui/ui_config.py",
        "src/gui/interface_factory.py",
        "src/gui/ui_loader.py",
        "src/gui/interfaces/base_interface.py",
        "src/gui/interfaces/carbon_interface.py",
        "src/openfoam/process_controller.py",
        "src/openfoam/solver_manager.py",
        "src/utils/file_operations.py",
        "src/utils/parameter_parser.py",
        "src/resources/ui/mainwindow.ui",
        "src/resources/ui/carboninterface.ui",
        "src/resources/ui/halfcellinterface.ui",
        "src/resources/ui/fullcellfoam.ui",
        "src/resources/ui/resultinterface.ui",
        "src/main.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = SRC_DIR / file_path
        if full_path.exists():
            print(f"File exists: {file_path}")
        else:
            print(f"MISSING: {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def check_constants_file():
    """Check if constants.py has the required constants."""
    print("\nChecking Constants File...")
    print("=" * 50)
    
    try:
        from src.core import constants
        required_constants = [
            'APP_NAME', 'APP_VERSION', 'SUPPORTED_MODULES', 
            'DEFAULT_PROJECT_PATH', 'ERROR_MESSAGES', 'SUCCESS_MESSAGES'
        ]
        
        missing_constants = []
        for const in required_constants:
            if hasattr(constants, const):
                print(f"Constant exists: {const}")
            else:
                print(f"MISSING: {const}")
                missing_constants.append(const)
        
        return missing_constants
    except Exception as e:
        print(f"Failed to import constants: {e}")
        return ['constants import failed']

def check_ui_files():
    """Check if UI files exist and are readable."""
    print("\nChecking UI Files...")
    print("=" * 50)
    
    ui_dir = SRC_DIR / "resources" / "ui"
    if not ui_dir.exists():
        print(f"UI directory missing: {ui_dir}")
        return [f"UI directory missing: {ui_dir}"]
    
    ui_files = [
        "mainwindow.ui", "carboninterface.ui", "halfcellinterface.ui",
        "fullcellfoam.ui", "resultinterface.ui"
    ]
    
    missing_ui = []
    for ui_file in ui_files:
        ui_path = ui_dir / ui_file
        if ui_path.exists():
            print(f"UI file exists: {ui_file}")
        else:
            print(f"UI file MISSING: {ui_file}")
            missing_ui.append(ui_file)
    
    return missing_ui

def test_pyqt6_import():
    """Test PyQt6 installation."""
    print("\nTesting PyQt6 Installation...")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon
        print("PyQt6 imported successfully")
        return []
    except ImportError as e:
        print(f"PyQt6 import failed: {e}")
        print("Please install PyQt6: pip install PyQt6")
        return ["PyQt6 not installed"]

def test_ui_loading():
    """Test UI loading functionality."""
    print("\nTesting UI Loading...")
    print("=" * 50)
    
    issues = []
    
    try:
        from src.gui.ui_loader import UILoader
        print("UILoader imported successfully")
        
        # Test if UI files exist
        ui_files = ["mainwindow", "carboninterface", "halfcellinterface", "fullcellfoam", "resultinterface"]
        for ui_name in ui_files:
            if UILoader.ui_file_exists(ui_name):
                print(f"UI file exists: {ui_name}.ui")
            else:
                print(f"UI file MISSING: {ui_name}.ui")
                issues.append(f"{ui_name}.ui missing")
        
        return issues
    except Exception as e:
        print(f"UI loading test failed: {e}")
        issues.append(f"UI loading failed: {e}")
        return issues

def test_interface_factory():
    """Test InterfaceFactory functionality."""
    print("\nTesting Interface Factory...")
    print("=" * 50)
    
    issues = []
    
    try:
        from src.gui.interface_factory import InterfaceFactory
        print("InterfaceFactory imported successfully")
        
        # Test available interfaces
        available = InterfaceFactory.get_available_interfaces()
        print(f"Available interfaces: {available}")
        
        # Test UI name mapping
        test_mappings = [
            ("carbon", "carboninterface"),
            ("halfcell", "halfcellinterface"),
            ("fullcell", "fullcellfoam"),
            ("result", "resultinterface")
        ]
        
        for interface_type, expected_ui in test_mappings:
            actual_ui = InterfaceFactory._get_ui_name(interface_type)
            if actual_ui == expected_ui:
                print(f"UI mapping correct: {interface_type} -> {actual_ui}")
            else:
                print(f"UI mapping INCORRECT: {interface_type} -> {actual_ui} (expected {expected_ui})")
                issues.append(f"UI name mapping incorrect for {interface_type}")
        
        return issues
    except Exception as e:
        print(f"InterfaceFactory test failed: {e}")
        issues.append(f"InterfaceFactory failed: {e}")
        return issues

def test_ui_config():
    """Test UIConfig functionality."""
    print("\nTesting UI Configuration...")
    print("=" * 50)
    
    issues = []
    
    try:
        from src.gui.ui_config import UIConfig, UILoadingMode
        print("UIConfig imported successfully")
        
        # Test default configuration
        config = UIConfig()
        print(f"Default mode: {config.mode}")
        print(f"Prefer UI files: {config.prefer_ui_files}")
        print(f"Fallback enabled: {config.fallback_to_hand_coded}")
        
        # Test environment configuration
        try:
            env_config = UIConfig.from_environment()
            print("Environment configuration works")
        except Exception as e:
            print(f"Environment configuration failed: {e}")
            issues.append(f"Environment config failed: {e}")
        
        return issues
    except Exception as e:
        print(f"UIConfig test failed: {e}")
        issues.append(f"UIConfig failed: {e}")
        return issues

def run_comprehensive_test():
    """Run all tests and provide a comprehensive report."""
    print("Running Comprehensive Debug Test")
    print("=" * 60)
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_imports())
    all_issues.extend(check_file_structure())
    all_issues.extend(check_constants_file())
    all_issues.extend(check_ui_files())
    all_issues.extend(test_pyqt6_import())
    all_issues.extend(test_ui_loading())
    all_issues.extend(test_interface_factory())
    all_issues.extend(test_ui_config())
    
    # Print summary
    print("\nTest Summary")
    print("=" * 60)
    
    if not all_issues:
        print("All tests passed! No issues found.")
        print("\nThe application should run successfully.")
    else:
        print(f"Found {len(all_issues)} issues:")
        print()
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        print("\nRecommended Fixes:")
        print("-" * 40)
        
        # Provide specific recommendations
        if any("config" in issue.lower() for issue in all_issues):
            print("1. Fix circular import in core/application.py:")
            print("   Change: from .config import ...")
            print("   To:     from .constants import ...")
        
        if any("pyqt6" in issue.lower() for issue in all_issues):
            print("2. Install PyQt6:")
            print("   pip install PyQt6")
        
        if any("missing" in issue.lower() for issue in all_issues):
            print("3. Create missing files or fix file paths")
        
        if any("ui" in issue.lower() for issue in all_issues):
            print("4. Check UI files in src/resources/ui/")
    
    return len(all_issues) == 0

def main():
    """Main debugging function."""
    print("Battery Simulator Debug Script")
    print("Starting comprehensive debugging analysis...")
    print()
    
    try:
        success = run_comprehensive_test()
        
        print("\n" + "=" * 60)
        if success:
            print("Debugging completed successfully!")
            print("You can now run: python src/main.py")
        else:
            print("Debugging found issues that need to be fixed.")
            print("Please address the issues above before running the application.")
        
    except Exception as e:
        print(f"\nCritical error during debugging: {e}")
        traceback.print_exc()
        print("\nPlease check your Python environment and file structure.")

if __name__ == "__main__":
    main()