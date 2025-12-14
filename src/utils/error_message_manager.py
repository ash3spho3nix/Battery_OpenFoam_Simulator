"""
Error message manager for Battery Simulator interfaces.

This module provides a centralized system for generating user-friendly
error messages with context-aware guidance.
"""

from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass


class ErrorType(Enum):
    """Types of errors that can occur."""
    GEOMETRY_INVALID = "geometry_invalid"
    MATERIAL_INCOMPATIBLE = "material_incompatible"
    SOLVER_FAILED = "solver_failed"
    TEMPLATE_MISSING = "template_missing"
    PARAMETER_INVALID = "parameter_invalid"
    PARAMETER_RANGE = "parameter_range"
    PARAMETER_TYPE = "parameter_type"
    SYSTEM_ERROR = "system_error"
    VALIDATION_ERROR = "validation_error"
    IO_ERROR = "io_error"
    PATH_ERROR = "path_error"


@dataclass
class ErrorMessage:
    """Represents a formatted error message."""
    severity: str  # 'error', 'warning', 'info'
    title: str
    message: str
    suggestion: str = ""
    context: Dict[str, Any] = None
    
    def __str__(self) -> str:
        """String representation of the error message."""
        result = f"[{self.severity.upper()}] {self.title}\n"
        result += f"  Message: {self.message}\n"
        if self.suggestion:
            result += f"  Suggestion: {self.suggestion}\n"
        if self.context:
            result += f"  Context: {self.context}"
        return result


