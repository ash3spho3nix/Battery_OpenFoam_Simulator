"""
Widget Naming Standardization System for Battery Simulator.

This module provides a comprehensive solution for widget naming standardization
between .ui files and Python code. It implements a flexible widget access pattern
that supports multiple naming conventions and provides automatic fallback mechanisms.

Key Features:
- Multi-convention widget access
- Automatic naming standardization
- Diagnostic tools for widget discovery
- Backward compatibility support
- Comprehensive error handling and logging
"""

import os
import sys
import logging
import inspect
import time
from typing import Optional, Dict, Any, List, Union, Callable
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum


class WidgetNamingError(Exception):
    """Custom exception for widget naming errors."""
    pass


class WidgetAccessMode(Enum):
    """
    Widget access modes for different naming conventions.
    
    Defines how widgets should be accessed:
    - UI_FIRST: Try .ui naming first, then hand-coded
    - CODE_FIRST: Try hand-coded naming first, then .ui
    - UI_ONLY: Only use .ui naming convention
    - CODE_ONLY: Only use hand-coded naming convention
    """
    UI_FIRST = "ui_first"       # Try .ui naming first
    CODE_FIRST = "code_first"   # Try hand-coded naming first
    UI_ONLY = "ui_only"         # Only .ui naming
    CODE_ONLY = "code_only"     # Only hand-coded naming


