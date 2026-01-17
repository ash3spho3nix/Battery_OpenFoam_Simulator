"""
Main application entry point for Battery Simulator.

This module contains the main function that initializes and runs the application.
"""

import sys
import logging
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add src directory to Python path
current_dir = Path(__file__).parent  # This is src/
parent_dir = current_dir.parent     # This is the project root
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("battery_simulator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the Battery Simulator application.
    
    Initializes the Qt application, creates the main window, and starts the event loop.
    """
    logger.info("Starting Battery Simulator application")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    try:
        # Import and create main window
        from src.gui.main_window import MainWindow
        from src.gui.ui_config import UIConfig
        from src.core.config import get_config_manager
        
        # Get UI files path from config manager
        config_manager = get_config_manager()
        ui_files_path = config_manager.get_ui_files_path()
        
        # Create UI configuration
        ui_config = UIConfig()
        ui_config.update_setting('ui_base_path', ui_files_path)
        
        # Create main window with UI configuration
        main_window = MainWindow(ui_config=ui_config)
        
        # Show main window
        main_window.show()
        
        # Start event loop
        logger.info("Application started successfully")
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
