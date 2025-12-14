# Phase 1 Implementation Guide: Parameter Validation & Error Messaging

## 🎯 Phase 1 Overview

**Duration**: 2-3 days  
**Priority**: 🔴 **CRITICAL**  
**Objective**: Create unified systems for parameter validation and error handling across all interfaces

## 📋 Implementation Checklist

### Day 1: Parameter Validation System

#### Task 1.1: Create Base Validator Class
**Estimated Time**: 2-3 hours  
**Priority**: 🔴 **CRITICAL**

**File**: `src/utils/parameter_validator.py`

**Implementation Steps**:
1. Create the base `ParameterValidator` class
2. Define the `ValidationResult` and `ValidationError` classes
3. Implement core validation logic
4. Add interface type detection

**Code Structure**:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def add_error(self, field: str, message: str, severity: str = 'error'):
        error = ValidationError(field, message, severity)
        if severity == 'error':
            self.errors.append(error)
            self.is_valid = False
        else:
            self.warnings.append(error)

class ParameterValidator(ABC):
    def __init__(self, interface_type: str):
        self.interface_type = interface_type
        self.rules = self._load_validation_rules()
    
    @abstractmethod
    def _load_validation_rules(self) -> List['ValidationRule']:
        pass
    
    def validate(self, parameters: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(True, [], [])
        for rule in self.rules:
            rule.validate(parameters, result)
        return result
```

#### Task 1.2: Create Validation Rules Engine
**Estimated Time**: 2-3 hours  
**Priority**: 🔴 **CRITICAL**

**File**: `src/utils/validation_rules.py`

**Implementation Steps**:
1. Create base `ValidationRule` class
2. Implement common validation rules (type, range, dependencies)
3. Create interface-specific rule classes
4. Add rule chaining and conditional validation

**Key Rules to Implement**:
- `TypeValidationRule`: Validate parameter types
- `RangeValidationRule`: Validate numeric ranges
- `DependencyValidationRule`: Validate parameter dependencies
- `GeometryValidationRule`: Validate geometry constraints
- `MaterialValidationRule`: Validate material compatibility

#### Task 1.3: Create Interface-Specific Validators
**Estimated Time**: 3-4 hours  
**Priority**: 🔴 **CRITICAL**

**Files**: 
- `src/utils/validators/carbon_validator.py`
- `src/utils/validators/halfcell_validator.py`
- `src/utils/validators/fullcell_validator.py`

**Implementation Steps**:
1. Create `CarbonValidator` class
2. Create `HalfCellValidator` class with WE/separator rules
3. Create `FullCellValidator` class with multi-region rules
4. Implement interface-specific validation logic

**HalfCell-Specific Rules**:
```python
class HalfCellValidator(ParameterValidator):
    def _load_validation_rules(self) -> List[ValidationRule]:
        return [
            GeometryRule(),           # WE + separator < total length
            MaterialRule(),           # Material compatibility
            ElectrochemicalRule(),    # Electrochemical parameter ranges
            BoundaryRule()            # Boundary condition validation
        ]
```

#### Task 1.4: Add Real-time Validation to Interfaces
**Estimated Time**: 2-3 hours  
**Priority**: 🟡 **HIGH**

**Files**: Update existing interface files

**Implementation Steps**:
1. Add validator initialization to BaseInterface
2. Create validation callback methods
3. Add real-time validation on parameter changes
4. Update UI state based on validation results

**Integration Points**:
```python
class BaseInterface(QWidget):
    def __init__(self, parent=None, ui_config=None):
        # ... existing code ...
        self.validator = self._create_validator()
        self._setup_validation_callbacks()
    
    def _create_validator(self):
        from src.utils.parameter_validator import ParameterValidator
        # Create appropriate validator based on interface type
    
    def _setup_validation_callbacks(self):
        # Connect parameter change signals to validation
        self.length_edit.textChanged.connect(self._on_parameter_changed)
        # ... connect other parameter widgets ...
    
    def _on_parameter_changed(self):
        parameters = self.get_parameters()
        result = self.validator.validate(parameters)
        self._update_validation_ui(result)
```

### Day 2: Error Messaging System

#### Task 2.1: Create Error Message Manager
**Estimated Time**: 2-3 hours  
**Priority**: 🔴 **CRITICAL**

**File**: `src/utils/error_message_manager.py`

**Implementation Steps**:
1. Create `ErrorMessageManager` class
2. Define error message templates
3. Implement context-aware message generation
4. Add severity level handling

**Code Structure**:
```python
class ErrorMessageManager:
    def __init__(self):
        self.message_templates = self._load_message_templates()
        self.severity_levels = {
            'error': '❌ Error',
            'warning': '⚠️ Warning', 
            'info': 'ℹ️ Info'
        }
    
    def get_error_message(self, error_type: str, context: Dict[str, Any]) -> str:
        template = self.message_templates.get(error_type, 'Unknown error')
        return template.format(**context)
    
    def _load_message_templates(self) -> Dict[str, str]:
        return {
            'geometry_invalid': 'Invalid geometry parameters: {details}',
            'material_incompatible': 'Material {material} is not compatible with {interface}',
            'solver_failed': 'Solver execution failed: {error_code}',
            'template_missing': 'Template {template_name} not found in {template_path}'
        }
```

#### Task 2.2: Define Error Message Templates
**Estimated Time**: 1-2 hours  
**Priority**: 🟡 **HIGH**

**File**: `src/utils/error_templates.py`

**Implementation Steps**:
1. Create comprehensive error message templates
2. Organize templates by category (geometry, materials, solver, etc.)
3. Add user-friendly and technical message variants
4. Include actionable guidance in messages

**Template Categories**:
- Geometry errors (dimensions, divisions, units)
- Material errors (compatibility, properties)
- Solver errors (compilation, execution, convergence)
- Template errors (missing, invalid, corrupted)
- System errors (permissions, paths, dependencies)

#### Task 2.3: Integrate Error Messaging with Validation
**Estimated Time**: 2-3 hours  
**Priority**: 🔴 **CRITICAL**

**Files**: Update validation system

**Implementation Steps**:
1. Connect error message manager to validators
2. Update validation error generation
3. Add context information to errors
4. Implement error display in UI

**Integration**:
```python
class ParameterValidator:
    def __init__(self, interface_type: str):
        self.interface_type = interface_type
        self.error_manager = ErrorMessageManager()
        # ... rest of initialization ...
    
    def _create_validation_error(self, error_type: str, context: Dict[str, Any]) -> ValidationError:
        message = self.error_manager.get_error_message(error_type, context)
        return ValidationError(context.get('field', 'unknown'), message, 'error')
```

#### Task 2.4: Add Error Display to Interfaces
**Estimated Time**: 2-3 hours  
**Priority**: 🟡 **HIGH**

**Files**: Update interface files

**Implementation Steps**:
1. Add error display widgets to interfaces
2. Create error context display
3. Add error severity indicators
4. Implement error resolution guidance

**UI Components**:
```python
class BaseInterface(QWidget):
    def _setup_error_display(self):
        self.error_display = QGroupBox("Validation Status")
        self.error_layout = QVBoxLayout()
        
        self.error_list = QListWidget()
        self.error_layout.addWidget(self.error_list)
        
        self.error_details = QTextEdit()
        self.error_details.setReadOnly(True)
        self.error_layout.addWidget(self.error_details)
        
        self.error_display.setLayout(self.error_layout)
        # Add to appropriate tab/layout
```

### Day 3: Testing & Integration

#### Task 3.1: Create Unit Tests
**Estimated Time**: 3-4 hours  
**Priority**: 🔴 **CRITICAL**

**Files**: 
- `tests/unit/test_parameter_validator.py`
- `tests/unit/test_validation_rules.py`
- `tests/unit/test_error_message_manager.py`

**Implementation Steps**:
1. Create comprehensive unit tests for validation system
2. Test all validation rules
3. Test error message generation
4. Test edge cases and error conditions

**Test Coverage**:
- Parameter validation for all interface types
- Validation rule functionality
- Error message template rendering
- Context handling and severity levels

#### Task 3.2: Create Integration Tests
**Estimated Time**: 2-3 hours  
**Priority**: 🟡 **HIGH**

**File**: `tests/integration/test_validation_integration.py`

**Implementation Steps**:
1. Test validation integration with interfaces
2. Test real-time validation functionality
3. Test error display integration
4. Test validation performance

**Integration Points**:
- Interface parameter validation
- Real-time validation callbacks
- Error display updates
- UI state changes based on validation

#### Task 3.3: Performance Testing & Optimization
**Estimated Time**: 1-2 hours  
**Priority**: 🟢 **MEDIUM**

**Implementation Steps**:
1. Test validation performance with large parameter sets
2. Optimize validation rule execution
3. Add caching for expensive validation operations
4. Test memory usage

**Performance Targets**:
- Validation response time < 100ms
- Memory usage < 10MB for validation system
- No memory leaks in long-running operations

## 🔧 Technical Implementation Details

### Parameter Structure Definition

**Common Parameters**:
```python
COMMON_PARAMETERS = {
    'project_name': str,
    'length': float,      # μm
    'width': float,       # μm  
    'height': float,      # μm
    'radius': float,      # μm (for particles)
    'unit': str,          # 'micrometer', 'millimeter', 'meter'
    'x_division': int,
    'y_division': int,
    'z_division': int,
    'endTime': float,
    'deltaT': float,
    'writeInterval': float,
    'tolerance': float
}
```

**HalfCell-Specific Parameters**:
```python
HALFCELL_PARAMETERS = {
    'we_thickness': float,      # Working electrode thickness
    'we_amf': float,            # Working electrode active material fraction
    'separator_thickness': float,
    'separator_porosity': float,
    'j0': float,                # Exchange current density
    'cdl': float,               # Double layer capacitance
    'material': str             # 'carbon', 'silicon', etc.
}
```

**FullCell-Specific Parameters**:
```python
FULLCELL_PARAMETERS = {
    'anode_thickness': float,
    'anode_material': str,
    'anode_amf': float,
    'cathode_thickness': float,
    'cathode_material': str,
    'cathode_amf': float,
    'separator_thickness': float,
    'separator_porosity': float,
    'electrolyte_concentration': float
}
```

### Validation Rule Examples

**Geometry Validation Rule**:
```python
class GeometryValidationRule(ValidationRule):
    def validate(self, parameters: Dict[str, Any], result: ValidationResult):
        # Check dimensions are positive
        for dim in ['length', 'width', 'height']:
            if parameters.get(dim, 0) <= 0:
                result.add_error(dim, f'{dim} must be positive')
        
        # Check divisions are positive integers
        for div in ['x_division', 'y_division', 'z_division']:
            if parameters.get(div, 0) <= 0:
                result.add_error(div, f'{div} must be positive')
```

**Material Compatibility Rule**:
```python
class MaterialCompatibilityRule(ValidationRule):
    def validate(self, parameters: Dict[str, Any], result: ValidationResult):
        interface_type = parameters.get('interface_type', '')
        material = parameters.get('material', '')
        
        # Define material compatibility
        compatible_materials = {
            'carbon': ['carbon', 'silicon'],
            'halfcell': ['carbon', 'silicon', 'LFP', 'NCA'],
            'fullcell': ['carbon', 'silicon', 'LFP', 'NCA', 'LionSimba']
        }
        
        if interface_type in compatible_materials:
            if material not in compatible_materials[interface_type]:
                result.add_error('material', 
                    f'Material {material} not compatible with {interface_type}')
```

## 🧪 Testing Strategy

### Unit Test Structure
```python
class TestParameterValidator(unittest.TestCase):
    def setUp(self):
        self.validator = CarbonValidator()
    
    def test_valid_parameters(self):
        # Test with valid parameters
        params = {'length': 100.0, 'width': 100.0, 'height': 100.0}
        result = self.validator.validate(params)
        self.assertTrue(result.is_valid)
    
    def test_invalid_geometry(self):
        # Test with invalid geometry
        params = {'length': -10.0, 'width': 0.0, 'height': 100.0}
        result = self.validator.validate(params)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)
