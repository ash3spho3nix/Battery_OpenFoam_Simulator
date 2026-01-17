#!/usr/bin/env python3
"""
Interface Factory Module - Dynamic Interface Creation with UI Loading Support.

This module provides a factory for creating interface instances with support
for different UI loading modes (AUTO_DETECT, UI_FILES, HAND_CODED) and
comprehensive error handling.
"""

import logging
from typing import Optional, Dict, Any, List, Callable, Union
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QMetaObject

from .ui_config import UIConfig
from .ui_loader import UILoader  # Fixed: Changed from UILoader to UILoader

from pathlib import Path

from .interfaces import (
    CarbonInterface,
    HalfCellInterface,
    FullCellInterface,
    ResultInterface
)

class InterfaceFactoryError(Exception):
    """Custom exception for interface factory errors."""
    pass


class InterfaceValidationError(Exception):
    """Custom exception for interface validation errors."""
    pass


class InterfaceFactory:
    """
    Factory for creating interface instances with UI loading support.
    
    Features:
    - Dynamic interface creation based on type
    - Support for all UI loading modes
    - Comprehensive error handling and recovery
    - Detailed logging and progress tracking
    - Interface validation and integrity checking
    - Performance monitoring and caching
    """
    
    # Class-level caches for performance
    _interface_cache: Dict[str, QWidget] = {}
    _loading_stats = {
        'total_attempts': 0,
        'successful_loads': 0,
        'failed_loads': 0,
        'fallbacks': 0
    }
    
    def __init__(self, ui_config: Optional[UIConfig] = None):
        """
        Initialize the interface factory.
        
        Args:
            ui_config: UI configuration for loading mode
        """
        self.ui_config = ui_config or UIConfig()
        self.logger = logging.getLogger(__name__)
        self.ui_loader = UILoader(self.ui_config.get_ui_path())
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup detailed logging for interface factory operations."""
        self.logger = logging.getLogger(f"{__name__}.InterfaceFactory")
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            # File handler for detailed logs
            log_file = Path(__file__).parent.parent / "logs" / "interface_factory.log"
            log_file.parent.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def create_interface(
        self, 
        interface_type: str, 
        parent: Optional[QWidget] = None,
        ui_config: Optional[UIConfig] = None
    ) -> Optional[QWidget]:
        """
        Create an interface instance using the configured UI loading mode.
        
        Args:
            interface_type: Type of interface to create
            parent: Parent widget
            ui_config: Optional UI configuration override
            
        Returns:
            Created interface widget or None if creation failed
            
        Raises:
            InterfaceFactoryError: If interface creation fails
            InterfaceValidationError: If interface validation fails
        """
        # Use provided config or fallback to instance config
        config = ui_config or self.ui_config
        
        # Check cache first
        cache_key = f"{interface_type}_{config.mode}"
        if cache_key in self._interface_cache:
            self.logger.info(f"Using cached interface for: {interface_type}")
            return self._interface_cache[cache_key]
        
        self.logger.info(f"Creating interface: {interface_type}")
        self.logger.info(f"UI loading mode: {config.mode}")
        
        # Update statistics
        self._update_stats('total_attempts')
        
        try:
            # Create interface based on type
            if interface_type.lower() == 'mainwindow':
                widget = self._create_main_window(parent, config)
            elif interface_type.lower() == 'carbon':
                widget = self._create_carbon_interface(parent, config)
            elif interface_type.lower() == 'halfcell':
                widget = self._create_half_cell_interface(parent, config)
            elif interface_type.lower() == 'fullcell':
                widget = self._create_full_cell_interface(parent, config)
            elif interface_type.lower() == 'resultinterface':
                widget = self._create_result_interface(parent, config)
            else:
                raise InterfaceFactoryError(f"Unknown interface type: {interface_type}")
            
            if widget:
                # Validate the created interface
                self._validate_interface_integrity(widget, interface_type)
                
                # Cache the interface if successful
                self._interface_cache[cache_key] = widget
                
                self.logger.info(f"Successfully created interface: {interface_type}")
                self._update_stats('successful_loads')
                return widget
            else:
                raise InterfaceFactoryError(f"Failed to create interface: {interface_type}")
                
        except Exception as e:
            self.logger.error(f"Interface creation failed for {interface_type}: {e}", exc_info=True)
            self._update_stats('failed_loads')
            
            # Re-raise specific exceptions
            if isinstance(e, (InterfaceFactoryError, InterfaceValidationError)):
                raise
            else:
                raise InterfaceFactoryError(f"Interface creation failed: {e}") from e
    
    def _create_main_window(self, parent: Optional[QWidget], config: UIConfig) -> Optional[QWidget]:
        """Create a main window interface."""
        try:
            # Local import to avoid circular dependency
            from .main_window import MainWindow
            window = MainWindow(ui_config=config)
            self.logger.info("Successfully created main window")
            return window
        except Exception as e:
            self.logger.error(f"Failed to create main window: {e}")
            return None
    
    def _create_carbon_interface(self, parent: Optional[QWidget], config: UIConfig) -> Optional[QWidget]:
        """Create a carbon interface."""
        try:
            interface = CarbonInterface(parent, config)
            self.logger.info("Successfully created carbon interface")
            return interface
        except Exception as e:
            self.logger.error(f"Failed to create carbon interface: {e}")
            return None
    
    def _create_half_cell_interface(self, parent: Optional[QWidget], config: UIConfig) -> Optional[QWidget]:
        """Create a half cell interface."""
        try:
            interface = HalfCellInterface(parent, config)
            self.logger.info("Successfully created half cell interface")
            return interface
        except Exception as e:
            self.logger.error(f"Failed to create half cell interface: {e}")
            return None
    
    def _create_full_cell_interface(self, parent: Optional[QWidget], config: UIConfig) -> Optional[QWidget]:
        """Create a full cell interface."""
        try:
            interface = FullCellInterface(parent, config)
            self.logger.info("Successfully created full cell interface")
            return interface
        except Exception as e:
            self.logger.error(f"Failed to create full cell interface: {e}")
            return None
    
    def _create_result_interface(self, parent: Optional[QWidget], config: UIConfig) -> Optional[QWidget]:
        """Create a result interface."""
        try:
            interface = ResultInterface(parent, config)
            self.logger.info("Successfully created result interface")
            return interface
        except Exception as e:
            self.logger.error(f"Failed to create result interface: {e}")
            return None
    
    def _validate_interface_integrity(self, widget: QWidget, interface_type: str):
        """
        Validate the integrity of a created interface.
        
        Args:
            widget: The created widget
            interface_type: Type of interface being validated
            
        Raises:
            InterfaceValidationError: If validation fails
        """
        try:
            # Check if widget is properly initialized
            if not widget:
                raise InterfaceValidationError(f"Widget is None for {interface_type}")
            
            # Check for basic widget properties
            if not hasattr(widget, 'objectName'):
                raise InterfaceValidationError(f"Widget missing objectName property for {interface_type}")
            
            # Check for required methods
            required_methods = ['show', 'close', 'setParent']
            for method in required_methods:
                if not hasattr(widget, method):
                    raise InterfaceValidationError(f"Widget missing required method {method} for {interface_type}")
            
            self.logger.debug(f"Interface validation passed for {interface_type}")
            
        except Exception as e:
            self.logger.error(f"Interface validation failed for {interface_type}: {e}")
            raise InterfaceValidationError(f"Interface validation failed: {e}") from e
    
    def _update_stats(self, stat_type: str):
        """Update interface creation statistics."""
        self._loading_stats[stat_type] += 1
    
    def get_creation_stats(self) -> Dict[str, int]:
        """Get interface creation statistics."""
        return self._loading_stats.copy()
    
    def clear_cache(self):
        """Clear all caches."""
        self._interface_cache.clear()
        self.ui_loader.clear_cache()
        self.logger.info("Cleared all interface factory caches")
    
    def validate_interface_availability(self, interface_type: str) -> Dict[str, Any]:
        """
        Validate interface availability and provide detailed analysis.
        
        Args:
            interface_type: Type of interface to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'interface_type': interface_type,
            'ui_file_available': False,
            'ui_file_path': None,
            'ui_file_valid': False,
            'hand_coded_available': False,
            'recommended_mode': None,
            'issues': [],
            'recommendations': []
        }
        
        # Use the UI loader's validation
        ui_result = self.ui_loader.validate_ui_availability(interface_type)
        
        result.update({
            'ui_file_available': ui_result['ui_file_available'],
            'ui_file_path': ui_result['ui_file_path'],
            'ui_file_valid': ui_result['ui_file_valid'],
            'hand_coded_available': ui_result['hand_coded_available'],
            'recommended_mode': ui_result['recommended_mode']
        })
        
        result['issues'].extend(ui_result['issues'])
        result['recommendations'].extend(ui_result['recommendations'])
        
        return result


def main():
    """Test the interface factory."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create interface factory with UI files mode (hardcoded)
    config = UIConfig()
    # Mode is hardcoded to use .ui files only
    
    factory = InterfaceFactory(config)
    
    # Test creating main window
    widget = factory.create_interface("mainwindow")
    if widget:
        widget.show()
        sys.exit(app.exec())
    else:
        print("Failed to create interface")
        sys.exit(1)


if __name__ == "__main__":
    main()
