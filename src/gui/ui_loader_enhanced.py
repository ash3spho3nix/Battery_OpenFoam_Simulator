#!/usr/bin/env python3
"""
Enhanced UI Loader Module - Multi-Mode UI Loading with Fallback Support.

This module provides an enhanced UI loading system that supports all three
loading modes (AUTO_DETECT, UI_FILES, HAND_CODED) with robust fallback
mechanisms, comprehensive error handling, and detailed logging.
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, Union
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QMetaObject
from PyQt6.QtGui import QGuiApplication
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMessageBox

from .ui_config_enhanced import EnhancedUIConfig, UILoadingMode


class UILoadingError(Exception):
    """Custom exception for UI loading errors."""
    pass


class UIValidationError(Exception):
    """Custom exception for UI validation errors."""
    pass


class UIProgressTracker(QObject):
    """
    Progress tracker for UI loading operations.
    
    Provides real-time feedback on UI loading progress with detailed
    status updates and error reporting.
    """
    
    # Signals for progress tracking
    loading_started = pyqtSignal(str)           # ui_name
    loading_progress = pyqtSignal(int, int)     # current, total
    loading_completed = pyqtSignal(bool, str)   # success, message
    error_occurred = pyqtSignal(str, str)       # error_type, message
    
    def __init__(self, parent=None):
        """Initialize the progress tracker."""
        super().__init__(parent)
        self.loading_session_active = False
        self.current_operation = ""
        
    def start_loading(self, operation_name: str):
        """Start a new loading operation."""
        self.loading_session_active = True
        self.current_operation = operation_name
        self.loading_started.emit(operation_name)
        
    def update_progress(self, current: int, total: int):
        """Update loading progress."""
        if self.loading_session_active:
            self.loading_progress.emit(current, total)
            
    def complete_loading(self, success: bool, message: str = ""):
        """Complete the loading operation."""
        if self.loading_session_active:
            self.loading_completed.emit(success, message)
            self.loading_session_active = False
            self.current_operation = ""
            
    def report_error(self, error_type: str, message: str):
        """Report an error during loading."""
        self.error_occurred.emit(error_type, message)


class EnhancedUILoader:
    """
    Enhanced UI loader with multi-mode support and fallback mechanisms.
    
    This loader supports three modes:
    1. AUTO_DETECT: Try .ui files first, fallback to hand-coded
    2. UI_FILES: Force .ui file loading
    3. HAND_CODED: Force hand-coded widgets
    
    Features:
    - Comprehensive error handling and recovery
    - Detailed logging and progress tracking
    - Widget validation and integrity checking
    - Automatic fallback with user notification
    - Performance monitoring and caching
    """
    
    # Class-level caches for performance
    _ui_file_cache: Dict[str, Path] = {}
    _widget_count_cache: Dict[str, int] = {}
    _last_modified_cache: Dict[str, float] = {}
    _interface_cache: Dict[str, QWidget] = {}
    
    # Statistics tracking
    _loading_stats = {
        'total_attempts': 0,
        'ui_success': 0,
        'hand_coded_success': 0,
        'fallbacks': 0,
        'failures': 0
    }
    UIConfig=EnhancedUIConfig()
    
    def __init__(self, ui_config: Optional[UIConfig] = None):
        """
        Initialize the enhanced UI loader.
        
        Args:
            ui_config: UI configuration for loading mode
        """
        self.ui_config = ui_config or EnhancedUIConfig()
        self.logger = logging.getLogger(__name__)
        self.progress_tracker = UIProgressTracker()
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup detailed logging for UI loading operations."""
        self.logger = logging.getLogger(f"{__name__}.EnhancedUILoader")
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
            log_file = Path(__file__).parent.parent / "logs" / "ui_loading.log"
            log_file.parent.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def load_ui(
        self, 
        ui_name: str, 
        parent: Optional[QWidget] = None,
        use_cache: bool = True
    ) -> Optional[QWidget]:
        """
        Load a UI using the configured loading mode with fallback support.
        
        Args:
            ui_name: Name of the UI to load (without .ui extension)
            parent: Parent widget
            use_cache: Whether to use cached interfaces
            
        Returns:
            Loaded widget or None if loading failed
            
        Raises:
            UILoadingError: If loading fails in UI_FILES mode
            UIValidationError: If UI validation fails
        """
        # Remove .ui extension if present
        if ui_name.endswith('.ui'):
            ui_name = ui_name[:-3]
            
        self.logger.info(f"Starting UI loading for: {ui_name}")
        self.logger.info(f"Loading mode: {self.ui_config.mode.name}")
        
        # Check cache first
        if use_cache and self.ui_config.mode != UILoadingMode.UI_FILES:
            cached = self._get_cached_interface(ui_name)
            if cached:
                self.logger.info(f"Using cached interface for: {ui_name}")
                return cached
        
        # Start progress tracking
        self.progress_tracker.start_loading(f"Loading {ui_name}")
        
        try:
            # Determine loading strategy based on mode
            if self.ui_config.mode == UILoadingMode.UI_FILES:
                widget = self._load_ui_files_only(ui_name, parent)
            elif self.ui_config.mode == UILoadingMode.HAND_CODED:
                widget = self._load_hand_coded_only(ui_name, parent)
            else:  # AUTO_DETECT
                widget = self._load_auto_detect(ui_name, parent)
            
            if widget:
                # Validate the loaded widget
                self._validate_widget_integrity(widget, ui_name)
                
                # Cache the widget if successful
                if use_cache:
                    self._cache_interface(ui_name, widget)
                
                self.logger.info(f"Successfully loaded UI: {ui_name}")
                self.progress_tracker.complete_loading(True, f"Loaded {ui_name} successfully")
                return widget
            else:
                raise UILoadingError(f"Failed to load UI: {ui_name}")
                
        except Exception as e:
            self.logger.error(f"UI loading failed for {ui_name}: {e}", exc_info=True)
            self.progress_tracker.report_error("Loading Error", str(e))
            self.progress_tracker.complete_loading(False, f"Failed to load {ui_name}")
            
            # Update statistics
            self._update_stats('failures')
            
            # In UI_FILES mode, re-raise the exception
            if self.ui_config.mode == UILoadingMode.UI_FILES:
                raise
            
            return None
    
    def _load_auto_detect(
        self, 
        ui_name: str, 
        parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """
        Load UI using auto-detect mode: try .ui files first, fallback to hand-coded.
        
        Args:
            ui_name: Name of the UI to load
            parent: Parent widget
            
        Returns:
            Loaded widget or None if both methods fail
        """
        self.logger.info(f"Auto-detect mode: trying .ui file for {ui_name}")
        
        # Try .ui file first
        try:
            widget = self._load_ui_file(ui_name, parent)
            if widget:
                self.logger.info(f"Auto-detect: successfully loaded .ui file for {ui_name}")
                self._update_stats('ui_success')
                return widget
        except Exception as e:
            self.logger.warning(f"Auto-detect: .ui file loading failed for {ui_name}: {e}")
        
        # Fallback to hand-coded
        self.logger.info(f"Auto-detect: falling back to hand-coded for {ui_name}")
        try:
            widget = self._load_hand_coded(ui_name, parent)
            if widget:
                self.logger.info(f"Auto-detect: successfully loaded hand-coded for {ui_name}")
                self._update_stats('fallbacks')
                self._update_stats('hand_coded_success')
                
                # Notify user about fallback
                self._notify_fallback(ui_name)
                return widget
        except Exception as e:
            self.logger.error(f"Auto-detect: hand-coded loading also failed for {ui_name}: {e}")
        
        return None
    
    def _load_ui_files_only(
        self, 
        ui_name: str, 
        parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """
        Load UI using only .ui files (no fallback).
        
        Args:
            ui_name: Name of the UI to load
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading fails
            
        Raises:
            UILoadingError: If .ui file loading fails
        """
        try:
            widget = self._load_ui_file(ui_name, parent)
            if widget:
                self._update_stats('ui_success')
                return widget
            else:
                raise UILoadingError(f"UI file not found or invalid: {ui_name}")
        except Exception as e:
            self.logger.error(f"UI_FILES mode: failed to load {ui_name}: {e}")
            raise UILoadingError(f"UI_FILES mode: {e}")
    
    def _load_hand_coded_only(
        self, 
        ui_name: str, 
        parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """
        Load UI using only hand-coded widgets (no fallback).
        
        Args:
            ui_name: Name of the UI to load
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading fails
            
        Raises:
            UILoadingError: If hand-coded loading fails
        """
        try:
            widget = self._load_hand_coded(ui_name, parent)
            if widget:
                self._update_stats('hand_coded_success')
                return widget
            else:
                raise UILoadingError(f"Hand-coded interface not found: {ui_name}")
        except Exception as e:
            self.logger.error(f"HAND_CODED mode: failed to load {ui_name}: {e}")
            raise UILoadingError(f"HAND_CODED mode: {e}")
    
    def _load_ui_file(
        self, 
        ui_name: str, 
        parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """
        Load a UI file directly.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading fails
        """
        ui_path = self._get_ui_path(ui_name)
        
        if not ui_path or not ui_path.exists():
            self.logger.warning(f"UI file not found: {ui_path}")
            return None
        
        # Validate UI file integrity
        if not self._validate_ui_file(ui_path):
            self.logger.warning(f"UI file validation failed: {ui_path}")
            return None
        
        try:
            # Load the UI file as a new widget, without a base instance.
            # The parent will be set later if needed.
            widget = loadUi(str(ui_path))
            
            if widget:
                # If a parent was provided, set it now.
                if parent:
                    widget.setParent(parent)
            
            if widget:
                self.logger.info(f"Successfully loaded UI file: {ui_path}")
                return widget
            else:
                self.logger.error(f"Failed to load UI file: {ui_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading UI file {ui_path}: {e}")
            return None
    
    def _load_hand_coded(
        self, 
        ui_name: str, 
        parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """
        Load a hand-coded interface.
        
        Args:
            ui_name: Name of the interface to load
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading fails
        """
        # Map UI names to interface classes
        interface_map = {
            'mainwindow': 'MainWindow',
            'carboninterface': 'CarbonInterface',
            'halfcellinterface': 'HalfCellInterface',
            'fullcellfoam': 'FullCellInterface',
            'resultinterface': 'ResultInterface'
        }
        
        interface_class_name = interface_map.get(ui_name.lower())
        if not interface_class_name:
            self.logger.warning(f"Unknown interface: {ui_name}")
            return None
        
        try:
            # Import the interface module
            if ui_name.lower() == 'mainwindow':
                from src.gui.main_window import MainWindow
                widget = MainWindow(parent=parent, ui_config=self.ui_config)
            elif ui_name.lower() == 'carboninterface':
                from .interfaces.carbon_interface import CarbonInterface
                widget = CarbonInterface(parent=parent, ui_config=self.ui_config)
            elif ui_name.lower() == 'halfcellinterface':
                from .interfaces.halfcell_interface import HalfCellInterface
                widget = HalfCellInterface(parent=parent, ui_config=self.ui_config)
            elif ui_name.lower() == 'fullcellfoam':
                from .interfaces.fullcell_interface import FullCellInterface
                widget = FullCellInterface(parent=parent, ui_config=self.ui_config)
            elif ui_name.lower() == 'resultinterface':
                from .interfaces.result_interface import ResultInterface
                widget = ResultInterface(parent=parent, ui_config=self.ui_config)
            else:
                self.logger.warning(f"No hand-coded interface available for: {ui_name}")
                return None
            
            self.logger.info(f"Successfully loaded hand-coded interface: {ui_name}")
            return widget
            
        except ImportError as e:
            self.logger.error(f"Failed to import hand-coded interface {ui_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create hand-coded interface {ui_name}: {e}")
            return None
    
    def _get_ui_path(self, ui_name: str) -> Optional[Path]:
        """
        Get the full path to a UI file.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            
        Returns:
            Path to the UI file or None if not found
        """
        # Check cache first
        if ui_name in self._ui_file_cache:
            cached_path = self._ui_file_cache[ui_name]
            if cached_path.exists():
                return cached_path
        
        # Construct path based on configuration
        if self.ui_config.ui_base_path:
            ui_path = Path(self.ui_config.ui_base_path) / f"{ui_name}.ui"
        else:
            # Default path: src/resources/ui/files/
            ui_path = Path(__file__).parent.parent / "resources" / "ui" / "files" / f"{ui_name}.ui"
        
        # Validate and cache
        if ui_path.exists():
            self._ui_file_cache[ui_name] = ui_path
            return ui_path
        else:
            self.logger.debug(f"UI file not found at: {ui_path}")
            return None
    
    def _validate_ui_file(self, ui_path: Path) -> bool:
        """
        Validate that a UI file is well-formed XML and contains valid content.
        
        Args:
            ui_path: Path to the UI file
            
        Returns:
            True if the file is valid, False otherwise
        """
        try:
            import xml.etree.ElementTree as ET
            
            # Check file size (should not be empty)
            if ui_path.stat().st_size == 0:
                self.logger.warning(f"UI file is empty: {ui_path}")
                return False
            
            # Parse XML
            tree = ET.parse(ui_path)
            root = tree.getroot()
            
            # Validate root element
            if root.tag != 'ui':
                self.logger.warning(f"Invalid UI file root element: {root.tag}")
                return False
            
            # Check for required elements
            widget_elements = root.findall('.//widget')
            if not widget_elements:
                self.logger.warning(f"No widget elements found in UI file: {ui_path}")
                return False
            
            self.logger.debug(f"UI file validation passed: {ui_path}")
            return True
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in UI file {ui_path}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error validating UI file {ui_path}: {e}")
            return False
    
    def _validate_widget_integrity(self, widget: QWidget, ui_name: str):
        """
        Validate the integrity of a loaded widget.
        
        Args:
            widget: The loaded widget
            ui_name: Name of the UI being loaded
            
        Raises:
            UIValidationError: If validation fails
        """
        try:
            # Check if widget is properly initialized
            if not widget:
                raise UIValidationError(f"Widget is None for {ui_name}")
            
            # Check for basic widget properties
            if not hasattr(widget, 'objectName'):
                raise UIValidationError(f"Widget missing objectName property for {ui_name}")
            
            # Count widgets and validate structure
            widget_count = self._count_widgets(widget)
            self.logger.debug(f"Widget count for {ui_name}: {widget_count}")
            
            # Basic sanity check: should have at least some widgets
            if widget_count < 5:
                self.logger.warning(f"Unusually low widget count for {ui_name}: {widget_count}")
            
            # Store widget count for future reference
            self._widget_count_cache[ui_name] = widget_count
            
        except Exception as e:
            self.logger.error(f"Widget validation failed for {ui_name}: {e}")
            raise UIValidationError(f"Widget validation failed: {e}")
    
    def _count_widgets(self, widget: QWidget) -> int:
        """
        Count the number of widgets in a widget hierarchy.
        
        Args:
            widget: The root widget
            
        Returns:
            Number of widgets in the hierarchy
        """
        count = 1  # Count the widget itself
        for child in widget.findChildren(QWidget):
            count += 1
        return count
    
    def _cache_interface(self, ui_name: str, widget: QWidget):
        """Cache a loaded interface for future use."""
        self._interface_cache[ui_name] = widget
        self.logger.debug(f"Cached interface: {ui_name}")
    
    def _get_cached_interface(self, ui_name: str) -> Optional[QWidget]:
        """Retrieve a cached interface if available."""
        return self._interface_cache.get(ui_name)
    
    def _notify_fallback(self, ui_name: str):
        """Notify user about fallback to hand-coded interface."""
        message = (
            f"UI file loading failed for '{ui_name}'. "
            f"Falling back to hand-coded interface.\n\n"
            f"This may affect the appearance or functionality.\n"
            f"Consider checking the .ui file or using AUTO_DETECT mode."
        )
        
        self.logger.warning(f"Fallback notification for {ui_name}: {message}")
        
        # Show user notification (non-blocking)
        try:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("UI Loading Fallback")
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            msg_box.setModal(False)  # Non-blocking
            msg_box.show()
        except Exception as e:
            self.logger.error(f"Failed to show fallback notification: {e}")
    
    def _update_stats(self, stat_type: str):
        """Update loading statistics."""
        self._loading_stats['total_attempts'] += 1
        self._loading_stats[stat_type] += 1
    
    def get_loading_stats(self) -> Dict[str, int]:
        """Get UI loading statistics."""
        return self._loading_stats.copy()
    
    def clear_cache(self):
        """Clear all caches."""
        self._ui_file_cache.clear()
        self._widget_count_cache.clear()
        self._interface_cache.clear()
        self.logger.info("Cleared all UI loader caches")
    
    def validate_ui_availability(self, ui_name: str) -> Dict[str, Any]:
        """
        Validate UI availability and provide detailed analysis.
        
        Args:
            ui_name: Name of the UI to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'ui_name': ui_name,
            'ui_file_available': False,
            'ui_file_path': None,
            'ui_file_valid': False,
            'hand_coded_available': False,
            'recommended_mode': None,
            'issues': [],
            'recommendations': []
        }
        
        # Check .ui file
        ui_path = self._get_ui_path(ui_name)
        if ui_path and ui_path.exists():
            result['ui_file_available'] = True
            result['ui_file_path'] = str(ui_path)
            result['ui_file_valid'] = self._validate_ui_file(ui_path)
            
            if not result['ui_file_valid']:
                result['issues'].append("UI file exists but is invalid or corrupted")
                result['recommendations'].append("Check and fix the .ui file")
        
        # Check hand-coded interface
        try:
            hand_coded_widget = self._load_hand_coded(ui_name, None)
            result['hand_coded_available'] = hand_coded_widget is not None
            if hand_coded_widget:
                hand_coded_widget.deleteLater()  # Clean up
        except Exception as e:
            result['issues'].append(f"Hand-coded interface error: {e}")
        
        # Determine recommended mode
        if result['ui_file_available'] and result['ui_file_valid']:
            result['recommended_mode'] = 'UI_FILES'
        elif result['hand_coded_available']:
            result['recommended_mode'] = 'HAND_CODED'
        else:
            result['recommended_mode'] = 'NONE'
            result['issues'].append("No valid UI implementation found")
            result['recommendations'].append("Create either a .ui file or hand-coded interface")
        
        return result


# Backward compatibility alias
UILoaderEnhanced = EnhancedUILoader


def main():
    """Test the enhanced UI loader."""
    app = QApplication(sys.argv)
    
    # Create enhanced loader with auto-detect mode
    config = EnhancedUIConfig()
    config.mode = UILoadingMode.AUTO_DETECT
    
    loader = EnhancedUILoader(config)
    
    # Test loading main window
    widget = loader.load_ui("mainwindow")
    if widget:
        widget.show()
        sys.exit(app.exec())
    else:
        print("Failed to load UI")
        sys.exit(1)


if __name__ == "__main__":
    main()
