"""
HalfCell interface parameter validator.

This module provides parameter validation specific to the HalfCell interface (P2D Half Cell).
"""

from typing import Dict, Any, List
from ..parameter_validator import (
    ParameterValidator, ValidationRule, ValidationResult,
    TypeValidationRule, RangeValidationRule, GeometryValidationRule,
    MaterialCompatibilityRule, create_geometry_rules, create_material_rules
)


class HalfCellValidator(ParameterValidator):
    """
    Parameter validator for HalfCell interface (P2D Half Cell).
    
    Validates parameters specific to half-cell simulations including working electrode,
    separator, electrochemical parameters, and simulation control parameters.
    """
    
    def _load_validation_rules(self) -> List[ValidationRule]:
        """Load validation rules for HalfCell interface."""
        rules = []
        
        # Basic type validations
        rules.extend(self._get_type_rules())
        
        # Geometry validations
        rules.extend(create_geometry_rules())
        
        # Half-cell specific geometry validations
        rules.extend(self._get_halfcell_geometry_rules())
        
        # Material compatibility
        rules.extend(create_material_rules())
        
        # Electrochemical parameter validations
        rules.extend(self._get_electrochemical_rules())
        
        # Simulation control validations
        rules.extend(self._get_simulation_control_rules())
        
        # Half-cell specific validations
        rules.extend(self._get_halfcell_specific_rules())
        
        return rules
    
    def _get_type_rules(self) -> List[ValidationRule]:
        """Get type validation rules for HalfCell interface."""
        return [
            TypeValidationRule('project_name', str),
            TypeValidationRule('length', (int, float)),
            TypeValidationRule('width', (int, float)),
            TypeValidationRule('height', (int, float)),
            TypeValidationRule('unit', str),
            TypeValidationRule('x_division', int),
            TypeValidationRule('y_division', int),
            TypeValidationRule('z_division', int),
            
            # Half-cell specific geometry parameters
            TypeValidationRule('we_thickness', (int, float)),
            TypeValidationRule('separator_thickness', (int, float)),
            TypeValidationRule('we_amf', (int, float), optional=True),  # Active material fraction
            TypeValidationRule('separator_porosity', (int, float), optional=True),
            
            # Electrochemical parameters
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
            
            # Half-cell specific electrochemical parameters
            TypeValidationRule('j0', (int, float), optional=True),  # Exchange current density
            TypeValidationRule('cdl', (int, float), optional=True),  # Double layer capacitance
            
            # Simulation control
            TypeValidationRule('endTime', (int, float)),
            TypeValidationRule('deltaT', (int, float)),
            TypeValidationRule('writeInterval', (int, float)),
            TypeValidationRule('tolerance', (int, float)),
            TypeValidationRule('material', str, optional=True),
        ]
    
    def _get_halfcell_geometry_rules(self) -> List[ValidationRule]:
        """Get HalfCell-specific geometry validation rules."""
        return [
            # Working electrode thickness should be positive and reasonable
            RangeValidationRule('we_thickness', min_value=1, max_value=500),
            
            # Separator thickness should be positive and reasonable
            RangeValidationRule('separator_thickness', min_value=5, max_value=100),
            
            # WE active material fraction should be between 0 and 1
            RangeValidationRule('we_amf', min_value=0.01, max_value=0.99),
            
            # Separator porosity should be between 0 and 1
            RangeValidationRule('separator_porosity', min_value=0.2, max_value=0.8),
            
            # Geometry consistency validation
            HalfCellGeometryConsistencyRule(),
        ]
    
    def _get_electrochemical_rules(self) -> List[ValidationRule]:
        """Get electrochemical parameter validation rules."""
        return [
            # DS value (diffusivity) should be positive and reasonable for half-cell
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
            
            # Applied current should be reasonable for half-cell
            RangeValidationRule('I_app', min_value=-10, max_value=10),
            
            # Initial concentration should be between 0 and CS_max
            RangeValidationRule('initial_cs', min_value=0, max_value=50000),
            
            # Half-cell specific parameters
            RangeValidationRule('j0', min_value=1e-8, max_value=1e-2),  # Exchange current density
            RangeValidationRule('cdl', min_value=1e-4, max_value=1e-1),  # Double layer capacitance
        ]
    
    def _get_simulation_control_rules(self) -> List[ValidationRule]:
        """Get simulation control parameter validation rules."""
        return [
            # End time should be positive
            RangeValidationRule('endTime', min_value=0.1, max_value=100000),
            
            # Delta T should be positive and reasonable for half-cell
            RangeValidationRule('deltaT', min_value=1e-6, max_value=1),
            
            # Write interval should be positive
            RangeValidationRule('writeInterval', min_value=0.001, max_value=10000),
            
            # Tolerance should be positive and small
            RangeValidationRule('tolerance', min_value=1e-12, max_value=1e-3),
        ]
    
    def _get_halfcell_specific_rules(self) -> List[ValidationRule]:
        """Get HalfCell-specific validation rules."""
        return [
            # Material should be compatible with half-cell
            HalfCellMaterialRule(),
            
            # Current direction should be consistent with half-cell operation
            HalfCellCurrentRule(),
        ]


