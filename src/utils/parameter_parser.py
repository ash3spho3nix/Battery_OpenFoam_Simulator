"""
Parameter parser for OpenFOAM configuration files.

DEPRECATED: This module is kept for backward compatibility.
Use parameter_manager_enhanced.py instead.
"""

# Import the enhanced version for compatibility
from .parameter_manager_enhanced import (
    ParameterManager,
    ParameterValidationError,
    OpenFOAMParseError,
    ParameterDefinition
)

__all__ = [
    'ParameterManager',
    'ParameterValidationError',
    'OpenFOAMParseError',
    'ParameterDefinition'
]
