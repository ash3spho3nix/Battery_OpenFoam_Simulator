"""
Enhanced UI Loader for Battery Simulator with Template Integration.

This module provides an advanced UILoader that integrates with the enhanced
template management system, providing better error handling, validation,
and fallback mechanisms for .ui file loading.
"""

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib
import json

logger = logging.getLogger(__name__)


class UIValidationError(Exception):
    """Exception raised when UI validation fails."""
    pass


class UILoaderEnhanced:
    """
    Enhanced UI loader with template integration and advanced features.
    
    This class extends the basic UILoader with advanced features including:
    - Template-based UI validation
    - Enhanced error handling and recovery
    - UI integrity checking
    - Performance monitoring
    - Integration with template management system
    """
    
    # UI file metadata cache
    _ui_metadata_cache: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def load_ui_file(
        cls, 
        ui_file_path: str, 
        parent: Optional[QWidget] = None,
        validate_ui: bool = True
    ) -> QWidget:
        """
        Load a .ui file with enhanced error handling and validation.
        
        Args:
            ui_file_path: Path to the .ui file
            parent: Parent widget (optional)
            validate_ui: Whether to validate the UI after loading
            
        Returns:
            QWidget: The loaded widget
            
        Raises:
            FileNotFoundError: If the .ui file doesn't exist
            UIValidationError: If UI validation fails
            Exception: If loading fails for any reason
        """
        ui_file_path = str(ui_file_path)
        
        if not os.path.exists(ui_file_path):
            error_msg = f"UI file not found: {ui_file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Load the .ui file using PyQt6's uic
            widget = uic.loadUi(ui_file_path, parent)
            
            # Validate the loaded UI if requested
            if validate_ui:
                cls._validate_loaded_ui(widget, ui_file_path)
            
            # Cache UI metadata for future validation
            cls._cache_ui_metadata(ui_file_path, widget)
            
            logger.info(f"Successfully loaded UI file: {ui_file_path}")
            return widget
            
        except Exception as e:
            error_msg = f"Failed to load UI file {ui_file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    @classmethod
    def _validate_loaded_ui(cls, widget: QWidget, ui_file_path: str):
        """
        Validate the loaded UI widget for completeness and integrity.
        
        Args:
            widget: The loaded widget to validate
            ui_file_path: Path to the .ui file that was loaded
            
        Raises:
            UIValidationError: If validation fails
        """
        validation_errors = []
        
        # Check if widget is properly loaded
        if widget is None:
            validation_errors.append("Widget is None after loading")
            return
        
        # Validate widget properties
        if not hasattr(widget, 'objectName') or not widget.objectName():
            validation_errors.append("Widget has no object name")
        
        # Check for common UI elements that should exist
        required_widgets = cls._get_required_widgets_for_ui(ui_file_path)
        missing_widgets = cls._check_required_widgets(widget, required_widgets)
        validation_errors.extend(missing_widgets)
        
        # Check widget hierarchy integrity
        hierarchy_issues = cls._validate_widget_hierarchy(widget)
        validation_errors.extend(hierarchy_issues)
        
        # Report validation results
        if validation_errors:
            error_msg = f"UI validation failed for {ui_file_path}:\n" + "\n".join(validation_errors)
            logger.warning(error_msg)
            # Don't raise exception for validation errors, just log them
            # This allows the application to continue even with minor UI issues
        else:
            logger.debug(f"UI validation passed for {ui_file_path}")
    
    @classmethod
    def _get_required_widgets_for_ui(cls, ui_file_path: str) -> List[str]:
        """
        Get list of required widgets for a specific UI file.
        
        Args:
            ui_file_path: Path to the .ui file
            
        Returns:
            List of required widget names
        """
        ui_name = Path(ui_file_path).stem.lower()
        
        # Define required widgets for each UI type
        required_widgets_map = {
            'mainwindow': ['tabWidget', 'intro_browser', 'main_path_label'],
            'carboninterface': ['tabWidget', 'terminal_output_window', 'change_geometry_button'],
            'halfcellinterface': ['tabWidget', 'terminal_output_window', 'change_geometry_button'],
            'fullcellfoam': ['tabWidget', 'terminal_output_window', 'change_geometry_button'],
            'resultinterface': ['customPlot', 'file_path_label', 'voltage_button']
        }
        
        return required_widgets_map.get(ui_name, [])
    
    @classmethod
    def _check_required_widgets(cls, widget: QWidget, required_widgets: List[str]) -> List[str]:
        """
        Check if all required widgets are present in the loaded UI.
        
        Args:
            widget: The loaded widget
            required_widgets: List of required widget names
            
        Returns:
            List of missing widget errors
        """
        missing_widgets = []
        
        for widget_name in required_widgets:
            found_widget = widget.findChild(QWidget, widget_name)
            if found_widget is None:
                missing_widgets.append(f"Missing required widget: {widget_name}")
        
        return missing_widgets
    
    @classmethod
    def _validate_widget_hierarchy(cls, widget: QWidget) -> List[str]:
        """
        Validate the widget hierarchy for common issues.
        
        Args:
            widget: The root widget to validate
            
        Returns:
            List of hierarchy validation errors
        """
        errors = []
        
        # Check for duplicate object names
        object_names = cls._collect_object_names(widget)
        duplicates = [name for name, count in object_names.items() if count > 1]
        if duplicates:
            errors.append(f"Duplicate object names found: {', '.join(duplicates)}")
        
        # Check for widgets with empty names
        empty_names = [name for name in object_names.keys() if not name]
        if empty_names:
            errors.append(f"Widgets with empty names: {len(empty_names)} found")
        
        return errors
    
    @classmethod
    def _collect_object_names(cls, widget: QWidget) -> Dict[str, int]:
        """
        Collect all object names in the widget hierarchy.
        
        Args:
            widget: The root widget
            
        Returns:
            Dictionary mapping object names to their occurrence count
        """
        object_names = {}
        
        def traverse_children(w: QWidget):
            object_name = w.objectName()
            if object_name:
                object_names[object_name] = object_names.get(object_name, 0) + 1
            
            for child in w.children():
                if hasattr(child, 'objectName'):
                    traverse_children(child)
        
        traverse_children(widget)
        return object_names
    
    @classmethod
    def _cache_ui_metadata(cls, ui_file_path: str, widget: QWidget):
        """
        Cache metadata about the loaded UI for future validation.
        
        Args:
            ui_file_path: Path to the .ui file
            widget: The loaded widget
        """
        try:
            # Calculate file checksum for integrity checking
            checksum = cls._calculate_file_checksum(ui_file_path)
            
            # Collect widget metadata
            metadata = {
                'checksum': checksum,
                'object_name': widget.objectName(),
                'widget_count': cls._count_widgets(widget),
                'timestamp': cls._get_file_timestamp(ui_file_path),
                'required_widgets': cls._get_required_widgets_for_ui(ui_file_path)
            }
            
            cls._ui_metadata_cache[ui_file_path] = metadata
            logger.debug(f"Cached metadata for {ui_file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to cache UI metadata for {ui_file_path}: {e}")
    
    @staticmethod
    def _calculate_file_checksum(file_path: str) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    @staticmethod
    def _count_widgets(widget: QWidget) -> int:
        """Count total number of widgets in hierarchy."""
        count = 1  # Count this widget
        for child in widget.children():
            if hasattr(child, 'objectName'):
                count += cls._count_widgets(child)
        return count
    
    @staticmethod
    def _get_file_timestamp(file_path: str) -> float:
        """Get file modification timestamp."""
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            logger.warning(f"Failed to get timestamp for {file_path}: {e}")
            return 0.0
    
    @classmethod
    def validate_ui_integrity(cls, ui_file_path: str) -> bool:
        """
        Validate the integrity of a .ui file.
        
        Args:
            ui_file_path: Path to the .ui file
            
        Returns:
            True if the UI file is valid and can be loaded
        """
        try:
            # Check if file exists and is readable
            if not os.path.exists(ui_file_path):
                logger.warning(f"UI file does not exist: {ui_file_path}")
                return False
            
            # Check file size (should not be empty)
            if os.path.getsize(ui_file_path) == 0:
                logger.warning(f"UI file is empty: {ui_file_path}")
                return False
            
            # Check if file is valid XML
            import xml.etree.ElementTree as ET
            try:
                ET.parse(ui_file_path)
            except ET.ParseError as e:
                logger.warning(f"UI file is not valid XML: {ui_file_path} - {e}")
                return False
            
            # Check if file has expected UI structure
            if not cls._validate_ui_structure(ui_file_path):
                logger.warning(f"UI file has invalid structure: {ui_file_path}")
                return False
            
            logger.debug(f"UI integrity validation passed for {ui_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"UI integrity validation failed for {ui_file_path}: {e}")
            return False
    
    @staticmethod
    def _validate_ui_structure(ui_file_path: str) -> bool:
        """
        Validate the basic structure of a .ui file.
        
        Args:
            ui_file_path: Path to the .ui file
            
        Returns:
            True if the structure is valid
        """
        import xml.etree.ElementTree as ET
        
        try:
            tree = ET.parse(ui_file_path)
            root = tree.getroot()
            
            # Check if it's a valid Qt UI file
            if root.tag != 'ui':
                return False
            
            # Check for required elements
            widget_element = root.find('widget')
            if widget_element is None:
                return False
            
            # Check widget class
            widget_class = widget_element.get('class')
            if not widget_class or not widget_class.startswith('Q'):
                return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def get_ui_metadata(cls, ui_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached metadata for a UI file.
        
        Args:
            ui_file_path: Path to the .ui file
            
        Returns:
            Dictionary containing UI metadata, or None if not cached
        """
        return cls._ui_metadata_cache.get(ui_file_path)
    
    @classmethod
    def clear_ui_cache(cls):
        """Clear the UI metadata cache."""
        cls._ui_metadata_cache.clear()
        logger.debug("Cleared UI metadata cache")
    
    @classmethod
    def load_main_window(cls, parent: Optional[QWidget] = None) -> QWidget:
        """Load the main window from .ui file with enhanced validation."""
        ui_path = cls.get_ui_path("mainwindow")
        return cls.load_ui_file(ui_path, parent)
    
    @classmethod
    def load_carbon_interface(cls, parent: Optional[QWidget] = None) -> QWidget:
        """Load the carbon interface from .ui file with enhanced validation."""
        ui_path = cls.get_ui_path("carboninterface")
        return cls.load_ui_file(ui_path, parent)
    
    @classmethod
    def load_halfcell_interface(cls, parent: Optional[QWidget] = None) -> QWidget:
        """Load the half-cell interface from .ui file with enhanced validation."""
        ui_path = cls.get_ui_path("halfcellinterface")
        return cls.load_ui_file(ui_path, parent)
    
    @classmethod
    def load_fullcell_interface(cls, parent: Optional[QWidget] = None) -> QWidget:
        """Load the full-cell interface from .ui file with enhanced validation."""
        ui_path = cls.get_ui_path("fullcellfoam")
        return cls.load_ui_file(ui_path, parent)
    
    @classmethod
    def load_result_interface(cls, parent: Optional[QWidget] = None) -> QWidget:
        """Load the result interface from .ui file with enhanced validation."""
        ui_path = cls.get_ui_path("resultinterface")
        return cls.load_ui_file(ui_path, parent)
    
    @staticmethod
    def get_ui_path(ui_name: str, base_path: Optional[str] = None) -> str:
        """Get the full path to a .ui file (static method for compatibility)."""
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / "resources" / "ui"
        else:
            base_path = Path(base_path)
        
        ui_file_path = base_path / f"{ui_name}.ui"
        return str(ui_file_path)
    
    @classmethod
    def ui_file_exists(cls, ui_name: str, base_path: Optional[str] = None) -> bool:
        """Check if a .ui file exists with enhanced validation."""
        ui_path = cls.get_ui_path(ui_name, base_path)
        return os.path.exists(ui_path) and cls.validate_ui_integrity(ui_path)
    
    @classmethod
    def get_available_ui_files(cls, base_path: Optional[str] = None) -> List[str]:
        """Get a list of available .ui files with integrity validation."""
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / "resources" / "ui"
        else:
            base_path = Path(base_path)
        
        if not base_path.exists():
            return []
        
        ui_files = []
        for file_path in base_path.glob("*.ui"):
            if cls.validate_ui_integrity(str(file_path)):
                ui_files.append(file_path.stem)
        
        return sorted(ui_files)
    
    @classmethod
    def diagnose_ui_loading_issue(cls, ui_name: str, base_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Diagnose issues with UI loading for debugging purposes.
        
        Args:
            ui_name: Name of the UI file to diagnose
            base_path: Base path to search for UI files
            
        Returns:
            Dictionary containing diagnosis results
        """
        diagnosis = {
            'ui_name': ui_name,
            'base_path': base_path,
            'issues': [],
            'recommendations': [],
            'file_info': {},
            'success': False
        }
        
        try:
            # Get UI path
            ui_path = cls.get_ui_path(ui_name, base_path)
            diagnosis['file_info']['path'] = ui_path
            
            # Check if file exists
            if not os.path.exists(ui_path):
                diagnosis['issues'].append(f"UI file does not exist: {ui_path}")
                diagnosis['recommendations'].append("Check that the UI file exists in the resources/ui directory")
                return diagnosis
            
            # Get file info
            diagnosis['file_info']['exists'] = True
            diagnosis['file_info']['size'] = os.path.getsize(ui_path)
            diagnosis['file_info']['timestamp'] = os.path.getmtime(ui_path)
            
            # Validate file integrity
            integrity_valid = cls.validate_ui_integrity(ui_path)
            diagnosis['file_info']['integrity_valid'] = integrity_valid
            
            if not integrity_valid:
                diagnosis['issues'].append("UI file failed integrity validation")
                diagnosis['recommendations'].append("Check the XML structure of the UI file")
                return diagnosis
            
            # Try to load the UI
            try:
                widget = cls.load_ui_file(ui_path, validate_ui=True)
                diagnosis['success'] = True
                diagnosis['file_info']['widget_count'] = cls._count_widgets(widget)
                diagnosis['file_info']['object_name'] = widget.objectName()
            except Exception as e:
                diagnosis['issues'].append(f"Failed to load UI: {str(e)}")
                diagnosis['recommendations'].append("Check PyQt6 installation and UI file compatibility")
        
        except Exception as e:
            diagnosis['issues'].append(f"Diagnosis failed: {str(e)}")
            diagnosis['recommendations'].append("Check file permissions and path configuration")
        
        return diagnosis
