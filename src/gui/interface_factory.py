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

from PyQt6.QtWidgets import QWidget
from typing import Optional, Type

logger.debug("Loading interface_factory module")

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
        ui_config: Optional['UIConfig'] = None
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
        logger.debug(f"InterfaceFactory.create_interface() called with interface_type='{interface_type}', parent={parent}, ui_config={ui_config}")
        
        ui_config = ui_config or InterfaceFactory._get_default_ui_config()
        
        # Determine if we should try .ui file loading
        should_try_ui = InterfaceFactory._should_try_ui_loading(interface_type, ui_config)
        
        logger.debug(f"InterfaceFactory.create_interface(): should_try_ui={should_try_ui}")
        
        if should_try_ui:
            try:
                logger.debug(f"InterfaceFactory.create_interface(): Attempting UI-based interface creation for {interface_type}")
                result = InterfaceFactory._create_ui_based_interface(interface_type, parent)
                logger.debug(f"InterfaceFactory.create_interface(): UI-based interface created successfully: {result}")
                return result
            except Exception as e:
                logger.error(f"InterfaceFactory.create_interface(): Failed to create UI-based interface: {e}", exc_info=True)
                print(f"Failed to create UI-based interface: {e}")
                if ui_config.should_fallback_to_hand_coded():
                    logger.info("InterfaceFactory.create_interface(): Falling back to hand-coded interface...")
                    print("Falling back to hand-coded interface...")
                    result = InterfaceFactory._create_hand_coded_interface(interface_type, parent)
                    logger.debug(f"InterfaceFactory.create_interface(): Hand-coded interface created successfully: {result}")
                    return result
                else:
                    error_msg = f"UI-based interface creation failed and fallback is disabled: {e}"
                    logger.error(f"InterfaceFactory.create_interface(): {error_msg}")
                    raise Exception(error_msg)
        else:
            logger.debug(f"InterfaceFactory.create_interface(): Creating hand-coded interface for {interface_type}")
            result = InterfaceFactory._create_hand_coded_interface(interface_type, parent)
            logger.debug(f"InterfaceFactory.create_interface(): Hand-coded interface created successfully: {result}")
            return result
    
    @staticmethod
    def _get_default_ui_config():
        """Get default UI configuration."""
        from src.gui.ui_config import UIConfig
        return UIConfig()
    
    @staticmethod
    def _should_try_ui_loading(interface_type: str, ui_config: 'UIConfig') -> bool:
        """
        Determine if we should try loading from .ui file.
        
        Args:
            interface_type: Type of interface
            ui_config: UI configuration
            
        Returns:
            bool: True if .ui loading should be attempted
        """
        from src.gui.ui_config import UILoadingMode
        
        if ui_config.mode == UILoadingMode.UI_FILES:
            return True
        elif ui_config.mode == UILoadingMode.HAND_CODED:
            return False
        elif ui_config.mode == UILoadingMode.AUTO_DETECT:
            # In auto-detect mode, check if .ui file exists
            ui_name = InterfaceFactory._get_ui_name(interface_type)
            from src.gui.ui_loader import UILoader
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
        logger.debug(f"InterfaceFactory._create_ui_based_interface() called for {interface_type}")
        ui_name = InterfaceFactory._get_ui_name(interface_type)
        from src.gui.ui_loader import UILoader
        ui_path = UILoader.get_ui_path(ui_name, base_path=None)
        
        logger.debug(f"InterfaceFactory._create_ui_based_interface(): Loading UI from {ui_path}")
        
        # Load the .ui file
        interface = UILoader.load_ui_file(ui_path, parent)
        
        logger.debug(f"InterfaceFactory._create_ui_based_interface(): UI loaded successfully: {interface}")
        
        # Set interface type for signal handling and debugging
        if hasattr(interface, 'set_property'):
            interface.setProperty('interface_type', interface_type)
        elif hasattr(interface, 'interface_type'):
            interface.interface_type = interface_type
        
        logger.debug(f"InterfaceFactory._create_ui_based_interface(): Interface type set to {interface_type}")
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
        logger.debug(f"InterfaceFactory._create_hand_coded_interface() called for {interface_type}")
        
        if interface_type == "carbon":
            logger.debug("InterfaceFactory._create_hand_coded_interface(): Creating CarbonInterface")
            from src.gui.interfaces.carbon_interface import CarbonInterface
            result = CarbonInterface(parent)
            logger.debug(f"InterfaceFactory._create_hand_coded_interface(): CarbonInterface created: {result}")
            return result
        elif interface_type == "halfcell":
            logger.debug("InterfaceFactory._create_hand_coded_interface(): Creating HalfCellInterface")
            from src.gui.interfaces.halfcell_interface import HalfCellInterface
            result = HalfCellInterface(parent)
            logger.debug(f"InterfaceFactory._create_hand_coded_interface(): HalfCellInterface created: {result}")
            return result
        elif interface_type == "fullcell":
            logger.debug("InterfaceFactory._create_hand_coded_interface(): Creating FullCellInterface")
            from src.gui.interfaces.fullcell_interface import FullCellInterface
            result = FullCellInterface(parent)
            logger.debug(f"InterfaceFactory._create_hand_coded_interface(): FullCellInterface created: {result}")
            return result
        elif interface_type == "result":
            logger.debug("InterfaceFactory._create_hand_coded_interface(): Creating ResultInterface")
            from src.gui.interfaces.result_interface import ResultInterface
            result = ResultInterface(parent)
            logger.debug(f"InterfaceFactory._create_hand_coded_interface(): ResultInterface created: {result}")
            return result
        else:
            error_msg = f"Unknown interface type: {interface_type}"
            logger.error(f"InterfaceFactory._create_hand_coded_interface(): {error_msg}")
            raise ValueError(error_msg)
    
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
    def create_main_window(ui_config: Optional['UIConfig'] = None) -> QWidget:
        """
        Create the main window interface.
        
        Args:
            ui_config: UI configuration
            
        Returns:
            QWidget: The main window widget
        """
        logger.debug("InterfaceFactory.create_main_window() called")
        ui_config = ui_config or InterfaceFactory._get_default_ui_config()
        
        if ui_config.should_load_ui_files():
            try:
                logger.debug("Attempting to load main window from .ui file")
                from src.gui.ui_loader import UILoader
                result = UILoader.load_main_window()
                logger.debug(f"InterfaceFactory.create_main_window(): Main window loaded from .ui: {result}")
                return result
            except Exception as e:
                logger.error(f"InterfaceFactory.create_main_window(): Failed to load main window from .ui file: {e}", exc_info=True)
                print(f"Failed to load main window from .ui file: {e}")
                if ui_config.should_fallback_to_hand_coded():
                    logger.debug("Falling back to hand-coded main window...")
                    # Import here to avoid circular imports - moved inside method
                    try:
                        from src.gui.main_window import MainWindow
                        logger.debug("Successfully imported MainWindow in create_main_window")
                        result = MainWindow(ui_config=ui_config)
                        logger.debug(f"InterfaceFactory.create_main_window(): Hand-coded main window created: {result}")
                        return result
                    except ImportError as ie:
                        logger.error(f"InterfaceFactory.create_main_window(): ImportError in create_main_window: {ie}", exc_info=True)
                        raise
                else:
                    error_msg = "UI-based main window creation failed and fallback is disabled"
                    logger.error(f"InterfaceFactory.create_main_window(): {error_msg}")
                    raise Exception(error_msg)
        
        # Fallback to hand-coded
        logger.debug("Using hand-coded main window fallback")
        try:
            from src.gui.main_window import MainWindow
            logger.debug("Successfully imported MainWindow in fallback")
            result = MainWindow(ui_config=ui_config)
            logger.debug(f"InterfaceFactory.create_main_window(): Hand-coded main window fallback created: {result}")
            return result
        except ImportError as ie:
            logger.error(f"InterfaceFactory.create_main_window(): ImportError in fallback: {ie}", exc_info=True)
            raise

logger.debug("interface_factory module loaded successfully")
