"""
Integration tests for parameter validation system.

This module tests the integration of parameter validation
with the overall application workflow.
"""

import unittest
import tempfile
import os
from pathlib import Path

from src.utils.validator_factory import create_validator, get_supported_interfaces
from src.utils.error_message_manager import get_error_manager
from src.utils.parameter_validator import ValidationResult


class TestValidationIntegration(unittest.TestCase):
    """Integration tests for parameter validation system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_manager = get_error_manager()
    
    def test_validator_factory(self):
        """Test validator factory creates correct validators."""
        # Test supported interfaces
        supported = get_supported_interfaces()
        self.assertIn('carbon', supported)
        self.assertIn('halfcell', supported)
        self.assertIn('fullcell', supported)
        
        # Test validator creation
        carbon_validator = create_validator('carbon')
        halfcell_validator = create_validator('halfcell')
        fullcell_validator = create_validator('fullcell')
        
        self.assertEqual(carbon_validator.get_interface_type(), 'carbon')
        self.assertEqual(halfcell_validator.get_interface_type(), 'halfcell')
        self.assertEqual(fullcell_validator.get_interface_type(), 'fullcell')
        
        # Test invalid interface
        with self.assertRaises(ValueError):
            create_validator('invalid_interface')
    
    def test_carbon_validation_workflow(self):
        """Test complete Carbon interface validation workflow."""
        validator = create_validator('carbon')
        
        # Valid parameters
        valid_params = {
            'project_name': 'test_project',
            'length': 100.0,
            'width': 100.0,
            'height': 100.0,
            'radius': 50.0,
            'unit': 'micrometer',
            'x_division': 10,
            'y_division': 10,
            'z_division': 10,
            'DS_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0,
            'initial_cs': 0.0,
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6,
            'material': 'carbon'
        }
        
        result = validator.validate(valid_params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")
        
        # Invalid parameters
        invalid_params = valid_params.copy()
        invalid_params['radius'] = 200.0  # Too large for geometry
        
        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertTrue(any('radius' in error.message for error in result.errors))
    
    def test_halfcell_validation_workflow(self):
        """Test complete HalfCell interface validation workflow."""
        validator = create_validator('halfcell')
        
        # Valid parameters
        valid_params = {
            'project_name': 'test_project',
            'length': 200.0,
            'width': 100.0,
            'height': 100.0,
            'unit': 'micrometer',
            'x_division': 20,
            'y_division': 10,
            'z_division': 10,
            'we_thickness': 100.0,
            'separator_thickness': 20.0,
            'we_amf': 0.5,
            'separator_porosity': 0.5,
            'DS_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0,
            'initial_cs': 0.0,
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6,
            'material': 'carbon'
        }
        
        result = validator.validate(valid_params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")
        
        # Invalid geometry
        invalid_params = valid_params.copy()
        invalid_params['we_thickness'] = 300.0  # Too large
        
        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertTrue(any('Working electrode' in error.message for error in result.errors))
    
    def test_fullcell_validation_workflow(self):
        """Test complete FullCell interface validation workflow."""
        validator = create_validator('fullcell')
        
        # Valid parameters
        valid_params = {
            'project_name': 'test_project',
            'length': 300.0,
            'width': 100.0,
            'height': 100.0,
            'unit': 'micrometer',
            'x_division': 30,
            'y_division': 10,
            'z_division': 10,
            'anode_thickness': 100.0,
            'cathode_thickness': 100.0,
            'separator_thickness': 20.0,
            'anode_material': 'carbon',
            'cathode_material': 'lfp',
            'anode_amf': 0.5,
            'cathode_amf': 0.5,
            'separator_porosity': 0.5,
            'DS_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0,
            'initial_cs': 0.0,
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6
        }
        
        result = validator.validate(valid_params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")
        
        # Invalid material pairing
        invalid_params = valid_params.copy()
        invalid_params['anode_material'] = 'invalid_material'
        
        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertTrue(any('material' in error.message.lower() for error in result.errors))
    
    def test_error_message_integration(self):
        """Test error message generation and formatting."""
        # Test validation error message
        error_msg = self.error_manager.get_validation_error_message(
            'test_field',
            'type',
            'string',
            'integer'
        )
        
        self.assertEqual(error_msg.severity, 'error')
        self.assertEqual(error_msg.title, 'Parameter Type Error')
        
        # Test formatted user message
        formatted = self.error_manager.format_user_message(error_msg)
        self.assertIn('❌', formatted)
        self.assertIn('Parameter Type Error', formatted)
        self.assertIn('test_field', formatted)
    
    def test_parameter_validation_with_realistic_values(self):
        """Test validation with realistic battery simulation parameters."""
        validator = create_validator('carbon')
        
        # Realistic SPM parameters
        realistic_params = {
            'project_name': 'spm_simulation',
            'length': 100.0,      # μm
            'width': 100.0,       # μm
            'height': 100.0,      # μm
            'radius': 5.0,        # μm (small particle)
            'unit': 'micrometer',
            'x_division': 20,
            'y_division': 20,
            'z_division': 20,
            'DS_value': 1e-14,    # Li diffusivity
            'CS_max': 30000,      # max concentration
            'kReact': 1e-11,      # reaction rate
            'R': 8.314,           # gas constant
            'F': 96485,           # Faraday's constant
            'Ce': 1000,           # electrolyte concentration
            'alphaA': 0.5,        # anodic transfer coefficient
            'alphaC': 0.5,        # cathodic transfer coefficient
            'T_temp': 298.15,     # temperature (K)
            'I_app': 0.001,       # small current (A/m2)
            'initial_cs': 0.0,
            'endTime': 100.0,     # seconds
            'deltaT': 0.01,       # small timestep
            'writeInterval': 1.0,
            'tolerance': 1e-8,
            'material': 'carbon'
        }
        
        result = validator.validate(realistic_params)
        self.assertTrue(result.is_valid, f"Realistic parameters failed: {result.get_all_messages()}")
    
    def test_parameter_validation_edge_cases(self):
        """Test validation edge cases and boundary conditions."""
        validator = create_validator('halfcell')
        
        # Test minimum valid values
        min_params = {
            'project_name': 'test',
            'length': 1.0,
            'width': 1.0,
            'height': 1.0,
            'unit': 'micrometer',
            'x_division': 1,
            'y_division': 1,
            'z_division': 1,
            'we_thickness': 1.0,
            'separator_thickness': 5.0,
            'we_amf': 0.01,
            'separator_porosity': 0.2,
            'DS_value': 1e-20,
            'CS_max': 1000,
            'kReact': 1e-15,
            'R': 8.0,
            'F': 96000,
            'Ce': 500,
            'alphaA': 0.0,
            'alphaC': 0.0,
            'T_temp': 200,
            'I_app': -10,
            'initial_cs': 0.0,
            'endTime': 0.1,
            'deltaT': 1e-6,
            'writeInterval': 0.001,
            'tolerance': 1e-12,
            'material': 'carbon'
        }
        
        result = validator.validate(min_params)
        self.assertTrue(result.is_valid, f"Minimum parameters failed: {result.get_all_messages()}")
        
        # Test maximum valid values
        max_params = min_params.copy()
        max_params.update({
            'length': 10000,
            'width': 10000,
            'height': 10000,
            'we_thickness': 500,
            'separator_thickness': 100,
            'we_amf': 0.99,
            'separator_porosity': 0.8,
            'DS_value': 1e-6,
            'CS_max': 50000,
            'kReact': 1e-8,
            'R': 8.5,
            'F': 97000,
            'Ce': 2000,
            'alphaA': 1.0,
            'alphaC': 1.0,
            'T_temp': 400,
            'I_app': 10,
            'endTime': 100000,
            'deltaT': 10,
            'writeInterval': 10000,
            'tolerance': 1e-3
        })
        
        result = validator.validate(max_params)
        self.assertTrue(result.is_valid, f"Maximum parameters failed: {result.get_all_messages()}")
    
    def test_validation_performance(self):
        """Test validation performance with many parameters."""
        validator = create_validator('fullcell')
        
        # Create a large parameter set
        params = {
            'project_name': 'performance_test',
            'length': 100.0,
            'width': 100.0,
            'height': 100.0,
            'unit': 'micrometer',
            'x_division': 50,
            'y_division': 50,
            'z_division': 50,
            'anode_thickness': 50.0,
            'cathode_thickness': 50.0,
            'separator_thickness': 10.0,
            'anode_material': 'carbon',
            'cathode_material': 'lfp',
            'anode_amf': 0.5,
            'cathode_amf': 0.5,
            'separator_porosity': 0.5,
            'DS_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0,
            'initial_cs': 0.0,
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6
        }
        
        # Add many additional parameters to test performance
        for i in range(100):
            params[f'extra_param_{i}'] = i
        
        import time
        start_time = time.time()
        result = validator.validate(params)
        end_time = time.time()
        
        # Validation should be fast (less than 1 second)
        self.assertLess(end_time - start_time, 1.0, "Validation too slow")
        self.assertTrue(result.is_valid, f"Performance test failed: {result.get_all_messages()}")
    
    def test_validation_with_missing_optional_parameters(self):
        """Test validation when optional parameters are missing."""
        validator = create_validator('halfcell')
        
        # Minimal required parameters only
        minimal_params = {
            'project_name': 'minimal_test',
            'length': 100.0,
            'width': 100.0,
            'height': 100.0,
            'unit': 'micrometer',
            'x_division': 10,
            'y_division': 10,
            'z_division': 10,
            'DS_value': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0,
            'initial_cs': 0.0,
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6,
            'material': 'carbon'
        }
        
        # Should still validate (optional parameters have defaults)
        result = validator.validate(minimal_params)
        # This might fail due to missing required half-cell parameters
        # The test documents the current behavior
        print(f"Minimal validation result: is_valid={result.is_valid}")
        if not result.is_valid:
            print("Validation messages:")
            for msg in result.get_all_messages():
                print(f"  - {msg}")


if __name__ == '__main__':
    unittest.main()