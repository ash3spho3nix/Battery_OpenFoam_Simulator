#!/usr/bin/env python3
"""
Main entry point for the Battery Simulator application.

This module contains the main application entry point and handles
application initialization, configuration, and startup.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('battery_simulator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    logger.info("Starting Battery Simulator application")
    
    try:
        # Import PyQt6
        from PyQt6.QtWidgets import QApplication
        
        # Import the main window
        from gui.main_window import MainWindow
        from gui.ui_config import UIConfig
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Battery Simulator")
        app.setApplicationVersion("1.0.0")
        
        # Create UI configuration
        ui_config = UIConfig()
        
        # Create main window
        main_window = MainWindow(ui_config=ui_config)
        main_window.show()
        
        # Start application event loop
        logger.info("Application started successfully")
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print(f"Error: {e}")
        print("Please install the required dependencies:")
        print("pip install PyQt6")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
