"""
Parameter validation system for Battery Simulator interfaces.

This module provides a comprehensive parameter validation system that ensures
all interface parameters are valid before simulation execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for validation errors."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error or warning."""
    field: str
    message: str
    severity: SeverityLevel
    context: Dict[str, Any] = None
    
    def __str__(self) -> str:
        """String representation of the validation error."""
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Result of parameter validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    infos: List[ValidationError]
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.infos = []
    
    def add_error(self, field: str, message: str, context: Dict[str, Any] = None):
        """Add an error to the validation result."""
        error = ValidationError(field, message, SeverityLevel.ERROR, context)
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, context: Dict[str, Any] = None):
        """Add a warning to the validation result."""
        warning = ValidationError(field, message, SeverityLevel.WARNING, context)
        self.warnings.append(warning)
    
    def add_info(self, field: str, message: str, context: Dict[str, Any] = None):
        """Add an info message to the validation result."""
        info = ValidationError(field, message, SeverityLevel.INFO, context)
        self.infos.append(info)
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def get_all_messages(self) -> List[str]:
        """Get all validation messages as strings."""
        messages = []
        for error in self.errors:
            messages.append(str(error))
        for warning in self.warnings:
            messages.append(str(warning))
        for info in self.infos:
            messages.append(str(info))
        return messages


class ValidationRule(ABC):
    """Abstract base class for validation rules."""
    
    @abstractmethod
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate parameters and add errors/warnings to the result.
        
        Args:
            parameters: Dictionary of parameters to validate
            result: ValidationResult to populate with errors/warnings
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what this rule validates."""
        pass


class ParameterValidator(ABC):
    """
    Abstract base class for parameter validators.
    
    Provides a framework for validating parameters for different interface types.
    """
    
    def __init__(self, interface_type: str):
        """
        Initialize the validator.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell)
        """
        self.interface_type = interface_type
        self.rules = self._load_validation_rules()
    
    @abstractmethod
    def _load_validation_rules(self) -> List[ValidationRule]:
        """Load the validation rules for this interface type."""
        pass
    
    def validate(self, parameters: Dict[str, Any]) -> ValidationResult:
        """
        Validate parameters using all loaded rules.
        
        Args:
            parameters: Dictionary of parameters to validate
            
        Returns:
            ValidationResult containing all errors and warnings
        """
        result = ValidationResult()
        
        # Add interface type to parameters for rules that need it
        if 'interface_type' not in parameters:
            parameters = parameters.copy()
            parameters['interface_type'] = self.interface_type
        
        # Apply all validation rules
        for rule in self.rules:
            try:
                rule.validate(parameters, result)
            except Exception as e:
                # Log the error but continue with other rules
                result.add_error(
                    'system', 
                    f"Validation rule '{rule.get_description()}' failed: {str(e)}"
                )
        
        return result
    
    def get_rule_descriptions(self) -> List[str]:
        """Get descriptions of all validation rules."""
        return [rule.get_description() for rule in self.rules]
    
    def get_interface_type(self) -> str:
        """Get the interface type for this validator."""
        return self.interface_type


class TypeValidationRule(ValidationRule):
    """Validates parameter types."""
    
    def __init__(self, field: str, expected_type: type, optional: bool = False):
        """
        Initialize type validation rule.
        
        Args:
            field: Name of the field to validate
            expected_type: Expected type of the field
            optional: Whether the field is optional
        """
        self.field = field
        self.expected_type = expected_type
        self.optional = optional
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate parameter type."""
        if self.field not in parameters:
            if not self.optional:
                result.add_error(self.field, f"Required field '{self.field}' is missing")
            return
        
        value = parameters[self.field]
        
        # Handle None values for optional fields
        if value is None and self.optional:
            return
        
        # Handle numeric types (int can be float)
        if self.expected_type in (int, float):
            if not isinstance(value, (int, float)):
                result.add_error(
                    self.field, 
                    f"Expected {self.expected_type.__name__}, got {type(value).__name__}"
                )
            elif self.expected_type == int and isinstance(value, float) and not value.is_integer():
                result.add_warning(
                    self.field,
                    f"Expected integer, got float {value}. Will be converted to {int(value)}"
                )
        else:
            if not isinstance(value, self.expected_type):
                result.add_error(
                    self.field,
                    f"Expected {self.expected_type.__name__}, got {type(value).__name__}"
                )
    
    def get_description(self) -> str:
        """Get rule description."""
        optional_str = " (optional)" if self.optional else ""
        return f"Type validation for '{self.field}' ({self.expected_type.__name__}){optional_str}"


