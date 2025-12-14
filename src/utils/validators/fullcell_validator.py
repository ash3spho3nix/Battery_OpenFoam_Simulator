"""
FullCell interface parameter validator.

This module provides parameter validation specific to the FullCell interface (P2D Full Cell).
"""

from typing import Dict, Any, List
from ..parameter_validator import (
    ParameterValidator, ValidationRule, ValidationResult,
    TypeValidationRule, RangeValidationRule, GeometryValidationRule,
    MaterialCompatibilityRule, create_geometry_rules, create_material_rules
)


class FullCellValidator(ParameterValidator):
    """
    Parameter validator for FullCell interface (P2D Full Cell).
    
    Validates parameters specific to full-cell simulations including anode,
    cathode, separator, electrochemical parameters, and simulation control parameters.
    """
    
    def _load_validation_rules(self) -> List[ValidationRule]:
        """Load validation rules for FullCell interface."""
        rules = []
        
        # Basic type validations
        rules.extend(self._get_type_rules())
        
        # Geometry validations
        rules.extend(create_geometry_rules())
        
        # Full-cell specific geometry validations
        rules.extend(self._get_fullcell_geometry_rules())
        
        # Material compatibility
        rules.extend(create_material_rules())
        
        # Electrochemical parameter validations
        rules.extend(self._get_electrochemical_rules())
        
        # Simulation control validations
        rules.extend(self._get_simulation_control_rules())
        
        # Full-cell specific validations
        rules.extend(self._get_fullcell_specific_rules())
        
        return rules
    
    def _get_type_rules(self) -> List[ValidationRule]:
        """Get type validation rules for FullCell interface."""
        return [
            TypeValidationRule('project_name', str),
            TypeValidationRule('length', (int, float)),
            TypeValidationRule('width', (int, float)),
            TypeValidationRule('height', (int, float)),
            TypeValidationRule('unit', str),
            TypeValidationRule('x_division', int),
            TypeValidationRule('y_division', int),
            TypeValidationRule('z_division', int),
            
            # Full-cell specific geometry parameters
            TypeValidationRule('anode_thickness', (int, float)),
            TypeValidationRule('cathode_thickness', (int, float)),
            TypeValidationRule('separator_thickness', (int, float)),
            TypeValidationRule('anode_material', str),
            TypeValidationRule('cathode_material', str),
            TypeValidationRule('anode_amf', (int, float), optional=True),  # Active material fraction
            TypeValidationRule('cathode_amf', (int, float), optional=True),
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
            
            # Full-cell specific electrochemical parameters
            TypeValidationRule('electrolyte_concentration', (int, float), optional=True),
            TypeValidationRule('anode_diffusivity', (int, float), optional=True),
            TypeValidationRule('cathode_diffusivity', (int, float), optional=True),
            
            # Simulation control
            TypeValidationRule('endTime', (int, float)),
            TypeValidationRule('deltaT', (int, float)),
            TypeValidationRule('writeInterval', (int, float)),
            TypeValidationRule('tolerance', (int, float)),
        ]
    
    def _get_fullcell_geometry_rules(self) -> List[ValidationRule]:
        """Get FullCell-specific geometry validation rules."""
        return [
            # Anode thickness should be positive and reasonable
            RangeValidationRule('anode_thickness', min_value=10, max_value=300),
            
            # Cathode thickness should be positive and reasonable
            RangeValidationRule('cathode_thickness', min_value=10, max_value=300),
            
            # Separator thickness should be positive and reasonable
            RangeValidationRule('separator_thickness', min_value=5, max_value=50),
            
            # Active material fractions should be between 0 and 1
            RangeValidationRule('anode_amf', min_value=0.01, max_value=0.99),
            RangeValidationRule('cathode_amf', min_value=0.01, max_value=0.99),
            
            # Separator porosity should be between 0 and 1
            RangeValidationRule('separator_porosity', min_value=0.2, max_value=0.8),
            
            # Geometry consistency validation
            FullCellGeometryConsistencyRule(),
        ]
    
    def _get_electrochemical_rules(self) -> List[ValidationRule]:
        """Get electrochemical parameter validation rules."""
        return [
            # DS value (diffusivity) should be positive and reasonable for full-cell
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
            
            # Applied current should be reasonable for full-cell
            RangeValidationRule('I_app', min_value=-5, max_value=5),
            
            # Initial concentration should be between 0 and CS_max
            RangeValidationRule('initial_cs', min_value=0, max_value=50000),
            
            # Full-cell specific parameters
            RangeValidationRule('electrolyte_concentration', min_value=500, max_value=2000),
            RangeValidationRule('anode_diffusivity', min_value=1e-20, max_value=1e-6),
            RangeValidationRule('cathode_diffusivity', min_value=1e-20, max_value=1e-6),
        ]
    
    def _get_simulation_control_rules(self) -> List[ValidationRule]:
        """Get simulation control parameter validation rules."""
        return [
            # End time should be positive
            RangeValidationRule('endTime', min_value=0.1, max_value=100000),
            
            # Delta T should be positive and reasonable for full-cell
            RangeValidationRule('deltaT', min_value=1e-6, max_value=1),
            
            # Write interval should be positive
            RangeValidationRule('writeInterval', min_value=0.001, max_value=10000),
            
            # Tolerance should be positive and small
            RangeValidationRule('tolerance', min_value=1e-12, max_value=1e-3),
        ]
    
    def _get_fullcell_specific_rules(self) -> List[ValidationRule]:
        """Get FullCell-specific validation rules."""
        return [
            # Material compatibility for full-cell
            FullCellMaterialRule(),
            
            # Anode-cathode material pairing
            FullCellMaterialPairingRule(),
            
            # Current direction and magnitude
            FullCellCurrentRule(),
            
            # Electrode balancing
            FullCellBalancingRule(),
        ]