class ErrorMessageManager:
    """
    Manages error message templates and generates context-aware messages.
    
    Provides user-friendly error messages with actionable guidance
    for common issues in battery simulation interfaces.
    """
    
    def __init__(self):
        """Initialize the error message manager."""
        self.message_templates = self._load_message_templates()
        self.severity_emojis = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
    
    def get_error_message(
        self, 
        error_type: ErrorType, 
        context: Dict[str, Any] = None,
        severity: str = 'error'
    ) -> ErrorMessage:
        """
        Generate an error message based on error type and context.
        
        Args:
            error_type: Type of error that occurred
            context: Additional context information
            severity: Severity level ('error', 'warning', 'info')
            
        Returns:
            Formatted error message
        """
        template = self.message_templates.get(error_type)
        if not template:
            return ErrorMessage(
                severity=severity,
                title="Unknown Error",
                message="An unknown error occurred.",
                context=context
            )
        
        # Format the message with context
        try:
            message = template['message'].format(**(context or {}))
            suggestion = template['suggestion'].format(**(context or {}))
        except (KeyError, ValueError) as e:
            # Fallback if context is incomplete
            message = template['message']
            suggestion = template['suggestion']
        
        return ErrorMessage(
            severity=severity,
            title=template['title'],
            message=message,
            suggestion=suggestion,
            context=context
        )
    
    def get_validation_error_message(
        self, 
        field: str, 
        error_type: str, 
        value: Any = None,
        expected: str = None,
        context: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Generate a validation error message.
        
        Args:
            field: Field name that failed validation
            error_type: Type of validation error
            value: Value that failed validation
            expected: Expected value or range
            context: Additional context
            
        Returns:
            Formatted validation error message
        """
        base_context = {
            'field': field,
            'value': value,
            'expected': expected,
            **(context or {})
        }
        
        if error_type == 'type':
            return self.get_error_message(
                ErrorType.PARAMETER_TYPE,
                {**base_context, 'field_type': type(value).__name__},
                'error'
            )
        elif error_type == 'range':
            return self.get_error_message(
                ErrorType.PARAMETER_RANGE,
                base_context,
                'error'
            )
        elif error_type == 'required':
            return self.get_error_message(
                ErrorType.PARAMETER_INVALID,
                base_context,
                'error'
            )
        else:
            return self.get_error_message(
                ErrorType.VALIDATION_ERROR,
                base_context,
                'warning'
            )
    
    def get_geometry_error_message(
        self,
        error_subtype: str,
        context: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Generate a geometry-related error message.
        
        Args:
            error_subtype: Specific type of geometry error
            context: Additional context
            
        Returns:
            Formatted geometry error message
        """
        if error_subtype == 'dimensions':
            return self.get_error_message(
                ErrorType.GEOMETRY_INVALID,
                {**(context or {}), 'issue': 'invalid dimensions'},
                'error'
            )
        elif error_subtype == 'divisions':
            return self.get_error_message(
                ErrorType.GEOMETRY_INVALID,
                {**(context or {}), 'issue': 'invalid divisions'},
                'error'
            )
        elif error_subtype == 'consistency':
            return self.get_error_message(
                ErrorType.GEOMETRY_INVALID,
                {**(context or {}), 'issue': 'geometry inconsistency'},
                'warning'
            )
        else:
            return self.get_error_message(
                ErrorType.GEOMETRY_INVALID,
                context,
                'error'
            )
    
    def get_material_error_message(
        self,
        material: str,
        interface_type: str,
        context: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Generate a material compatibility error message.
        
        Args:
            material: Material that caused the error
            interface_type: Interface type (carbon, halfcell, fullcell)
            context: Additional context
            
        Returns:
            Formatted material error message
        """
        return self.get_error_message(
            ErrorType.MATERIAL_INCOMPATIBLE,
            {**(context or {}), 'material': material, 'interface': interface_type},
            'error'
        )
    
    def get_solver_error_message(
        self,
        solver_name: str,
        exit_code: int = None,
        context: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Generate a solver execution error message.
        
        Args:
            solver_name: Name of the solver that failed
            exit_code: Exit code from solver execution
            context: Additional context
            
        Returns:
            Formatted solver error message
        """
        return self.get_error_message(
            ErrorType.SOLVER_FAILED,
            {**(context or {}), 'solver': solver_name, 'exit_code': exit_code},
            'error'
        )
    
    def get_template_error_message(
        self,
        template_name: str,
        template_path: str = None,
        context: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Generate a template-related error message.
        
        Args:
            template_name: Name of the missing/invalid template
            template_path: Path to the template
            context: Additional context
            
        Returns:
            Formatted template error message
        """
        return self.get_error_message(
            ErrorType.TEMPLATE_MISSING,
            {**(context or {}), 'template_name': template_name, 'template_path': template_path},
            'error'
        )
    
    def format_user_message(self, error_message: ErrorMessage) -> str:
        """
        Format error message for user display.
        
        Args:
            error_message: Error message to format
            
        Returns:
            User-friendly formatted message
        """
        emoji = self.severity_emojis.get(error_message.severity, '•')
        
        message = f"{emoji} {error_message.title}\n\n"
        message += f"{error_message.message}\n\n"
        
        if error_message.suggestion:
            message += f"💡 {error_message.suggestion}\n\n"
        
        if error_message.context:
            message += f"📋 Context: {error_message.context}\n"
        
        return message.strip()
    
    def _load_message_templates(self) -> Dict[ErrorType, Dict[str, str]]:
        """Load error message templates."""
        return {
            ErrorType.GEOMETRY_INVALID: {
                'title': 'Invalid Geometry Parameters',
                'message': 'Geometry parameters are invalid: {details}',
                'suggestion': 'Check that all dimensions are positive and divisions are integers.'
            },
            ErrorType.MATERIAL_INCOMPATIBLE: {
                'title': 'Material Compatibility Issue',
                'message': 'Material {material} is not compatible with {interface} interface',
                'suggestion': 'Choose a compatible material from the available options.'
            },
            ErrorType.SOLVER_FAILED: {
                'title': 'Solver Execution Failed',
                'message': 'Solver {solver} failed with exit code {exit_code}',
                'suggestion': 'Check solver installation and parameters. Review terminal output for details.'
            },
            ErrorType.TEMPLATE_MISSING: {
                'title': 'Template Not Found',
                'message': 'Template {template_name} not found in {template_path}',
                'suggestion': 'Ensure templates are properly installed and accessible.'
            },
            ErrorType.PARAMETER_INVALID: {
                'title': 'Invalid Parameter',
                'message': 'Parameter {field} has invalid value: {value}',
                'suggestion': 'Check parameter requirements and enter a valid value.'
            },
            ErrorType.PARAMETER_RANGE: {
                'title': 'Parameter Out of Range',
                'message': 'Parameter {field} value {value} is outside valid range',
                'suggestion': 'Enter a value within the specified range: {expected}'
            },
            ErrorType.PARAMETER_TYPE: {
                'title': 'Parameter Type Error',
                'message': 'Parameter {field} expects {expected}, got {field_type}',
                'suggestion': 'Enter a value of the correct type.'
            },
            ErrorType.SYSTEM_ERROR: {
                'title': 'System Error',
                'message': 'A system error occurred: {error}',
                'suggestion': 'Check system configuration and try again.'
            },
            ErrorType.VALIDATION_ERROR: {
                'title': 'Validation Error',
                'message': 'Parameter validation failed: {details}',
                'suggestion': 'Review parameter values and try again.'
            },
            ErrorType.IO_ERROR: {
                'title': 'File I/O Error',
                'message': 'File operation failed: {error}',
                'suggestion': 'Check file permissions and disk space.'
            },
            ErrorType.PATH_ERROR: {
                'title': 'Path Error',
                'message': 'Invalid path: {path}',
                'suggestion': 'Check that the path exists and is accessible.'
            }
        }


# Global error message manager instance
_error_manager = None


def get_error_manager() -> ErrorMessageManager:
    """Get the global error message manager instance."""
    global _error_manager
    if _error_manager is None:
        _error_manager = ErrorMessageManager()
    return _error_manager