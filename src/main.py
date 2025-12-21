#!/usr/bin/env python3
"""
Main entry point for the Battery Simulator application.
This module contains the main application entry point and handles
application initialization, configuration, and startup.
"""

import sys
import logging
from pathlib import Path
import io

# Fix console encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))  # Add parent directory (project root)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application."""
    logger.info("Starting Battery Simulator application")
    
    try:
        # Import PyQt6
        from PyQt6.QtWidgets import QApplication
        
        # Import enhanced modules
        from src.gui.main_window import MainWindow
        from src.gui.ui_config_enhanced import EnhancedUIConfig
        from src.gui.ui_loader_enhanced import EnhancedUILoader
        from src.core.project_manager_enhanced import EnhancedProjectManager
        
        # Create configuration from multiple sources (CLI, Env, Defaults)
        ui_config = EnhancedUIConfig.from_multiple_sources()
        
        # Set up logging based on the resolved configuration
        ui_config._setup_logger() # This method needs to be added to EnhancedUIConfig
        logger.info(f"UI Configuration loaded: {ui_config.get_summary()}")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Battery Simulator")
        app.setApplicationVersion("1.0.0")
        
        # Initialize core enhanced components
        projects_path = Path.home() / "BatterySimulatorProjects"
        project_manager = EnhancedProjectManager(base_projects_path=projects_path)
        ui_loader = EnhancedUILoader(ui_config=ui_config)
        
        logger.info(f"UI Mode: {ui_config.get_setting('mode').name}")
        logger.info(f"Projects will be stored in: {projects_path}")
        
        # Create main window
        main_window = MainWindow()
        main_window.show()
        
        # Start application event loop
        logger.info("Application started successfully")
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)
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