class WidgetDiagnosticInfo:
    """
    Information about widget discovery and access.
    
    Contains details about widget access attempts and results.
    """
    
    def __init__(self):
        self.access_attempts = []
        self.successful_accesses = []
        self.failed_accesses = []
        self.widget_types = {}
        self.naming_patterns = {}
    
    def add_attempt(self, base_name: str, variant: str, success: bool, error: Optional[str] = None):
        """Add an access attempt record."""
        attempt = {
            'base_name': base_name,
            'variant': variant,
            'success': success,
            'error': error,
            'timestamp': time.time()
        }
        self.access_attempts.append(attempt)
        
        if success:
            self.successful_accesses.append(attempt)
        else:
            self.failed_accesses.append(attempt)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get diagnostic statistics."""
        return {
            'total_attempts': len(self.access_attempts),
            'successful_accesses': len(self.successful_accesses),
            'failed_accesses': len(self.failed_accesses),
            'success_rate': len(self.successful_accesses) / max(len(self.access_attempts), 1) * 100,
            'widget_types': self.widget_types.copy(),
            'naming_patterns': self.widget_patterns.copy()
        }


class WidgetNamingStandardizer:
    """
    Widget naming standardization system.
    
    Provides a unified interface for accessing widgets regardless of their
    naming convention (.ui files vs hand-coded). Supports multiple access
    modes and provides comprehensive diagnostic information.
    """
    
    # Standard widget type mappings
    WIDGET_TYPE_MAPPINGS = {
        # Line edit variants
        'lineEdit': ['lineEdit', 'edit', 'LineEdit'],
        'line_edit': ['lineEdit', 'edit', 'LineEdit'],
        
        # Spin box variants
        'spinBox': ['spinBox', 'spin', 'SpinBox'],
        'spin_box': ['spinBox', 'spin', 'SpinBox'],
        
        # Double spin box variants
        'doubleSpinBox': ['doubleSpinBox', 'doubleSpin', 'DoubleSpinBox'],
        'double_spin_box': ['doubleSpinBox', 'doubleSpin', 'DoubleSpinBox'],
        
        # Combo box variants
        'comboBox': ['comboBox', 'combo', 'ComboBox'],
        'combo_box': ['comboBox', 'combo', 'ComboBox'],
        
        # Button variants
        'pushButton': ['pushButton', 'button', 'PushButton', 'Button'],
        'push_button': ['pushButton', 'button', 'PushButton', 'Button'],
        
        # Label variants
        'label': ['label', 'Label'],
        
        # Group box variants
        'groupBox': ['groupBox', 'group', 'GroupBox'],
        'group_box': ['groupBox', 'group', 'GroupBox'],
        
        # Tab widget variants
        'tabWidget': ['tabWidget', 'tab', 'TabWidget'],
        'tab_widget': ['tabWidget', 'tab', 'TabWidget'],
        
        # Text edit variants
        'textEdit': ['textEdit', 'text', 'TextEdit'],
        'text_edit': ['textEdit', 'text', 'TextEdit'],
        
        # Text browser variants
        'textBrowser': ['textBrowser', 'browser', 'TextBrowser'],
        'text_browser': ['textBrowser', 'browser', 'TextBrowser'],
        
        # Radio button variants
        'radioButton': ['radioButton', 'radio', 'RadioButton'],
        'radio_button': ['radioButton', 'radio', 'RadioButton'],
        
        # Check box variants
        'checkBox': ['checkBox', 'check', 'CheckBox'],
        'check_box': ['checkBox', 'check', 'CheckBox'],
        
        # Tool button variants
        'toolButton': ['toolButton', 'tool', 'ToolButton'],
        'tool_button': ['toolButton', 'tool', 'ToolButton']
    }
    
    # Common base name mappings
    COMMON_BASE_NAMES = {
        # Geometry parameters
        'length': ['length', 'Length'],
        'width': ['width', 'Width'],
        'height': ['height', 'Height'],
        'radius': ['radius', 'Radius'],
        
        # Division parameters
        'x_division': ['x_division', 'xDiv', 'x_div', 'XDiv'],
        'y_division': ['y_division', 'yDiv', 'y_div', 'YDiv'],
        'z_division': ['z_division', 'zDiv', 'z_div', 'ZDiv'],
        
        # Material properties
        'ds_value': ['DS_value', 'dsValue', 'DSValue', 'ds_value'],
        'cs_max': ['CS_max', 'csMax', 'CSMax', 'cs_max'],
        'k_react': ['kReact', 'k_react', 'KReact'],
        'ce': ['Ce', 'ce', 'CE'],
        'alpha_a': ['alphaA', 'alpha_a', 'AlphaA'],
        'alpha_c': ['alphaC', 'alpha_c', 'AlphaC'],
        
        # Control parameters
        'end_time': ['endTime', 'end_time', 'EndTime'],
        'delta_t': ['deltaT', 'delta_t', 'DeltaT'],
        'write_interval': ['writeInterval', 'write_interval', 'WriteInterval'],
        'tolerance': ['tolerance', 'Tolerance'],
        
        # UI elements
        'change': ['change', 'Change'],
        'run': ['run', 'Run'],
        'pause': ['pause', 'Pause'],
        'stop': ['stop', 'Stop'],
        'view': ['view', 'View'],
        'help': ['help', 'Help'],
        
        # Material selection
        'carbon': ['carbon', 'Carbon', 'graphite', 'Graphite'],
        'silicon': ['silicon', 'Silicon'],
        
        # Operation modes
        'charge': ['charge', 'Charge'],
        'discharge': ['discharge', 'Discharge']
    }
    
    def __init__(
        self, 
        widget: QWidget,
        access_mode: WidgetAccessMode = WidgetAccessMode.UI_FIRST,
        enable_diagnostics: bool = True
    ):
        """
        Initialize the widget naming standardizer.
        
        Args:
            widget: The widget to standardize access for
            access_mode: How to prioritize naming conventions
            enable_diagnostics: Whether to enable diagnostic tracking
        """
        self.widget = widget
        self.access_mode = access_mode
        self.enable_diagnostics = enable_diagnostics
        
        # Setup logger
        self.logger = logging.getLogger(f"{__name__}.WidgetNamingStandardizer")
        
        # Initialize diagnostics if enabled
        self.diagnostic_info = WidgetDiagnosticInfo() if enable_diagnostics else None
        
        self.logger.debug(f"Initialized standardizer for {widget.__class__.__name__} with mode {access_mode.value}")
    
    def get_widget(
        self, 
        base_name: str, 
        widget_type: str = 'lineEdit',
        default: Any = None
    ) -> Optional[QWidget]:
        """
        Get a widget using standardized naming.
        
        Args:
            base_name: Base name of the widget (e.g., 'length', 'width')
            widget_type: Type of widget (e.g., 'lineEdit', 'spinBox')
            default: Default value to return if widget not found
            
        Returns:
            The widget if found, otherwise None or default
            
        Raises:
            WidgetNamingError: If widget cannot be found and no default provided
        """
        # Get all possible naming variants
        variants = self._generate_naming_variants(base_name, widget_type)
        
        # Try variants based on access mode
        if self.access_mode == WidgetAccessMode.UI_FIRST:
            return self._try_variants(base_name, variants, widget_type, default)
        elif self.access_mode == WidgetAccessMode.CODE_FIRST:
            return self._try_variants_reverse(base_name, variants, widget_type, default)
        elif self.access_mode == WidgetAccessMode.UI_ONLY:
            ui_variants = [v for v in variants if self._is_ui_naming(v)]
            return self._try_variants(base_name, ui_variants, widget_type, default)
        elif self.access_mode == WidgetAccessMode.CODE_ONLY:
            code_variants = [v for v in variants if not self._is_ui_naming(v)]
            return self._try_variants(base_name, code_variants, widget_type, default)
        
        return default
    
    def get_widget_value(
        self, 
        base_name: str, 
        widget_type: str = 'lineEdit',
        default: Any = None
    ) -> Any:
        """
        Get the value from a widget using standardized naming.
        
        Args:
            base_name: Base name of the widget
            widget_type: Type of widget
            default: Default value to return if widget not found or value cannot be retrieved
            
        Returns:
            The widget value or default
        """
        try:
            widget = self.get_widget(base_name, widget_type)
            if widget is None:
                if self.enable_diagnostics:
                    self.diagnostic_info.add_attempt(base_name, widget_type, False, "Widget not found")
                return default
            
            # Get value based on widget type
            value = self._get_widget_value(widget)
            
            if self.enable_diagnostics:
                self.diagnostic_info.add_attempt(base_name, widget_type, True)
            
            return value
            
        except Exception as e:
            if self.enable_diagnostics:
                self.diagnostic_info.add_attempt(base_name, widget_type, False, str(e))
            self.logger.warning(f"Failed to get value for {base_name}: {e}")
            return default
    
    def set_widget_value(
        self, 
        base_name: str, 
        value: Any,
        widget_type: str = 'lineEdit'
    ) -> bool:
        """
        Set the value of a widget using standardized naming.
        
        Args:
            base_name: Base name of the widget
            value: Value to set
            widget_type: Type of widget
            
        Returns:
            True if successful, False otherwise
        """
        try:
            widget = self.get_widget(base_name, widget_type)
            if widget is None:
                if self.enable_diagnostics:
                    self.diagnostic_info.add_attempt(base_name, widget_type, False, "Widget not found for setting value")
                return False
            
            # Set value based on widget type
            self._set_widget_value(widget, value)
            
            if self.enable_diagnostics:
                self.diagnostic_info.add_attempt(base_name, widget_type, True)
            
            return True
            
        except Exception as e:
            if self.enable_diagnostics:
                self.diagnostic_info.add_attempt(base_name, widget_type, False, str(e))
            self.logger.warning(f"Failed to set value for {base_name}: {e}")
            return False
    
    def _generate_naming_variants(
        self, 
        base_name: str, 
        widget_type: str
    ) -> List[str]:
        """
        Generate all possible naming variants for a widget.
        
        Args:
            base_name: Base name of the widget
            widget_type: Type of widget
            
        Returns:
            List of possible widget names
        """
        variants = []
        
        # Get widget type suffixes
        type_suffixes = self.WIDGET_TYPE_MAPPINGS.get(widget_type, [widget_type])
        
        # Get base name variants
        base_variants = self.COMMON_BASE_NAMES.get(base_name, [base_name])
        
        # Generate combinations
        for base in base_variants:
            for suffix in type_suffixes:
                # UI convention: base_suffix
                variants.append(f"{base}_{suffix}")
                # Hand-coded convention: base_edit, base_spin, etc.
                if suffix in ['lineEdit', 'spinBox', 'doubleSpinBox']:
                    simple_suffix = suffix.replace('Box', '').replace('Spin', '').lower()
                    variants.append(f"{base}_{simple_suffix}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        return unique_variants
    
    def _try_variants(
        self, 
        base_name: str, 
        variants: List[str], 
        widget_type: str,
        default: Any
    ) -> Optional[QWidget]:
        """
        Try to find a widget using the given variants.
        
        Args:
            base_name: Base name of the widget
            variants: List of possible widget names
            widget_type: Type of widget
            default: Default value to return
            
        Returns:
            The widget if found, otherwise None or default
        """
        for variant in variants:
            if hasattr(self.widget, variant):
                widget = getattr(self.widget, variant)
                if isinstance(widget, QWidget):
                    if self.enable_diagnostics:
                        self.diagnostic_info.add_attempt(base_name, variant, True)
                    return widget
                else:
                    if self.enable_diagnostics:
                        self.diagnostic_info.add_attempt(base_name, variant, False, f"Not a QWidget: {type(widget)}")
        
        # If no widget found, log failure
        if self.enable_diagnostics:
            self.diagnostic_info.add_attempt(base_name, widget_type, False, "No variants found")
        
        return default
    
    def _try_variants_reverse(
        self, 
        base_name: str, 
        variants: List[str], 
        widget_type: str,
        default: Any
    ) -> Optional[QWidget]:
        """
        Try to find a widget using variants in reverse order (code-first).
        
        Args:
            base_name: Base name of the widget
            variants: List of possible widget names
            widget_type: Type of widget
            default: Default value to return
            
        Returns:
            The widget if found, otherwise None or default
        """
        # Try reverse order to prioritize hand-coded naming
        for variant in reversed(variants):
            if hasattr(self.widget, variant):
                widget = getattr(self.widget, variant)
                if isinstance(widget, QWidget):
                    if self.enable_diagnostics:
                        self.diagnostic_info.add_attempt(base_name, variant, True)
                    return widget
                else:
                    if self.enable_diagnostics:
                        self.diagnostic_info.add_attempt(base_name, variant, False, f"Not a QWidget: {type(widget)}")
        
        # If no widget found, log failure
        if self.enable_diagnostics:
            self.diagnostic_info.add_attempt(base_name, widget_type, False, "No variants found")
        
        return default
    
    def _is_ui_naming(self, widget_name: str) -> bool:
        """
        Check if a widget name follows .ui naming convention.
        
        Args:
            widget_name: Name of the widget
            
        Returns:
            True if follows .ui convention, False otherwise
        """
        # .ui convention typically uses full widget type names
        ui_indicators = ['lineEdit', 'spinBox', 'doubleSpinBox', 'comboBox', 'pushButton']
        return any(indicator in widget_name for indicator in ui_indicators)
    
    def _get_widget_value(self, widget: QWidget) -> Any:
        """
        Get the value from a widget based on its type.
        
        Args:
            widget: The widget to get value from
            
        Returns:
            The widget value
        """
        # Handle different widget types
        if hasattr(widget, 'text'):
            return widget.text()
        elif hasattr(widget, 'value'):
            return widget.value()
        elif hasattr(widget, 'currentIndex'):
            return widget.currentIndex()
        elif hasattr(widget, 'isChecked'):
            return widget.isChecked()
        elif hasattr(widget, 'toPlainText'):
            return widget.toPlainText()
        else:
            raise WidgetNamingError(f"Unsupported widget type: {type(widget)}")
    
    def _set_widget_value(self, widget: QWidget, value: Any):
        """
        Set the value of a widget based on its type.
        
        Args:
            widget: The widget to set value for
            value: The value to set
        """
        # Handle different widget types
        if hasattr(widget, 'setText') and hasattr(widget, 'text'):
            widget.setText(str(value))
        elif hasattr(widget, 'setValue') and hasattr(widget, 'value'):
            widget.setValue(float(value))
        elif hasattr(widget, 'setCurrentIndex') and hasattr(widget, 'currentIndex'):
            widget.setCurrentIndex(int(value))
        elif hasattr(widget, 'setChecked') and hasattr(widget, 'isChecked'):
            widget.setChecked(bool(value))
        elif hasattr(widget, 'setPlainText') and hasattr(widget, 'toPlainText'):
            widget.setPlainText(str(value))
        else:
            raise WidgetNamingError(f"Cannot set value for widget type: {type(widget)}")
    
    def discover_widgets(self) -> Dict[str, List[str]]:
        """
        Discover all widgets in the interface and categorize them.
        
        Returns:
            Dictionary mapping widget types to lists of widget names
        """
        widget_discovery = {}
        
        # Get all attributes that are QWidgets
        for attr_name in dir(self.widget):
            try:
                attr = getattr(self.widget, attr_name)
                if isinstance(attr, QWidget):
                    widget_type = type(attr).__name__
                    if widget_type not in widget_discovery:
                        widget_discovery[widget_type] = []
                    widget_discovery[widget_type].append(attr_name)
            except Exception:
                # Skip attributes that can't be accessed
                continue
        
        return widget_discovery
    
    def get_diagnostics(self) -> Optional[Dict[str, Any]]:
        """
        Get diagnostic information about widget access.
        
        Returns:
            Diagnostic information or None if diagnostics disabled
        """
        if not self.enable_diagnostics or not self.diagnostic_info:
            return None
        
        return {
            'statistics': self.diagnostic_info.get_statistics(),
            'access_attempts': self.diagnostic_info.access_attempts,
            'successful_accesses': self.diagnostic_info.successful_accesses,
            'failed_accesses': self.diagnostic_info.failed_accesses
        }
    
    def reset_diagnostics(self):
        """Reset diagnostic information."""
        if self.enable_diagnostics and self.diagnostic_info:
            self.diagnostic_info = WidgetDiagnosticInfo()
    
    def validate_naming_convention(self) -> Dict[str, Any]:
        """
        Validate the current naming convention usage.
        
        Returns:
            Validation report with recommendations
        """
        discovery = self.discover_widgets()
        
        report = {
            'total_widgets': sum(len(widgets) for widgets in discovery.values()),
            'widget_types': discovery,
            'ui_convention_count': 0,
            'code_convention_count': 0,
            'mixed_convention': False,
            'recommendations': []
        }
        
        # Count naming conventions
        for widget_type, widgets in discovery.items():
            for widget_name in widgets:
                if self._is_ui_naming(widget_name):
                    report['ui_convention_count'] += 1
                else:
                    report['code_convention_count'] += 1
        
        # Check for mixed conventions
        total_widgets = report['total_widgets']
        if total_widgets > 0:
            ui_ratio = report['ui_convention_count'] / total_widgets
            code_ratio = report['code_convention_count'] / total_widgets
            
            if ui_ratio > 0.1 and code_ratio > 0.1:
                report['mixed_convention'] = True
                report['recommendations'].append("Consider standardizing on one naming convention")
                if ui_ratio > code_ratio:
                    report['recommendations'].append("Recommendation: Use .ui naming convention")
                else:
                    report['recommendations'].append("Recommendation: Use hand-coded naming convention")
        
        return report


def create_standardized_interface_mixin(access_mode: WidgetAccessMode = WidgetAccessMode.UI_FIRST):
    """
    Create a mixin class for standardized widget access.
    
    Args:
        access_mode: Widget access mode
        
    Returns:
        Mixin class that can be used with any QWidget
    """
    
    class StandardizedWidgetAccess:
        """Mixin class for standardized widget access."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._widget_standardizer = WidgetNamingStandardizer(self, access_mode)
        
        def get_widget(self, base_name: str, widget_type: str = 'lineEdit', default=None):
            """Get widget using standardized naming."""
            return self._widget_standardizer.get_widget(base_name, widget_type, default)
        
        def get_widget_value(self, base_name: str, widget_type: str = 'lineEdit', default=None):
            """Get widget value using standardized naming."""
            return self._widget_standardizer.get_widget_value(base_name, widget_type, default)
        
        def set_widget_value(self, base_name: str, value, widget_type: str = 'lineEdit'):
            """Set widget value using standardized naming."""
            return self._widget_standardizer.set_widget_value(base_name, value, widget_type)
        
        def discover_widgets(self):
            """Discover all widgets in the interface."""
            return self._widget_standardizer.discover_widgets()
        
        def get_diagnostics(self):
            """Get diagnostic information."""
            return self._widget_standardizer.get_diagnostics()
        
        def validate_naming(self):
            """Validate naming convention usage."""
            return self._widget_standardizer.validate_naming_convention()
    
    return StandardizedWidgetAccess


