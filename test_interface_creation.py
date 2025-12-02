#!/usr/bin/env python3
"""
Test script to diagnose interface creation issues.

This script helps identify the root cause of the blank screen issue
by testing interface creation in isolation.
"""

import sys
import os
import logging

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Set up logging to see detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_ui_loading():
    """Test .ui file loading."""
    logger.info("=== Testing UI File Loading ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Test UI loader
        from src.gui.ui_loader import UILoader
        
        # Test if carboninterface.ui exists
        ui_path = UILoader.get_ui_path("carboninterface")
        logger.info(f"UI path: {ui_path}")
        logger.info(f"UI file exists: {os.path.exists(ui_path)}")
        
        if os.path.exists(ui_path):
            try:
                # Try to load the .ui file
                widget = UILoader.load_ui_file(ui_path)
                logger.info(f"UI loaded successfully: {widget}")
                logger.info(f"Widget type: {type(widget)}")
                logger.info(f"Widget class name: {widget.metaObject().className()}")
                
                # List all attributes
                logger.info("Widget attributes:")
                for attr_name in dir(widget):
                    if not attr_name.startswith('_'):
                        try:
                            attr_value = getattr(widget, attr_name)
                            if hasattr(attr_value, '__class__'):
                                logger.info(f"  {attr_name}: {attr_value.__class__.__name__}")
                        except:
                            logger.info(f"  {attr_name}: <cannot access>")
                
                return True
            except Exception as e:
                logger.error(f"Failed to load UI file: {e}", exc_info=True)
                return False
        else:
            logger.error("UI file does not exist")
            return False
            
    except Exception as e:
        logger.error(f"Error in test_ui_loading: {e}", exc_info=True)
        return False

def test_interface_creation():
    """Test interface creation."""
    logger.info("=== Testing Interface Creation ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Test interface factory
        from src.gui.interface_factory import InterfaceFactory
        from src.gui.ui_config import UIConfig
        
        ui_config = UIConfig()
        ui_config.mode = ui_config.mode.HAND_CODED  # Force hand-coded
        
        logger.info(f"UI Config: {ui_config}")
        
        # Test hand-coded interface creation
        try:
            interface = InterfaceFactory.create_interface("carbon", None, ui_config)
            logger.info(f"Hand-coded interface created: {interface}")
            logger.info(f"Interface type: {type(interface)}")
            return True
        except Exception as e:
            logger.error(f"Failed to create hand-coded interface: {e}", exc_info=True)
            
            # Try UI-based creation
            ui_config.mode = ui_config.mode.UI_FILES
            try:
                interface = InterfaceFactory.create_interface("carbon", None, ui_config)
                logger.info(f"UI-based interface created: {interface}")
                logger.info(f"Interface type: {type(interface)}")
                return True
            except Exception as e2:
                logger.error(f"Failed to create UI-based interface: {e2}", exc_info=True)
                return False
                
    except Exception as e:
        logger.error(f"Error in test_interface_creation: {e}", exc_info=True)
        return False

def test_widget_naming():
    """Test widget naming compatibility."""
    logger.info("=== Testing Widget Naming ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Test hand-coded interface
        from src.gui.interfaces.carbon_interface import CarbonInterface
        from src.gui.ui_config import UIConfig
        
        ui_config = UIConfig()
        ui_config.mode = ui_config.mode.HAND_CODED
        
        interface = CarbonInterface(None, ui_config)
        
        # Check widget availability
        widgets_to_check = [
            'length_edit', 'width_edit', 'height_edit',
            'length_lineEdit', 'width_lineEdit', 'height_lineEdit',
            'unit_combo', 'unit_select_box',
            'tabWidget'
        ]
        
        for widget_name in widgets_to_check:
            if hasattr(interface, widget_name):
                widget = getattr(interface, widget_name)
                logger.info(f"✓ {widget_name}: {type(widget)}")
            else:
                logger.info(f"✗ {widget_name}: Not found")
                
        return True
        
    except Exception as e:
        logger.error(f"Error in test_widget_naming: {e}", exc_info=True)
        return False

def main():
    """Run all tests."""
    logger.info("Starting interface diagnosis tests...")
    
    tests = [
        ("UI Loading", test_ui_loading),
        ("Interface Creation", test_interface_creation),
        ("Widget Naming", test_widget_naming)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results[test_name] = result
            logger.info(f"{test_name} test: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"{test_name} test failed with exception: {e}")
            results[test_name] = False
    
    logger.info(f"\n{'='*50}")
    logger.info("Test Results Summary:")
    logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        logger.info(f"{test_name}: {'PASSED' if result else 'FAILED'}")
    
    # Overall diagnosis
    logger.info(f"\n{'='*50}")
    logger.info("DIAGNOSIS:")
    logger.info(f"{'='*50}")
    
    if not results.get("UI Loading", False):
        logger.error("❌ UI file loading is failing - this could cause blank screens")
    else:
        logger.info("✅ UI file loading is working")
        
    if not results.get("Interface Creation", False):
        logger.error("❌ Interface creation is failing - this is likely causing blank screens")
    else:
        logger.info("✅ Interface creation is working")
        
    if not results.get("Widget Naming", False):
        logger.error("❌ Widget naming issues detected - this could cause AttributeError exceptions")
    else:
        logger.info("✅ Widget naming is working")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)