"""
Carbon interface parameter validator.

This module provides parameter validation specific to the Carbon interface (SPM).
"""

from typing import Dict, Any, List
from ..parameter_validator import (
    ParameterValidator, ValidationRule, ValidationResult,
    TypeValidationRule, RangeValidationRule, GeometryValidationRule,
    MaterialCompatibilityRule, create_geometry_rules, create_material_rules
)


class CarbonValidator(ParameterValidator):
    """
    Parameter validator for Carbon interface (Single Particle Model).
    
    Validates parameters specific to SPM simulations including geometry,
    electrochemical parameters, and simulation control parameters.
    """
    
    def _load_validation_rules(self) -> List[ValidationRule]:
        """Load validation rules for Carbon interface."""
        rules = []
        
        # Basic type validations
        rules.extend(self._get_type_rules())
        
        # Geometry validations
        rules.extend(create_geometry_rules())
        
        # Material compatibility
        rules.extend(create_material_rules())
        
        # Electrochemical parameter validations
        rules.extend(self._get_electrochemical_rules())
        
        # Simulation control validations
        rules.extend(self._get_simulation_control_rules())
        
        # SPM-specific validations
        rules.extend(self._get_spm_specific_rules())
        
        return rules
    
    def _get_type_rules(self) -> List[ValidationRule]:
        """Get type validation rules for Carbon interface."""
        return [
            TypeValidationRule('project_name', str),
            TypeValidationRule('length', (int, float)),
            TypeValidationRule('width', (int, float)),
            TypeValidationRule('height', (int, float)),
            TypeValidationRule('radius', (int, float)),
            TypeValidationRule('unit', str),
            TypeValidationRule('x_division', int),
            TypeValidationRule('y_division', int),
            TypeValidationRule('z_division', int),
            TypeValidationRule('DS_value', (int, float)),
            TypeValidationRule('CS_max', (int, float)),
            TypeValidationRule('kReact', (int, float)),
            TypeValidationRule('R', (int, float)),
            TypeValidationRule('F', (int, float)),
            TypeValidationRule('Ce', (int, float)),
            TypeValidationRule('alphaA', (int, float)),
            TypeValidationRule('alphaC', (int, float)),
            TypeValidationRule('T_temp', (int, float)),
            TypeValidationRule('I_app', (int, float)),
            TypeValidationRule('initial_cs', (int, float)),
            TypeValidationRule('endTime', (int, float)),
            TypeValidationRule('deltaT', (int, float)),
            TypeValidationRule('writeInterval', (int, float)),
            TypeValidationRule('tolerance', (int, float)),
            TypeValidationRule('material', str, optional=True),
        ]
    
    def _get_electrochemical_rules(self) -> List[ValidationRule]:
        """Get electrochemical parameter validation rules."""
        return [
            # DS value (diffusivity) should be positive and reasonable
            RangeValidationRule('DS_value', min_value=1e-20, max_value=1e-6),
            
            # CS max should be positive
            RangeValidationRule('CS_max', min_value=1000, max_value=50000),
            
            # kReact should be positive
            RangeValidationRule('kReact', min_value=1e-15, max_value=1e-8),
            
            # Universal gas constant should be around 8.314
            RangeValidationRule('R', min_value=8.0, max_value=8.5),
            
            # Faraday's constant should be around 96485
            RangeValidationRule('F', min_value=96000, max_value=97000),
            
            # Electrolyte concentration should be reasonable
            RangeValidationRule('Ce', min_value=500, max_value=2000),
            
            # Alpha values should be between 0 and 1
            RangeValidationRule('alphaA', min_value=0, max_value=1),
            RangeValidationRule('alphaC', min_value=0, max_value=1),
            
            # Temperature should be reasonable (200-400K)
            RangeValidationRule('T_temp', min_value=200, max_value=400),
            
            # Applied current should be reasonable
            RangeValidationRule('I_app', min_value=-1000, max_value=1000),
            
            # Initial concentration should be between 0 and CS_max
            RangeValidationRule('initial_cs', min_value=0, max_value=50000),
        ]
    
    def _get_simulation_control_rules(self) -> List[ValidationRule]:
        """Get simulation control parameter validation rules."""
        return [
            # End time should be positive
            RangeValidationRule('endTime', min_value=0.1, max_value=100000),
            
            # Delta T should be positive and reasonable
            RangeValidationRule('deltaT', min_value=1e-6, max_value=10),
            
            # Write interval should be positive
            RangeValidationRule('writeInterval', min_value=0.001, max_value=10000),
            
            # Tolerance should be positive and small
            RangeValidationRule('tolerance', min_value=1e-12, max_value=1e-3),
        ]
    
    def _get_spm_specific_rules(self) -> List[ValidationRule]:
        """Get SPM-specific validation rules."""
        return [
            # For SPM, radius should be smaller than half of any dimension
            SPMSphereValidationRule(),
            
            # For SPM, divisions should be reasonable for particle simulation
            RangeValidationRule('x_division', min_value=5, max_value=200),
            RangeValidationRule('y_division', min_value=5, max_value=200),
            RangeValidationRule('z_division', min_value=5, max_value=200),
        ]


class SPMSphereValidationRule(ValidationRule):
    """Validates that particle radius is appropriate for SPM geometry."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate SPM sphere geometry constraints."""
        if 'radius' not in parameters or 'length' not in parameters:
            return
        
        radius = parameters['radius']
        length = parameters['length']
        width = parameters.get('width', length)
        height = parameters.get('height', length)
        
        # Check if values are numeric
        if not all(isinstance(v, (int, float)) for v in [radius, length, width, height]):
            return
        
        # Radius should be smaller than half of any dimension
        min_dimension = min(length, width, height) / 2
        
        if radius >= min_dimension:
            result.add_error(
                'radius',
                f"Particle radius ({radius}) should be smaller than half of "
                f"the smallest dimension ({min_dimension})"
            )
        
        # Radius should be reasonable compared to dimensions
        max_reasonable_radius = min_dimension * 0.8
        if radius > max_reasonable_radius:
            result.add_warning(
                'radius',
                f"Particle radius ({radius}) is very large compared to geometry. "
                f"Consider reducing for better SPM accuracy."
            )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "SPM sphere geometry validation (radius vs dimensions)"