def main():
    """Test the widget naming standardization system."""
    app = QApplication(sys.argv)
    
    # Create a test widget
    test_widget = QWidget()
    test_widget.setObjectName("TestWidget")
    
    # Add some test widgets with different naming conventions
    from PyQt6.QtWidgets import QLineEdit, QPushButton
    
    # UI convention
    test_widget.length_lineEdit = QLineEdit()
    test_widget.width_lineEdit = QLineEdit()
    
    # Hand-coded convention
    test_widget.height_edit = QLineEdit()
    test_widget.radius_spin = QPushButton()
    
    # Test standardization
    standardizer = WidgetNamingStandardizer(test_widget, WidgetAccessMode.UI_FIRST)
    
    print("Testing widget access:")
    print(f"length (UI): {standardizer.get_widget('length') is not None}")
    print(f"height (Code): {standardizer.get_widget('height') is not None}")
    print(f"width (UI): {standardizer.get_widget('width') is not None}")
    
    # Test diagnostics
    diagnostics = standardizer.get_diagnostics()
    if diagnostics:
        print(f"\nDiagnostics: {diagnostics['statistics']}")
    
    # Test validation
    validation = standardizer.validate_naming()
    print(f"\nValidation: {validation}")
    
    print("Widget naming standardization test completed!")


if __name__ == "__main__":
    main()