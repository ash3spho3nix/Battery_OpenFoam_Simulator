"""
Interface Factory for Battery Simulator.

This module provides a factory for creating simulation interfaces,
supporting both .ui file loading and hand-coded widget approaches.
"""

import sys
import logging

# Set up logging to help debug circular imports
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Loading interface_factory module")

from PyQt6.QtWidgets import QWidget
from typing import Optional, Type

# Import modules using absolute imports to avoid packaging issues
from src_py.gui.ui_loader import UILoader
from src_py.gui.ui_config import UIConfig, UILoadingMode
from src_py.gui.interfaces.base_interface import BaseInterface

logger.debug("interface_factory: Core imports completed")


class InterfaceFactory:
    """
    Factory for creating simulation interfaces.
    
    This factory creates the appropriate interface based on the configuration,
    supporting both .ui file loading and hand-coded widget approaches with
    automatic fallback capabilities.
    """
    
    @staticmethod
    def create_interface(
        interface_type: str, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional[UIConfig] = None
    ) -> QWidget:
        """
        Create an interface based on type and configuration.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell, result)
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            ValueError: If interface type is unknown
            Exception: If creation fails and no fallback is available
        """
        ui_config = ui_config or UIConfig()
        
        # Determine if we should try .ui file loading
        should_try_ui = InterfaceFactory._should_try_ui_loading(interface_type, ui_config)
        
        if should_try_ui:
            try:
                return InterfaceFactory._create_ui_based_interface(interface_type, parent)
            except Exception as e:
                print(f"Failed to create UI-based interface: {e}")
                if ui_config.should_fallback_to_hand_coded():
                    print("Falling back to hand-coded interface...")
                    return InterfaceFactory._create_hand_coded_interface(interface_type, parent)
                else:
                    raise Exception(f"UI-based interface creation failed and fallback is disabled: {e}")
        else:
            return InterfaceFactory._create_hand_coded_interface(interface_type, parent)
    
    @staticmethod
    def _should_try_ui_loading(interface_type: str, ui_config: UIConfig) -> bool:
        """
        Determine if we should try loading from .ui file.
        
        Args:
            interface_type: Type of interface
            ui_config: UI configuration
            
        Returns:
            bool: True if .ui loading should be attempted
        """
        if ui_config.mode == UILoadingMode.UI_FILES:
            return True
        elif ui_config.mode == UILoadingMode.HAND_CODED:
            return False
        elif ui_config.mode == UILoadingMode.AUTO_DETECT:
            # In auto-detect mode, check if .ui file exists
            ui_name = InterfaceFactory._get_ui_name(interface_type)
            return UILoader.ui_file_exists(ui_name, ui_config.get_ui_base_path())
        return False
    
    @staticmethod
    def _create_ui_based_interface(interface_type: str, parent: Optional[QWidget]) -> QWidget:
        """
        Create interface from .ui file.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            
        Returns:
            QWidget: The loaded interface widget
        """
        ui_name = InterfaceFactory._get_ui_name(interface_type)
        ui_path = UILoader.get_ui_path(ui_name, base_path=None)
        
        # Load the .ui file
        interface = UILoader.load_ui_file(ui_path, parent)
        
        # Set interface type for signal handling and debugging
        if hasattr(interface, 'set_property'):
            interface.setProperty('interface_type', interface_type)
        elif hasattr(interface, 'interface_type'):
            interface.interface_type = interface_type
        
        return interface
    
    @staticmethod
    def _create_hand_coded_interface(interface_type: str, parent: Optional[QWidget]) -> QWidget:
        """
        Create hand-coded interface.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            
        Returns:
            QWidget: The created interface widget
        """
        if interface_type == "carbon":
            from src_py.gui.interfaces.carbon_interface import CarbonInterface
            return CarbonInterface(parent)
        elif interface_type == "halfcell":
            from src_py.gui.interfaces.halfcell_interface import HalfCellInterface
            return HalfCellInterface(parent)
        elif interface_type == "fullcell":
            from src_py.gui.interfaces.fullcell_interface import FullCellInterface
            return FullCellInterface(parent)
        elif interface_type == "result":
            from src_py.gui.interfaces.result_interface import ResultInterface
            return ResultInterface(parent)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
    
    @staticmethod
    def _get_ui_name(interface_type: str) -> str:
        """
        Get the .ui file name for an interface type.
        
        Args:
            interface_type: Type of interface
            
        Returns:
            str: Corresponding .ui file name
        """
        ui_name_map = {
            "carbon": "carboninterface",
            "halfcell": "halfcellinterface",
            "fullcell": "fullcellfoam",
            "result": "resultinterface"
        }
        return ui_name_map.get(interface_type, interface_type)
    
    @staticmethod
    def get_available_interfaces() -> list:
        """
        Get a list of available interface types.
        
        Returns:
            list: List of available interface types
        """
        return ["carbon", "halfcell", "fullcell", "result"]
    
    @staticmethod
    def interface_exists(interface_type: str) -> bool:
        """
        Check if an interface type exists.
        
        Args:
            interface_type: Type of interface
            
        Returns:
            bool: True if interface exists
        """
        return interface_type in InterfaceFactory.get_available_interfaces()
    
    @staticmethod
    def create_main_window(ui_config: Optional[UIConfig] = None) -> QWidget:
        """
        Create the main window interface.
        
        Args:
            ui_config: UI configuration
            
        Returns:
            QWidget: The main window widget
        """
        logger.debug("InterfaceFactory.create_main_window() called")
        ui_config = ui_config or UIConfig()
        
        if ui_config.should_load_ui_files():
            try:
                logger.debug("Attempting to load main window from .ui file")
                return UILoader.load_main_window()
            except Exception as e:
                print(f"Failed to load main window from .ui file: {e}")
                if ui_config.should_fallback_to_hand_coded():
                    logger.debug("Falling back to hand-coded main window...")
                    # Import here to avoid circular imports - moved inside method
                    try:
                        from src_py.gui.main_window import MainWindow
                        logger.debug("Successfully imported MainWindow in create_main_window")
                        return MainWindow(ui_config=ui_config)
                    except ImportError as ie:
                        logger.error(f"ImportError in create_main_window: {ie}")
                        raise
                else:
                    raise
        
        # Fallback to hand-coded
        logger.debug("Using hand-coded main window fallback")
        try:
            from src_py.gui.main_window import MainWindow
            logger.debug("Successfully imported MainWindow in fallback")
            return MainWindow(ui_config=ui_config)
        except ImportError as ie:
            logger.error(f"ImportError in fallback: {ie}")
            raise

logger.debug("interface_factory module loaded successfully")
