#!/usr/bin/env python3
"""
Interface Factory for Battery Simulator with Multi-Mode UI Loading Support.

This module provides an InterfaceFactory that supports all three UI loading modes:
- AUTO_DETECT: Try .ui files, fallback to hand-coded
- UI_FILES: Force .ui file loading
- HAND_CODED: Force hand-coded widgets

It provides robust error handling, caching, and proper interface lifecycle management.
"""

import sys
import logging
import traceback
from typing import Optional, Dict, Any, List, Type, Union
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)


class InterfaceCreationError(Exception):
    """Exception raised when interface creation fails."""
    pass


class InterfaceFactory:
    """
    Interface factory for multi-mode UI loading with robust error handling.
    
    This factory provides:
    - Support for all three UI loading modes (AUTO_DETECT, UI_FILES, HAND_CODED)
    - Robust error handling and user-friendly messages
    - Interface caching for performance
    - Proper signal/slot management
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
        Create an interface with support for all UI loading modes.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell, result)
            parent: Parent widget
            ui_config: UI configuration (supports all modes)
            use_cache: Whether to use cached interfaces
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If interface creation fails
        """
        start_time = cls._get_timestamp()
        
        # Get or create UI configuration
        ui_config = ui_config or cls._get_default_ui_config()
        logger.info(f"Creating interface: {interface_type} with mode: {ui_config.mode.name}")
        
        # Check cache if enabled
        if use_cache:
            cached = cls._get_cached_interface(interface_type, ui_config)
            if cached:
                logger.info(f"Using cached interface for {interface_type}")
                return cached
        
        # Create interface based on UI mode
        interface = cls._create_interface_by_mode(
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
    def _create_interface_by_mode(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface based on the specified UI mode.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If interface creation fails
        """
        if ui_config.mode.name == 'UI_FILES':
            return cls._create_interface_from_ui(interface_type, parent, ui_config)
        elif ui_config.mode.name == 'HAND_CODED':
            return cls._create_interface_hand_coded(interface_type, parent, ui_config)
        else:  # AUTO_DETECT
            return cls._create_interface_auto_detect(interface_type, parent, ui_config)
    
    @classmethod
    def _create_interface_from_ui(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface by loading from .ui file.
        
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
    
    @classmethod
    def _create_interface_hand_coded(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface using hand-coded widgets.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If hand-coded creation fails
        """
        try:
            # Import the appropriate interface class
            if interface_type == "carbon":
                from src.gui.interfaces.carbon_interface import CarbonInterface
                interface = CarbonInterface(parent=parent, ui_config=ui_config)
            elif interface_type == "halfcell":
                from src.gui.interfaces.halfcell_interface import HalfCellInterface
                interface = HalfCellInterface(parent=parent, ui_config=ui_config)
            elif interface_type == "fullcell":
                from src.gui.interfaces.fullcell_interface import FullCellInterface
                interface = FullCellInterface(parent=parent, ui_config=ui_config)
            elif interface_type == "result":
                from src.gui.interfaces.result_interface import ResultInterface
                interface = ResultInterface(parent=parent, ui_config=ui_config)
            else:
                raise ValueError(f"Unknown interface type: {interface_type}")
            
            logger.info(f"Successfully created hand-coded interface: {interface_type}")
            return interface
            
        except Exception as e:
            error_msg = f"Failed to create hand-coded interface {interface_type}: {e}"
            logger.error(error_msg)
            QMessageBox.critical(
                parent,
                "Interface Creation Error",
                f"Failed to create the interface.\n\n"
                f"Interface: {interface_type}\n"
                f"Error: {str(e)}\n\n"
                "Please check the application files and try again."
            )
            cls._update_creation_stats('failures')
            raise InterfaceCreationError(error_msg)
    
    @classmethod
    def _create_interface_auto_detect(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface using auto-detect mode (try .ui first, fallback to hand-coded).
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If both .ui and hand-coded creation fail
        """
        # Try .ui file first
        try:
            return cls._create_interface_from_ui(interface_type, parent, ui_config)
        except InterfaceCreationError as e:
            logger.warning(f"UI file loading failed, falling back to hand-coded: {e}")
            
            # Fallback to hand-coded
            try:
                return cls._create_interface_hand_coded(interface_type, parent, ui_config)
            except InterfaceCreationError as e2:
                error_msg = f"Both UI file and hand-coded creation failed for {interface_type}: {e2}"
                logger.error(error_msg)
                QMessageBox.critical(
                    parent,
                    "Interface Creation Error",
                    f"Failed to create the interface using both methods.\n\n"
                    f"Interface: {interface_type}\n"
                    f"UI Error: {e}\n"
                    f"Hand-coded Error: {e2}\n\n"
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
            
            # Test hand-coded interface creation
            diagnosis['test_results']['hand_coded_available'] = cls._test_hand_coded(interface_type, ui_config)
            
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
            from src.gui.ui_loader import UiLoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UiLoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            results['file_exists'] = os.path.exists(ui_path)
            results['integrity_valid'] = UiLoader.validate_ui_integrity(ui_path) if results['file_exists'] else False
            results['path'] = ui_path
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @classmethod
    def _test_hand_coded(cls, interface_type: str, ui_config: Optional['UIConfig']) -> Dict[str, Any]:
        """Test hand-coded interface creation."""
        results = {'import_successful': False, 'creation_successful': False}
        
        try:
            # Test import
            if interface_type == "carbon":
                from src.gui.interfaces.carbon_interface import CarbonInterface
            elif interface_type == "halfcell":
                from src.gui.interfaces.halfcell_interface import HalfCellInterface
            elif interface_type == "fullcell":
                from src.gui.interfaces.fullcell_interface import FullCellInterface
            elif interface_type == "result":
                from src.gui.interfaces.result_interface import ResultInterface
            else:
                results['error'] = f"Unknown interface type: {interface_type}"
                return results
            
            results['import_successful'] = True
            
            # Test creation (without parent to avoid UI issues)
            if interface_type == "carbon":
                interface = CarbonInterface(parent=None, ui_config=ui_config)
            elif interface_type == "halfcell":
                interface = HalfCellInterface(parent=None, ui_config=ui_config)
            elif interface_type == "fullcell":
                interface = FullCellInterface(parent=None, ui_config=ui_config)
            elif interface_type == "result":
                interface = ResultInterface(parent=None, ui_config=ui_config)
            
            results['creation_successful'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @classmethod
    def _analyze_diagnosis_results(cls, diagnosis: Dict[str, Any]):
        """Analyze diagnosis results and provide recommendations."""
        test_results = diagnosis['test_results']
        
        # Check for common issues
        ui_available = test_results.get('ui_files_available', {}).get('file_exists', False)
        hand_coded_available = test_results.get('hand_coded_available', {}).get('creation_successful', False)
        
        if not ui_available and not hand_coded_available:
            diagnosis['issues'].append("No valid interface creation method available")
            diagnosis['recommendations'].append("Check that either UI files or interface classes exist")
        
        if not ui_available:
            diagnosis['issues'].append("UI files not found in expected location")
            diagnosis['recommendations'].append("Check that UI files exist in resources/ui directory")
        
        if not hand_coded_available:
            diagnosis['issues'].append("Hand-coded interface creation failed")
            diagnosis['recommendations'].append("Check that interface classes are properly implemented")
        
        # Provide specific recommendations based on available options
        if ui_available and hand_coded_available:
            diagnosis['recommendations'].append("Both UI files and hand-coded interfaces available")
            diagnosis['recommendations'].append("Use AUTO_DETECT mode for best compatibility")
        elif ui_available:
            diagnosis['recommendations'].append("Use UI_FILES mode for best results")
        elif hand_coded_available:
            diagnosis['recommendations'].append("Use HAND_CODED mode")
        
        if not diagnosis['issues']:
            diagnosis['recommendations'].append("No issues detected - interface should load successfully")
        else:
            diagnosis['recommendations'].append("Check application configuration and dependencies")
    
    @classmethod
    def create_interface_with_validation(
        cls,
        interface_type: str,
        parent: Optional[QWidget] = None,
        ui_config: Optional['UIConfig'] = None,
        project_path: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> QWidget:
        """
        Create interface with validation and proper initialization.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            project_path: Project path for initialization
            project_name: Project name for initialization
            
        Returns:
            QWidget: The created and validated interface
            
        Raises:
            InterfaceCreationError: If interface creation or validation fails
        """
        try:
            # Create interface
            interface = cls.create_interface(interface_type, parent, ui_config)
            
            # Set project paths if provided
            if project_path and project_name and hasattr(interface, 'set_project_paths'):
                success = interface.set_project_paths(project_path, project_name)
                if not success:
                    raise InterfaceCreationError("Failed to set project paths")
            
            # Validate interface
            if hasattr(interface, 'validate_interface'):
                if not interface.validate_interface():
                    raise InterfaceCreationError("Interface validation failed")
            
            logger.info(f"Interface {interface_type} created and validated successfully")
            return interface
            
        except Exception as e:
            logger.error(f"Interface creation with validation failed: {e}", exc_info=True)
            raise InterfaceCreationError(f"Interface creation with validation failed: {e}")
