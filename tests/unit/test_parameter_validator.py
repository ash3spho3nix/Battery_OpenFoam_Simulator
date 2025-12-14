"""
Unit tests for parameter validation system.

This module tests the parameter validation system including
validators, validation rules, and error message management.
"""

import unittest
from src.utils.parameter_validator import (
    ParameterValidator, ValidationRule, ValidationResult,
    ValidationError, SeverityLevel, TypeValidationRule,
    RangeValidationRule, GeometryValidationRule,
    MaterialCompatibilityRule
)
from src.utils.validators.carbon_validator import CarbonValidator
from src.utils.validators.halfcell_validator import HalfCellValidator
from src.utils.validators.fullcell_validator import FullCellValidator
from src.utils.error_message_manager import (
    ErrorMessageManager, ErrorType, get_error_manager
)


class MockValidationRule(ValidationRule):
    """Mock validation rule for testing."""
    
    def __init__(self, should_fail=False, error_field='test', error_message='Test error'):
        self.should_fail = should_fail
        self.error_field = error_field
        self.error_message = error_message
    
    def validate(self, parameters, result):
        if self.should_fail:
            result.add_error(self.error_field, self.error_message)
    
    def get_description(self):
        return "Mock validation rule"


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult."""
    
    def setUp(self):
        self.result = ValidationResult()
    
    def test_initial_state(self):
        """Test initial state of ValidationResult."""
        self.assertTrue(self.result.is_valid)
        self.assertEqual(len(self.result.errors), 0)
        self.assertEqual(len(self.result.warnings), 0)
        self.assertEqual(len(self.result.infos), 0)
    
    def test_add_error(self):
        """Test adding errors."""
        self.result.add_error('field1', 'Error message')
        self.assertFalse(self.result.is_valid)
        self.assertEqual(len(self.result.errors), 1)
        self.assertEqual(self.result.errors[0].field, 'field1')
        self.assertEqual(self.result.errors[0].message, 'Error message')
        self.assertEqual(self.result.errors[0].severity, SeverityLevel.ERROR)
    
    def test_add_warning(self):
        """Test adding warnings."""
        self.result.add_warning('field1', 'Warning message')
        self.assertTrue(self.result.is_valid)  # Warnings don't invalidate
        self.assertEqual(len(self.result.warnings), 1)
        self.assertEqual(self.result.warnings[0].field, 'field1')
        self.assertEqual(self.result.warnings[0].message, 'Warning message')
        self.assertEqual(self.result.warnings[0].severity, SeverityLevel.WARNING)
    
    def test_add_info(self):
        """Test adding info messages."""
        self.result.add_info('field1', 'Info message')
        self.assertTrue(self.result.is_valid)
        self.assertEqual(len(self.result.infos), 1)
        self.assertEqual(self.result.infos[0].field, 'field1')
        self.assertEqual(self.result.infos[0].message, 'Info message')
        self.assertEqual(self.result.infos[0].severity, SeverityLevel.INFO)
    
    def test_has_errors(self):
        """Test has_errors method."""
        self.assertFalse(self.result.has_errors())
        self.result.add_error('field1', 'Error')
        self.assertTrue(self.result.has_errors())
    
    def test_has_warnings(self):
        """Test has_warnings method."""
        self.assertFalse(self.result.has_warnings())
        self.result.add_warning('field1', 'Warning')
        self.assertTrue(self.result.has_warnings())
    
    def test_get_all_messages(self):
        """Test get_all_messages method."""
        self.result.add_error('field1', 'Error message')
        self.result.add_warning('field2', 'Warning message')
        self.result.add_info('field3', 'Info message')
        
        messages = self.result.get_all_messages()
        self.assertEqual(len(messages), 3)
        self.assertIn('[ERROR] field1: Error message', messages)
        self.assertIn('[WARNING] field2: Warning message', messages)
        self.assertIn('[INFO] field3: Info message', messages)


class TestValidationRule(unittest.TestCase):
    """Test cases for validation rules."""
    
    def test_type_validation_rule(self):
        """Test TypeValidationRule."""
        rule = TypeValidationRule('test_field', int)
        result = ValidationResult()
        
        # Valid integer
        rule.validate({'test_field': 42}, result)
        self.assertTrue(result.is_valid)
        
        # Invalid type
        rule.validate({'test_field': 'string'}, result)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        
        # Missing field (required)
        rule.validate({}, result)
        self.assertEqual(len(result.errors), 2)  # Previous error + new error
    
    def test_range_validation_rule(self):
        """Test RangeValidationRule."""
        rule = RangeValidationRule('test_field', min_value=0, max_value=100)
        result = ValidationResult()
        
        # Valid range
        rule.validate({'test_field': 50}, result)
        self.assertTrue(result.is_valid)
        
        # Below minimum
        rule.validate({'test_field': -10}, result)
        self.assertFalse(result.is_valid)
        
        # Above maximum
        rule.validate({'test_field': 150}, result)
        self.assertEqual(len(result.errors), 2)  # Previous error + new error
        
        # Non-numeric value
        rule.validate({'test_field': 'string'}, result)
        self.assertEqual(len(result.errors), 3)
    
    def test_geometry_validation_rule(self):
        """Test GeometryValidationRule."""
        rule = GeometryValidationRule()
        result = ValidationResult()
        
        # Valid geometry
        params = {
            'length': 100,
            'width': 100,
            'height': 100,
            'x_division': 10,
            'y_division': 10,
            'z_division': 10,
            'unit': 'micrometer'
        }
        rule.validate(params, result)
        self.assertTrue(result.is_valid)
        
        # Invalid dimensions
        params['length'] = -10
        rule.validate(params, result)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        
        # Invalid divisions
        params['x_division'] = 0
        rule.validate(params, result)
        self.assertEqual(len(result.errors), 2)
        
        # Invalid unit
        params['unit'] = 'invalid_unit'
        rule.validate(params, result)
        self.assertEqual(len(result.errors), 3)
    
    def test_material_compatibility_rule(self):
        """Test MaterialCompatibilityRule."""
        rule = MaterialCompatibilityRule()
        result = ValidationResult()
        
        # Valid material for carbon
        params = {'interface_type': 'carbon', 'material': 'carbon'}
        rule.validate(params, result)
        self.assertTrue(result.is_valid)
        
        # Invalid material for carbon
        params['material'] = 'invalid_material'
        rule.validate(params, result)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        
        # Valid material for halfcell
        params = {'interface_type': 'halfcell', 'material': 'silicon'}
        rule.validate(params, result)
        self.assertEqual(len(result.errors), 1)  # Previous error still there


class TestParameterValidator(unittest.TestCase):
    """Test cases for ParameterValidator base class."""
    
    def setUp(self):
        class TestValidator(ParameterValidator):
            def _load_validation_rules(self):
                return [
                    MockValidationRule(should_fail=False),
                    MockValidationRule(should_fail=True, error_field='test2', error_message='Test error 2')
                ]
        
        self.validator = TestValidator('test')
    
    def test_validate_success(self):
        """Test successful validation."""
        result = self.validator.validate({'field1': 'value1'})
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].field, 'test2')
    
    def test_validate_with_exception(self):
        """Test validation with rule exception."""
        class FailingRule(ValidationRule):
            def validate(self, parameters, result):
                raise Exception("Rule failed")
            
            def get_description(self):
                return "Failing rule"
        
        class TestValidatorWithException(ParameterValidator):
            def _load_validation_rules(self):
                return [FailingRule()]
        
        validator = TestValidatorWithException('test')
        result = validator.validate({'field1': 'value1'})
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].field, 'system')
    
    def test_get_rule_descriptions(self):
        """Test getting rule descriptions."""
        descriptions = self.validator.get_rule_descriptions()
        self.assertEqual(len(descriptions), 2)
        self.assertIn('Mock validation rule', descriptions)


class TestInterfaceValidators(unittest.TestCase):
        # Valid parameters
        params = {
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
        
        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")
        
        # Invalid parameters - radius too large
        invalid_params = params.copy()
        invalid_params['radius'] = 200.0  # Too large for geometry
        
        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        # Check for radius error (either validation or warning)
        has_radius_issue = any('radius' in error.message.lower() for error in result.errors + result.warnings)
        self.assertTrue(has_radius_issue, "Expected radius validation error/warning")
    """Test cases for interface-specific validators."""
    def test_carbon_validator(self):
        """Test CarbonValidator."""
        validator = CarbonValidator('carbon')

        # Valid parameters
        params = {
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

        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")

        # Invalid parameters - radius too large
        invalid_params = params.copy()
        invalid_params['radius'] = 200.0  # Too large for geometry

        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        # Check for radius error (either validation or warning)
        has_radius_issue = any('radius' in error.message.lower() for error in result.errors + result.warnings)
        self.assertTrue(has_radius_issue, "Expected radius validation error/warning")
    
    def test_carbon_validator(self):
        """Test CarbonValidator."""
        validator = CarbonValidator('carbon')
        
        # Valid parameters
        params = {
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
        # Valid parameters
        params = {
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
        
        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Valid parameters failed: {result.get_all_messages()}")
        
        # Invalid parameters - radius too large
        invalid_params = params.copy()
        invalid_params['radius'] = 200.0  # Too large for geometry
        
        result = validator.validate(invalid_params)
        self.assertFalse(result.is_valid)
        # Check for radius error (either validation or warning)
        has_radius_issue = any('radius' in error.message.lower() for error in result.errors + result.warnings)
        self.assertTrue(has_radius_issue, "Expected radius validation error/warning")
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
        
        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Validation failed: {result.get_all_messages()}")
    
    def test_carbon_validator_invalid_radius(self):
        """Test CarbonValidator with invalid radius."""
        validator = CarbonValidator('carbon')
        
        params = {
            'length': 100.0,
            'width': 100.0,
            'height': 100.0,
            'radius': 200.0,  # Too large
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
        
        result = validator.validate(params)
        self.assertFalse(result.is_valid)
        self.assertTrue(any('radius' in error.message for error in result.errors))
    
    def test_halfcell_validator(self):
        """Test HalfCellValidator."""
        validator = HalfCellValidator('halfcell')
        
        params = {
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
        self.assertEqual(message.severity, 'error')
        self.assertEqual(message.title, 'Parameter Type Error')
        self.assertIn('test_field', message.message)
        # Updated to match actual error message format
        self.assertIn('string', message.message)  # This should now pass
            'deltaT': 0.1,
            'writeInterval': 1.0,
            'tolerance': 1e-6,
            'material': 'carbon'
        }
        
        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Validation failed: {result.get_all_messages()}")
    
    def test_fullcell_validator(self):
        """Test FullCellValidator."""
        validator = FullCellValidator('fullcell')
        
        params = {
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
        
        result = validator.validate(params)
        self.assertTrue(result.is_valid, f"Validation failed: {result.get_all_messages()}")


class TestErrorMessageManager(unittest.TestCase):
    """Test cases for ErrorMessageManager."""
    
    def setUp(self):
        self.manager = ErrorMessageManager()
    
    def test_get_error_message(self):
        """Test getting error messages."""
        context = {'field': 'test_field', 'value': 'invalid_value'}
        message = self.manager.get_error_message(
            ErrorType.PARAMETER_INVALID,
            context,
            'error'
        )
        
        self.assertEqual(message.severity, 'error')
        self.assertEqual(message.title, 'Invalid Parameter')
        self.assertIn('test_field', message.message)
        self.assertIn('invalid_value', message.message)
    
    def test_get_validation_error_message(self):
        """Test getting validation error messages."""
        message = self.manager.get_validation_error_message(
            'test_field',
            'type',
            'string',
            'integer'
        )
        
        self.assertEqual(message.severity, 'error')
        self.assertEqual(message.title, 'Parameter Type Error')
        self.assertIn('test_field', message.message)
        self.assertIn('string', message.message)
        self.assertIn('integer', message.message)
    
    def test_format_user_message(self):
        """Test formatting user messages."""
        message = self.manager.get_error_message(
            ErrorType.GEOMETRY_INVALID,
            {'details': 'test details'},
            'error'
        )
        
        formatted = self.manager.format_user_message(message)
        self.assertIn('❌', formatted)
        self.assertIn('Invalid Geometry Parameters', formatted)
        self.assertIn('test details', formatted)
    
    def test_get_error_manager_singleton(self):
        """Test that get_error_manager returns the same instance."""
        manager1 = get_error_manager()
        manager2 = get_error_manager()
        self.assertIs(manager1, manager2)


if __name__ == '__main__':
    unittest.main()