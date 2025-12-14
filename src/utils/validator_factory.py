"""
Validator factory for creating appropriate parameter validators.

This module provides a factory function to create the appropriate
parameter validator based on the interface type.
"""

from typing import Optional
from .parameter_validator import ParameterValidator
from .validators.carbon_validator import CarbonValidator
from .validators.halfcell_validator import HalfCellValidator
from .validators.fullcell_validator import FullCellValidator


def create_validator(interface_type: str) -> ParameterValidator:
    """
    Create the appropriate parameter validator for the given interface type.
    
    Args:
        interface_type: Type of interface (carbon, halfcell, fullcell)
        
    Returns:
        ParameterValidator instance for the specified interface type
        
    Raises:
        ValueError: If interface_type is not supported
    """
    interface_type = interface_type.lower()
    
    if interface_type == 'carbon':
        return CarbonValidator('carbon')
    elif interface_type == 'halfcell':
        return HalfCellValidator('halfcell')
    elif interface_type == 'fullcell':
        return FullCellValidator('fullcell')
    else:
        raise ValueError(f"Unsupported interface type: {interface_type}")


def get_supported_interfaces() -> list:
    """
    Get a list of supported interface types.
    
    Returns:
        List of supported interface types
    """
    return ['carbon', 'halfcell', 'fullcell']


def is_interface_supported(interface_type: str) -> bool:
    """
    Check if the interface type is supported.
    
    Args:
        interface_type: Type of interface to check
        
    Returns:
        True if supported, False otherwise
    """
    return interface_type.lower() in get_supported_interfaces()


def create_validator_safe(interface_type: str) -> Optional[ParameterValidator]:
    """
    Safely create a parameter validator, returning None if unsupported.
    
    Args:
        interface_type: Type of interface (carbon, halfcell, fullcell)
        
    Returns:
        ParameterValidator instance or None if unsupported
    """
    try:
        return create_validator(interface_type)
    except ValueError:
        return None