class HalfCellGeometryConsistencyRule(ValidationRule):
    """Validates geometry consistency for HalfCell (WE + separator)."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate HalfCell geometry constraints."""
        if 'we_thickness' not in parameters or 'separator_thickness' not in parameters:
            return
        
        we_thickness = parameters['we_thickness']
        sep_thickness = parameters['separator_thickness']
        total_length = parameters.get('length', we_thickness + sep_thickness)
        
        # Check if values are numeric
        if not all(isinstance(v, (int, float)) for v in [we_thickness, sep_thickness, total_length]):
            return
        
        # WE + separator should not exceed total length
        total_region_thickness = we_thickness + sep_thickness
        if total_region_thickness > total_length:
            result.add_error(
                'we_thickness',
                f"Working electrode ({we_thickness}) + separator ({sep_thickness}) = "
                f"{total_region_thickness} exceeds total length ({total_length})"
            )
        
        # WE should be thicker than separator typically
        if we_thickness < sep_thickness:
            result.add_warning(
                'we_thickness',
                f"Working electrode thickness ({we_thickness}) is smaller than "
                f"separator thickness ({sep_thickness}). Verify this is intended."
            )
        
        # Check aspect ratios
        width = parameters.get('width', total_length)
        height = parameters.get('height', total_length)
        
        min_dimension = min(width, height)
        if we_thickness > min_dimension:
            result.add_warning(
                'we_thickness',
                f"Working electrode thickness ({we_thickness}) exceeds "
                f"minimum lateral dimension ({min_dimension}). Consider 2D simulation."
            )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "HalfCell geometry consistency (WE + separator vs total dimensions)"


class HalfCellMaterialRule(ValidationRule):
    """Validates material selection for HalfCell."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate HalfCell material compatibility."""
        material = parameters.get('material', '').lower()
        interface_type = parameters.get('interface_type', '').lower()
        
        if interface_type != 'halfcell':
            return
        
        # Define HalfCell-compatible materials
        halfcell_materials = ['carbon', 'silicon', 'lfp', 'nca']
        
        if material and material not in halfcell_materials:
            result.add_error(
                'material',
                f"Material '{material}' not compatible with HalfCell interface. "
                f"Valid materials: {', '.join(halfcell_materials)}"
            )
        
        # Material-specific validations
        if material == 'carbon':
            # Carbon-specific checks
            pass
        elif material == 'silicon':
            # Silicon-specific checks (higher expansion)
            if 'we_amf' in parameters:
                we_amf = parameters['we_amf']
                if isinstance(we_amf, (int, float)) and we_amf > 0.8:
                    result.add_warning(
                        'we_amf',
                        f"High active material fraction ({we_amf}) with silicon may "
                        f"cause mechanical stress issues."
                    )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "HalfCell material compatibility and constraints"


class HalfCellCurrentRule(ValidationRule):
    """Validates current direction for HalfCell operation."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate HalfCell current direction."""
        if 'I_app' not in parameters:
            return
        
        i_app = parameters['I_app']
        
        if not isinstance(i_app, (int, float)):
            return
        
        # For half-cell, typically:
        # Positive current = intercalation (discharge)
        # Negative current = deintercalation (charge)
        
        # Check for extremely high currents
        if abs(i_app) > 5:
            result.add_warning(
                'I_app',
                f"High current density ({i_app}) may cause numerical instability. "
                f"Consider reducing for better convergence."
            )
        
        # Check for zero current (valid but may indicate user error)
        if i_app == 0:
            result.add_info(
                'I_app',
                "Zero current applied. This will simulate open-circuit conditions."
            )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "HalfCell current direction and magnitude validation"