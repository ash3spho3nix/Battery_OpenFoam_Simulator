"""
Enhanced Interface Factory for Battery Simulator with Direct UI Loading.

This module provides an InterfaceFactory that loads interfaces directly from .ui files
without any fallback to hand-coded widgets. It provides robust error handling and
user-friendly error messages when .ui files are missing or corrupted.
"""

import sys
import logging
import traceback
from typing import Optional, Dict, Any, List, Type, Union
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
import os

logger = logging.getLogger(__name__)


class InterfaceCreationError(Exception):
    """Exception raised when interface creation fails."""
    pass


class InterfaceFactory:
    """
    Interface factory for direct .ui file loading without fallback.
    
    This factory provides direct loading of interfaces from .ui files with:
    - Robust error handling and user-friendly messages
    - Performance monitoring and caching
    - Comprehensive error handling and recovery
    - Integration with UI loading system
    """
    
    # Interface creation cache for performance
    _interface_cache: Dict[str, Dict[str, Any]] = {}
    _creation_stats: Dict[str, int] = {'success': 0, 'failures': 0}
    
    @classmethod
    def create_interface(
        cls,
        interface_type: str,
        parent: Optional[QWidget] = None,
        ui_config: Optional['UIConfig'] = None,
        use_cache: bool = True
    ) -> QWidget:
        """
        Create an interface by loading directly from .ui files.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell, result)
            parent: Parent widget
            ui_config: UI configuration (must be UI_FILES mode)
            use_cache: Whether to use cached interfaces
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If interface creation fails
        """
        start_time = cls._get_timestamp()
        
        # Get or create UI configuration
        ui_config = ui_config or cls._get_default_ui_config()
        logger.info(f"Creating interface: {interface_type} with mode: {ui_config.mode.value}")
        
        # Validate that we're in UI_FILES mode
        if ui_config.mode.value != 'ui_files':
            error_msg = f"InterfaceFactory requires UI_FILES mode, but got {ui_config.mode.value}"
            logger.error(error_msg)
            QMessageBox.critical(
                parent, 
                "Configuration Error", 
                f"Application configuration error: {error_msg}\n\n"
                "Please ensure the application is configured to use .ui files only."
            )
            raise InterfaceCreationError(error_msg)
        
        # Check cache if enabled
        if use_cache:
            cached = cls._get_cached_interface(interface_type, ui_config)
            if cached:
                logger.info(f"Using cached interface for {interface_type}")
                return cached
        
        # Create interface with direct .ui loading
        interface = cls._create_interface_from_ui(
            interface_type, parent, ui_config
        )
        
        # Cache the interface if successful
        if interface and use_cache:
            cls._cache_interface(interface_type, ui_config, interface)
        
        # Update statistics
        cls._update_creation_stats('success')
        
        # Log performance metrics
        creation_time = cls._get_timestamp() - start_time
        logger.info(f"Interface creation completed in {creation_time:.3f}s")
        
        return interface
    
    @classmethod
    def _create_interface_from_ui(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface by loading directly from .ui file.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If .ui file loading fails
        """
        # Get UI name mapping
        ui_name = cls._get_ui_name(interface_type)
        
        # Import UI loader
        from src.gui.ui_loader import UiLoader
        
        # Load UI using UiLoader
        try:
            widget = UiLoader.load_ui(ui_name, parent)
            if widget:
                logger.info(f"Successfully loaded UI: {ui_name}")
                return widget
            else:
                # UI file exists but failed to load
                error_msg = f"Failed to load UI file: {ui_name}.ui"
                logger.error(error_msg)
                QMessageBox.critical(
                    parent,
                    "UI Loading Error",
                    f"Failed to load the user interface.\n\n"
                    f"Interface: {interface_type}\n"
                    f"File: {ui_name}.ui\n\n"
                    "The .ui file may be corrupted or incompatible.\n"
                    "Please check the application files and try again."
                )
                cls._update_creation_stats('failures')
                raise InterfaceCreationError(error_msg)
                
        except Exception as e:
            # UI file doesn't exist or other loading error
            error_msg = f"Failed to load UI {ui_name}: {e}"
            logger.error(error_msg)
            QMessageBox.critical(
                parent,
                "UI Loading Error",
                f"Failed to load the user interface.\n\n"
                f"Interface: {interface_type}\n"
                f"File: {ui_name}.ui\n"
                f"Error: {str(e)}\n\n"
                "The .ui file may be missing or corrupted.\n"
                "Please check the application files and try again."
            )
            cls._update_creation_stats('failures')
            raise InterfaceCreationError(error_msg)
    
    @staticmethod
    def _get_ui_name(interface_type: str) -> str:
        """Get the .ui file name for an interface type."""
        ui_name_map = {
            "carbon": "carboninterface",
            "halfcell": "halfcellinterface",
            "fullcell": "fullcellfoam",
            "result": "resultinterface"
        }
        return ui_name_map.get(interface_type, interface_type)
    
    @classmethod
    def _cache_interface(
        cls,
        interface_type: str,
        ui_config: 'UIConfig',
        interface: QWidget
    ):
        """Cache a created interface for reuse."""
        cache_key = cls._generate_cache_key(interface_type, ui_config)
        cls._interface_cache[cache_key] = {
            'interface': interface,
            'timestamp': cls._get_timestamp(),
            'config': ui_config.to_dict()
        }
        logger.debug(f"Cached interface: {cache_key}")
    
    @classmethod
    def _get_cached_interface(
        cls,
        interface_type: str,
        ui_config: 'UIConfig'
    ) -> Optional[QWidget]:
        """Retrieve a cached interface if available."""
        cache_key = cls._generate_cache_key(interface_type, ui_config)
        cached = cls._interface_cache.get(cache_key)
        
        if cached:
            # Check if cache is still valid (simple time-based invalidation)
            cache_age = cls._get_timestamp() - cached['timestamp']
            if cache_age < 300:  # 5 minutes cache lifetime
                return cached['interface']
            else:
                # Remove expired cache
                del cls._interface_cache[cache_key]
                logger.debug(f"Removed expired cache: {cache_key}")
        
        return None
    
    @staticmethod
    def _generate_cache_key(interface_type: str, ui_config: 'UIConfig') -> str:
        """Generate a cache key for the interface configuration."""
        config_hash = hash(str(sorted(ui_config.to_dict().items())))
        return f"{interface_type}_{config_hash}"
    
    @staticmethod
    def _get_default_ui_config() -> 'UIConfig':
        """Get default UI configuration."""
        from src.gui.ui_config import UIConfig
        return UIConfig()
    
    @staticmethod
    def _get_timestamp() -> float:
        """Get current timestamp for performance monitoring."""
        import time
        return time.time()
    
    @classmethod
    def _update_creation_stats(cls, stat_type: str):
        """Update interface creation statistics."""
        if stat_type in cls._creation_stats:
            cls._creation_stats[stat_type] += 1
    
    @classmethod
    def get_creation_stats(cls) -> Dict[str, int]:
        """Get interface creation statistics."""
        return cls._creation_stats.copy()
    
    @classmethod
    def clear_cache(cls):
        """Clear the interface cache."""
        cls._interface_cache.clear()
        logger.debug("Cleared interface cache")
    
    @classmethod
    def diagnose_interface_creation(
        cls,
        interface_type: str,
        ui_config: Optional['UIConfig'] = None
    ) -> Dict[str, Any]:
        """
        Diagnose interface creation issues for debugging.
        
        Args:
            interface_type: Type of interface to diagnose
            ui_config: UI configuration (optional)
            
        Returns:
            Dictionary containing diagnosis results
        """
        diagnosis = {
            'interface_type': interface_type,
            'config': ui_config.to_dict() if ui_config else {},
            'issues': [],
            'recommendations': [],
            'test_results': {},
            'success': False
        }
        
        try:
            # Test UI file availability
            diagnosis['test_results']['ui_files_available'] = cls._test_ui_files(interface_type, ui_config)
            
            # Analyze results and provide recommendations
            cls._analyze_diagnosis_results(diagnosis)
            
            # Try to create the interface to verify it works
            try:
                interface = cls.create_interface(interface_type, ui_config=ui_config, use_cache=False)
                diagnosis['success'] = True
                diagnosis['recommendations'].append("Interface creation successful")
            except Exception as e:
                diagnosis['issues'].append(f"Interface creation failed: {str(e)}")
                
        except Exception as e:
            diagnosis['issues'].append(f"Diagnosis failed: {str(e)}")
            diagnosis['recommendations'].append("Check application logs for more details")
        
        return diagnosis
    
    @classmethod
    def _test_ui_files(cls, interface_type: str, ui_config: Optional['UIConfig']) -> Dict[str, Any]:
        """Test UI file availability and integrity."""
        results = {'file_exists': False, 'integrity_valid': False, 'path': None}
        
        try:
            # Test UI loader
            from src.gui.ui_loader import UILoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UILoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            results['file_exists'] = os.path.exists(ui_path)
            results['integrity_valid'] = UILoader.validate_ui_integrity(ui_path) if results['file_exists'] else False
            results['path'] = ui_path
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @classmethod
    def _analyze_diagnosis_results(cls, diagnosis: Dict[str, Any]):
        """Analyze diagnosis results and provide recommendations."""
        test_results = diagnosis['test_results']
        
        # Check for common issues
        if not test_results.get('ui_files_available', {}).get('file_exists', False):
            diagnosis['issues'].append("UI files not found in expected location")
            diagnosis['recommendations'].append("Check that UI files exist in resources/ui directory")
        
        # Provide specific recommendations based on test results
        if test_results.get('ui_files_available', {}).get('integrity_valid', False):
            diagnosis['recommendations'].append("Use UI_FILES loading mode for best results")
        else:
            diagnosis['issues'].append("UI file integrity check failed")
            diagnosis['recommendations'].append("Check that UI files are valid and not corrupted")
        
        if not diagnosis['issues']:
            diagnosis['recommendations'].append("No issues detected - interface should load successfully")
        else:
            diagnosis['recommendations'].append("Check application configuration and dependencies")