```

### Integration Test Structure
```python
class TestValidationIntegration(unittest.TestCase):
    def setUp(self):
        self.interface = CarbonInterface()
    
    def test_real_time_validation(self):
        # Test real-time validation on parameter changes
        self.interface.length_edit.setText('-10')
        # Check that validation error is displayed
        self.assertTrue(self.interface.has_validation_errors())
```

## 📊 Success Criteria

### Functional Requirements
- [ ] All parameter types are validated correctly
- [ ] All parameter ranges are validated correctly  
- [ ] All parameter dependencies are validated correctly
- [ ] Error messages are user-friendly and actionable
- [ ] Validation is performed in real-time
- [ ] UI state reflects validation results

### Performance Requirements
- [ ] Validation response time < 100ms
- [ ] Memory usage < 10MB for validation system
- [ ] No memory leaks in long-running operations
- [ ] CPU usage < 5% during validation

### Quality Requirements
- [ ] Unit test coverage > 95%
- [ ] Integration test coverage > 90%
- [ ] All error scenarios are handled gracefully
- [ ] Code follows PEP 8 style guidelines

## 🚨 Common Issues & Solutions

### Issue 1: Circular Import Problems
**Symptom**: ImportError when importing validators
**Solution**: Use lazy imports and TYPE_CHECKING

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.utils.parameter_validator import ParameterValidator
```

