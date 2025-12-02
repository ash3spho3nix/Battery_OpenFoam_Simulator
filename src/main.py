"""
Main entry point for Battery Simulator Python application.

This module provides the main application entry point, similar to the C++ main.cpp.
It initializes the Qt application, creates the main window, and starts the event loop.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the src_py directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon

# Import modules using absolute imports to avoid packaging issues
from src.gui.main_window import MainWindow
from src.gui.ui_config import UIConfig
from src.core.constants import APP_NAME, APP_VERSION


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Battery Simulator Python Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Auto-detect UI mode
  python main.py --ui-mode ui_files        # Force .ui file loading
  python main.py --ui-mode hand_coded      # Force hand-coded widgets
  python main.py --ui-mode auto            # Auto-detect (default)
  python main.py --ui-path /custom/ui/path # Custom .ui file path
        """
    )
    
    parser.add_argument(
        '--ui-mode',
        choices=['ui_files', 'hand_coded', 'auto'],
        default='auto',
        help='UI loading mode (default: auto)'
    )
    
    parser.add_argument(
        '--ui-path',
        type=str,
        help='Custom path to .ui files directory'
    )
    
    parser.add_argument(
        '--no-fallback',
        action='store_true',
        help='Disable fallback to hand-coded widgets if .ui loading fails'
    )
    
    return parser.parse_args()


def main():
    """
    Main application entry point.
    
    Creates QApplication, MainWindow, and starts the event loop.
    Equivalent to the C++ main() function.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Set application metadata
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    QCoreApplication.setOrganizationName("BatterySimulator")
    QCoreApplication.setOrganizationDomain("batterysimulator.example.com")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application style (similar to C++)
    app.setStyle("Fusion")
    
    # Create UI configuration from command line arguments and environment
    ui_config = UIConfig.from_environment()
    ui_config = UIConfig.from_command_line(args)
    
    # Override fallback setting if requested
    if args.no_fallback:
        ui_config.set_fallback_enabled(False)
    
    # Override UI path if provided
    if args.ui_path:
        ui_config.set_ui_base_path(args.ui_path)
    
    print(f"Starting Battery Simulator with UI configuration: {ui_config}")
    
    # Create main window with UI configuration
    window = MainWindow(ui_config=ui_config)
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    # Handle Windows-specific path issues
    if sys.platform == "win32":
        # Ensure proper handling of Windows paths
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + os.getcwd()
    
    # Run the application
    exit_code = main()
    sys.exit(exit_code)