class RangeValidationRule(ValidationRule):
    """Validates parameter ranges."""
    
    def __init__(
        self, 
        field: str, 
        min_value: float = None, 
        max_value: float = None,
        min_inclusive: bool = True,
        max_inclusive: bool = True
    ):
        """
        Initialize range validation rule.
        
        Args:
            field: Name of the field to validate
            min_value: Minimum allowed value (None for no minimum)
            max_value: Maximum allowed value (None for no maximum)
            min_inclusive: Whether minimum is inclusive
            max_inclusive: Whether maximum is inclusive
        """
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate parameter range."""
        if self.field not in parameters:
            return
        
        value = parameters[self.field]
        
        # Skip validation for None values
        if value is None:
            return
        
        # Check if value is numeric
        if not isinstance(value, (int, float)):
            result.add_error(self.field, f"Cannot validate range for non-numeric value: {value}")
            return
        
        # Check minimum value
        if self.min_value is not None:
            if self.min_inclusive and value < self.min_value:
                result.add_error(
                    self.field,
                    f"Value {value} is less than minimum {self.min_value}"
                )
            elif not self.min_inclusive and value <= self.min_value:
                result.add_error(
                    self.field,
                    f"Value {value} is less than or equal to minimum {self.min_value}"
                )
        
        # Check maximum value
        if self.max_value is not None:
            if self.max_inclusive and value > self.max_value:
                result.add_error(
                    self.field,
                    f"Value {value} is greater than maximum {self.max_value}"
                )
            elif not self.max_inclusive and value >= self.max_value:
                result.add_error(
                    self.field,
                    f"Value {value} is greater than or equal to maximum {self.max_value}"
                )
    
    def get_description(self) -> str:
        """Get rule description."""
        min_str = f"min={self.min_value}{'(inclusive)' if self.min_inclusive else '(exclusive)'}"
        max_str = f"max={self.max_value}{'(inclusive)' if self.max_inclusive else '(exclusive)'}"
        return f"Range validation for '{self.field}': {min_str}, {max_str}"


class GeometryValidationRule(ValidationRule):
    """Validates geometry parameters."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate geometry constraints."""
        # Check that dimensions are positive
        for dim in ['length', 'width', 'height']:
            if dim in parameters:
                value = parameters[dim]
                if isinstance(value, (int, float)) and value <= 0:
                    result.add_error(dim, f"{dim} must be positive")
        
        # Check that divisions are positive integers
        for div in ['x_division', 'y_division', 'z_division']:
            if div in parameters:
                value = parameters[div]
                if isinstance(value, (int, float)):
                    if value <= 0:
                        result.add_error(div, f"{div} must be positive")
                    elif isinstance(value, float) and not value.is_integer():
                        result.add_error(div, f"{div} must be an integer")
                else:
                    result.add_error(div, f"{div} must be a number")
        
        # Check unit validity
        if 'unit' in parameters:
            unit = parameters['unit']
            valid_units = ['micrometer', 'millimeter', 'meter']
            if unit not in valid_units:
                result.add_error('unit', f"Invalid unit '{unit}'. Must be one of: {', '.join(valid_units)}")
    
    def get_description(self) -> str:
        """Get rule description."""
        return "Geometry parameter validation (dimensions, divisions, units)"


class MaterialCompatibilityRule(ValidationRule):
    """Validates material compatibility with interface type."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate material compatibility."""
        interface_type = parameters.get('interface_type', '')
        material = parameters.get('material', '')
        
        # Define material compatibility
        compatible_materials = {
            'carbon': ['carbon', 'silicon'],
            'halfcell': ['carbon', 'silicon', 'LFP', 'NCA'],
            'fullcell': ['carbon', 'silicon', 'LFP', 'NCA', 'LionSimba']
        }
        
        if interface_type in compatible_materials:
            if material and material not in compatible_materials[interface_type]:
                result.add_error(
                    'material',
                    f"Material '{material}' not compatible with {interface_type} interface. "
                    f"Valid materials: {', '.join(compatible_materials[interface_type])}"
                )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "Material compatibility validation"


# Convenience functions for creating common validation rules
def create_geometry_rules() -> List[ValidationRule]:
    """Create common geometry validation rules."""
    return [
        GeometryValidationRule(),
        RangeValidationRule('length', min_value=0.1, max_value=10000),
        RangeValidationRule('width', min_value=0.1, max_value=10000),
        RangeValidationRule('height', min_value=0.1, max_value=10000),
        RangeValidationRule('radius', min_value=0.1, max_value=1000),
        RangeValidationRule('x_division', min_value=1, max_value=1000),
        RangeValidationRule('y_division', min_value=1, max_value=1000),
        RangeValidationRule('z_division', min_value=1, max_value=1000),
    ]


def create_material_rules() -> List[ValidationRule]:
    """Create material compatibility validation rules."""
    return [MaterialCompatibilityRule()]