### Issue 2: Slow Validation Response
**Symptom**: UI freezes during validation
**Solution**: Implement validation debouncing and caching

```python
class BaseInterface:
    def __init__(self):
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._perform_validation)
    
    def _on_parameter_changed(self):
        self._validation_timer.start(200)  # 200ms debounce
```

### Issue 3: Memory Leaks in Validation
**Symptom**: Memory usage increases over time
**Solution**: Clear validation results and use weak references

```python
def _perform_validation(self):
    # Clear previous results
    self.validation_results.clear()
    # Perform validation
    result = self.validator.validate(self.get_parameters())
    # Store results (use weak references if needed)
```

## 🔄 Next Steps

After completing Phase 1:

1. **Review and Test**: Thoroughly test the validation system
2. **Performance Tuning**: Optimize validation performance if needed
3. **Documentation**: Update documentation with validation rules
4. **Phase 2 Preparation**: Prepare for HalfCell interface enhancement

## 📞 Support

### Escalation Path
1. **Level 1**: Implementation issues → Review this guide
2. **Level 2**: Technical blockers → Check architecture documentation
3. **Level 3**: Critical blockers → Request mode switch to specialized agent

### Resources
- [Architecture Documentation](ARCHITECTURE.md)
- [Battery Simulator README](README.md)
- [OpenFOAM Integration Guide](docs/OPENFOAM_INTEGRATION.md)

---

**🎯 Phase 1 Complete**: Unified parameter validation and error messaging system ready for Phase 2 integration!