class FullCellGeometryConsistencyRule(ValidationRule):
    """Validates geometry consistency for FullCell (anode + separator + cathode)."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate FullCell geometry constraints."""
        required_params = ['anode_thickness', 'separator_thickness', 'cathode_thickness']
        if not all(param in parameters for param in required_params):
            return
        
        anode_thick = parameters['anode_thickness']
        sep_thick = parameters['separator_thickness']
        cathode_thick = parameters['cathode_thickness']
        total_length = parameters.get('length', anode_thick + sep_thick + cathode_thick)
        
        # Check if values are numeric
        if not all(isinstance(v, (int, float)) for v in [anode_thick, sep_thick, cathode_thick, total_length]):
            return
        
        # Anode + separator + cathode should not exceed total length
        total_region_thickness = anode_thick + sep_thick + cathode_thick
        if total_region_thickness > total_length:
            result.add_error(
                'anode_thickness',
                f"Anode ({anode_thick}) + separator ({sep_thick}) + cathode ({cathode_thick}) = "
                f"{total_region_thickness} exceeds total length ({total_length})"
            )
        
        # Separator should be thinner than electrodes typically
        if sep_thick > min(anode_thick, cathode_thick):
            result.add_warning(
                'separator_thickness',
                f"Separator thickness ({sep_thick}) is larger than "
                f"electrode thickness. Verify this is intended."
            )
        
        # Check aspect ratios
        width = parameters.get('width', total_length)
        height = parameters.get('height', total_length)
        
        min_dimension = min(width, height)
        max_electrode_thick = max(anode_thick, cathode_thick)
        if max_electrode_thick > min_dimension:
            result.add_warning(
                'anode_thickness',
                f"Electrode thickness ({max_electrode_thick}) exceeds "
                f"minimum lateral dimension ({min_dimension}). Consider 2D simulation."
            )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "FullCell geometry consistency (anode + separator + cathode vs total dimensions)"


class FullCellMaterialRule(ValidationRule):
    """Validates material selection for FullCell."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate FullCell material compatibility."""
        anode_material = parameters.get('anode_material', '').lower()
        cathode_material = parameters.get('cathode_material', '').lower()
        interface_type = parameters.get('interface_type', '').lower()
        
        if interface_type != 'fullcell':
            return
        
        # Define FullCell-compatible materials
        anode_materials = ['carbon', 'silicon', 'graphite']
        cathode_materials = ['lfp', 'nca', 'lionsimba', 'lco', 'nmc']
        
        # Validate anode material
        if anode_material and anode_material not in anode_materials:
            result.add_error(
                'anode_material',
                f"Anode material '{anode_material}' not compatible with FullCell interface. "
                f"Valid anode materials: {', '.join(anode_materials)}"
            )
        
        # Validate cathode material
        if cathode_material and cathode_material not in cathode_materials:
            result.add_error(
                'cathode_material',
                f"Cathode material '{cathode_material}' not compatible with FullCell interface. "
                f"Valid cathode materials: {', '.join(cathode_materials)}"
            )
        
        # Material-specific validations
        if anode_material == 'silicon':
            # Silicon-specific checks (higher expansion)
            if 'anode_amf' in parameters:
                anode_amf = parameters['anode_amf']
                if isinstance(anode_amf, (int, float)) and anode_amf > 0.7:
                    result.add_warning(
                        'anode_amf',
                        f"High active material fraction ({anode_amf}) with silicon may "
                        f"cause mechanical stress issues."
                    )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "FullCell material compatibility and constraints"


class FullCellMaterialPairingRule(ValidationRule):
    """Validates anode-cathode material pairing for FullCell."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate FullCell material pairing."""
        anode_material = parameters.get('anode_material', '').lower()
        cathode_material = parameters.get('cathode_material', '').lower()
        
        if not anode_material or not cathode_material:
            return
        
        # Define valid material pairings
        valid_pairings = {
            'carbon': ['lfp', 'nca', 'lionsimba', 'lco', 'nmc'],
            'silicon': ['lfp', 'nca', 'lionsimba'],
            'graphite': ['lfp', 'nca', 'lionsimba', 'lco', 'nmc']
        }
        
        if anode_material in valid_pairings:
            if cathode_material not in valid_pairings[anode_material]:
                result.add_warning(
                    'cathode_material',
                    f"Material pairing '{anode_material}' + '{cathode_material}' "
                    f"may not be optimal. Consider using one of: "
                    f"{', '.join(valid_pairings[anode_material])}"
                )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "FullCell anode-cathode material pairing validation"


class FullCellCurrentRule(ValidationRule):
    """Validates current direction for FullCell operation."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate FullCell current direction."""
        if 'I_app' not in parameters:
            return
        
        i_app = parameters['I_app']
        
        if not isinstance(i_app, (int, float)):
            return
        
        # For full-cell, typically:
        # Positive current = charge (Li moves from cathode to anode)
        # Negative current = discharge (Li moves from anode to cathode)
        
        # Check for extremely high currents
        if abs(i_app) > 2:
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
        return "FullCell current direction and magnitude validation"


class FullCellBalancingRule(ValidationRule):
    """Validates electrode balancing for FullCell."""
    
    def validate(self, parameters: Dict[str, Any], result: ValidationResult) -> None:
        """Validate FullCell electrode balancing."""
        if 'anode_thickness' not in parameters or 'cathode_thickness' not in parameters:
            return
        
        anode_thick = parameters['anode_thickness']
        cathode_thick = parameters['cathode_thickness']
        
        # Check if values are numeric
        if not all(isinstance(v, (int, float)) for v in [anode_thick, cathode_thick]):
            return
        
        # Check thickness ratio
        thickness_ratio = anode_thick / cathode_thick if cathode_thick > 0 else float('inf')
        
        # Typical full-cell has cathode thicker than anode
        if thickness_ratio > 2:
            result.add_warning(
                'anode_thickness',
                f"Anode thickness ({anode_thick}) is much larger than "
                f"cathode thickness ({cathode_thick}). This may affect cell balancing."
            )
        elif thickness_ratio < 0.5:
            result.add_warning(
                'cathode_thickness',
                f"Cathode thickness ({cathode_thick}) is much larger than "
                f"anode thickness ({anode_thick}). This may affect cell balancing."
            )
        
        # Check for N/P ratio considerations (if active material fractions available)
        if 'anode_amf' in parameters and 'cathode_amf' in parameters:
            anode_amf = parameters['anode_amf']
            cathode_amf = parameters['cathode_amf']
            
            if all(isinstance(v, (int, float)) for v in [anode_amf, cathode_amf]):
                # Simple N/P ratio estimation
                np_ratio = (anode_thick * anode_amf) / (cathode_thick * cathode_amf)
                
                if np_ratio < 0.8:
                    result.add_warning(
                        'anode_amf',
                        f"N/P ratio ({np_ratio:.2f}) is low. Consider increasing "
                        f"anode capacity or decreasing cathode capacity."
                    )
                elif np_ratio > 1.2:
                    result.add_warning(
                        'cathode_amf',
                        f"N/P ratio ({np_ratio:.2f}) is high. Consider decreasing "
                        f"anode capacity or increasing cathode capacity."
                    )
    
    def get_description(self) -> str:
        """Get rule description."""
        return "FullCell electrode balancing (N/P ratio and thickness ratio)"